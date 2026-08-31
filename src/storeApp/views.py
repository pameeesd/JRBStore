import logging
import uuid
from decimal import Decimal

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from storeApp.forms import CategoriaForm, ProductoForm, RegistroForm
from storeApp.models import Categoria, Pedido, PedidoItem, Producto, Venta

logger = logging.getLogger(__name__)


def format_clp(amount):
    """Format integer/decimal as CLP currency: 50000 -> $50.000"""
    try:
        val = int(amount)
        return f"${val:,}".replace(',', '.')
    except (ValueError, TypeError):
        return f"${amount}"


def _get_session_cart(request):
    """Returns normalized dictionary cart: {str(codigoBarra): int(cantidad)}"""
    cart = request.session.get('carrito', {})
    if isinstance(cart, list):
        new_cart = {}
        for item in cart:
            if isinstance(item, dict) and 'codigoBarra' in item:
                code = str(item['codigoBarra'])
                new_cart[code] = new_cart.get(code, 0) + int(item.get('cantidad', 1))
        cart = new_cart
        request.session['carrito'] = cart
    elif not isinstance(cart, dict):
        cart = {}
        request.session['carrito'] = cart
    return cart


def _get_cart_details(request):
    """Queries DB for current cart items, calculates backend totals using Decimal."""
    cart_dict = _get_session_cart(request)
    items = []
    total = Decimal(0)

    if cart_dict:
        codes = list(cart_dict.keys())
        productos_qs = Producto.objects.filter(codigoBarra__in=codes).select_related('categoria')
        prod_map = {str(p.codigoBarra): p for p in productos_qs}

        valid_cart = {}
        for code, cantidad in cart_dict.items():
            if code in prod_map and cantidad > 0:
                prod = prod_map[code]
                qty = min(cantidad, prod.stock) if prod.stock > 0 else 0
                if qty > 0:
                    valid_cart[code] = qty
                    subtotal = Decimal(str(prod.precio)) * qty
                    total += subtotal
                    items.append({
                        'codigoBarra': prod.codigoBarra,
                        'nombre': prod.nombre,
                        'categoria': prod.categoria,
                        'precio': prod.precio,
                        'precio_clp': format_clp(prod.precio),
                        'stock': prod.stock,
                        'cantidad': qty,
                        'subtotal': subtotal,
                        'subtotal_clp': format_clp(subtotal),
                        'foto': prod.foto,
                    })

        if valid_cart != cart_dict:
            request.session['carrito'] = valid_cart

    return items, total, format_clp(total)


def index(request):
    productos = Producto.objects.all()[:6]
    categorias = Categoria.objects.values_list('categoria', flat=True).distinct()
    return render(request, 'index.html', {'productos': productos, 'categorias': categorias})


@staff_member_required(login_url='login')
def Admin(request):
    total_productos = Producto.objects.count()
    total_categorias = Categoria.objects.count()
    total_ventas = Pedido.objects.filter(estado='PAGADO').count()
    return render(request, 'Admin.html', {
        'total_productos': total_productos,
        'total_categorias': total_categorias,
        'total_ventas': total_ventas
    })


@staff_member_required(login_url='login')
def crearProducto(request):
    form = ProductoForm()
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado con éxito!')
            return redirect('listaproducto')
        else:
            messages.error(request, 'Error en el formulario.')
    return render(request, 'storeApp/create.html', {'titulo': 'Crear Producto', 'formulario': form})


@staff_member_required(login_url='login')
def listarProducto(request):
    productos = Producto.objects.all().select_related('categoria')
    return render(request, 'storeApp/productosad.html', {'lista': productos})


@staff_member_required(login_url='login')
def editarProducto(request, codigo):
    prod = get_object_or_404(Producto, pk=codigo)
    form = ProductoForm(instance=prod)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=prod)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto editado con éxito!')
            return redirect('listaproducto')
    return render(request, 'storeApp/create.html', {
        'titulo': 'Editar Producto',
        'formulario': form,
        'foto_actual': prod.foto.url if prod.foto else None
    })


@staff_member_required(login_url='login')
@require_POST
def eliminarProducto(request, codigo):
    prod = get_object_or_404(Producto, pk=codigo)
    try:
        if prod.foto:
            prod.foto.delete(save=False)
        prod.delete()
        messages.success(request, 'Producto eliminado con éxito!')
    except ProtectedError:
        messages.error(request, 'No se puede eliminar el producto porque está asociado a pedidos.')
    except Exception:
        logger.exception("Error al eliminar producto")
        messages.error(request, 'Ocurrió un error al eliminar el producto.')
    return redirect('listaproducto')


@staff_member_required(login_url='login')
def crearCategoria(request):
    form = CategoriaForm()
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada con éxito!')
            return redirect('listacategoria')
    return render(request, 'categoria/create2.html', {'titulo': 'Crear Categoría', 'formulario': form})


@staff_member_required(login_url='login')
def listarCategoria(request):
    categorias = Categoria.objects.all().order_by('categoria', 'subcategoria')
    return render(request, 'categoria/categoria.html', {'lista': categorias})


@staff_member_required(login_url='login')
def editarCategoria(request, codigo):
    cat = get_object_or_404(Categoria, pk=codigo)
    form = CategoriaForm(instance=cat)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, 'La categoría ha sido modificada con éxito!')
            return redirect('listacategoria')
    return render(request, 'categoria/create2.html', {'titulo': 'Editar Categoría', 'formulario': form})


@staff_member_required(login_url='login')
@require_POST
def eliminarCategoria(request, codigo):
    cat = get_object_or_404(Categoria, pk=codigo)
    try:
        cat.delete()
        messages.success(request, 'Categoría eliminada con éxito!')
    except ProtectedError:
        messages.error(request, 'No se puede eliminar la categoría porque existen productos asociados.')
    except Exception:
        logger.exception("Error al eliminar categoría")
        messages.error(request, 'Ocurrió un error al eliminar la categoría.')
    return redirect('listacategoria')


def Registrarse(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        try:
            if form.is_valid():
                user = form.save()
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                messages.success(request, f'¡Bienvenido {user.username}! Tu cuenta ha sido registrada con éxito.')
                return redirect('index')
            else:
                return render(request, 'Usuario/registro.html', {'formulario': form, 'titulo': 'Registro'}, status=200)
        except IntegrityError:
            form.add_error(None, "Este nombre de usuario o correo electrónico ya está registrado.")
            return render(request, 'Usuario/registro.html', {'formulario': form, 'titulo': 'Registro'}, status=200)
        except Exception:
            logger.exception("Unexpected error during user registration process")
            form.add_error(None, "No pudimos completar el registro. Inténtalo nuevamente.")
            return render(request, 'Usuario/registro.html', {'formulario': form, 'titulo': 'Registro'}, status=200)
    else:
        form = RegistroForm()
    return render(request, 'Usuario/registro.html', {'formulario': form, 'titulo': 'Registro'})


def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"¡Bienvenido {username}!")
                if user.is_staff or user.is_superuser:
                    return redirect('Admin')
                return redirect('index')
            else:
                messages.error(request, "Usuario o contraseña incorrectos.")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
    else:
        form = AuthenticationForm()
    return render(request, 'Usuario/login.html', {'form': form})


def logout_user(request):
    logout(request)
    messages.success(request, "Has cerrado sesión con éxito.")
    return redirect('index')


def productos(request):
    query = request.GET.get('q', '').strip()
    cat_name = request.GET.get('categoria', '').strip()
    subcat_name = request.GET.get('subcategoria', '').strip()

    lista_productos = Producto.objects.all().select_related('categoria')

    if query:
        lista_productos = lista_productos.filter(nombre__icontains=query)

    if cat_name:
        lista_productos = lista_productos.filter(categoria__categoria__iexact=cat_name)

    if subcat_name:
        lista_productos = lista_productos.filter(categoria__subcategoria__iexact=subcat_name)

    categorias_unicas = Categoria.objects.values_list('categoria', flat=True).distinct()

    return render(request, 'storeApp/productos.html', {
        'productos': lista_productos,
        'categorias': categorias_unicas,
        'search_query': query,
        'selected_cat': cat_name,
        'selected_subcat': subcat_name
    })


@staff_member_required(login_url='login')
def productosAD(request):
    productos = Producto.objects.all().select_related('categoria')
    return render(request, 'storeApp/productosad.html', {'productos': productos})


def inicioSesion(request):
    return render(request, 'Usuario/login.html')


def agregar_al_carrito(request, codigo):
    producto = get_object_or_404(Producto, pk=codigo)
    if producto.stock <= 0:
        messages.error(request, f"El producto {producto.nombre} no tiene stock disponible.")
        return redirect('productos')

    cart = _get_session_cart(request)
    code_str = str(producto.codigoBarra)
    cant_actual = cart.get(code_str, 0)

    if cant_actual + 1 > producto.stock:
        messages.error(request, f"No puedes agregar más unidades de {producto.nombre}. Stock disponible: {producto.stock}.")
    else:
        cart[code_str] = cant_actual + 1
        request.session['carrito'] = cart
        request.session.modified = True
        messages.success(request, f"¡{producto.nombre} agregado al carrito!")

    return redirect('carrito')


@require_POST
def incrementar_cantidad(request, codigo):
    producto = get_object_or_404(Producto, pk=codigo)
    cart = _get_session_cart(request)
    code_str = str(producto.codigoBarra)
    cant_actual = cart.get(code_str, 0)

    if cant_actual + 1 > producto.stock:
        messages.error(request, f"Stock insuficiente para {producto.nombre}. Disponible: {producto.stock}.")
    else:
        cart[code_str] = cant_actual + 1
        request.session['carrito'] = cart
        request.session.modified = True

    return redirect('carrito')


@require_POST
def decrementar_cantidad(request, codigo):
    cart = _get_session_cart(request)
    code_str = str(codigo)
    if code_str in cart:
        if cart[code_str] > 1:
            cart[code_str] -= 1
        else:
            del cart[code_str]
        request.session['carrito'] = cart
        request.session.modified = True
    return redirect('carrito')


@require_POST
def eliminar_producto_carrito(request, codigo):
    cart = _get_session_cart(request)
    code_str = str(codigo)
    if code_str in cart:
        del cart[code_str]
        request.session['carrito'] = cart
        request.session.modified = True
        messages.info(request, "Producto eliminado del carrito.")
    return redirect('carrito')


@require_POST
def vaciar_carrito(request):
    request.session['carrito'] = {}
    request.session.modified = True
    messages.info(request, "Carrito vaciado.")
    return redirect('carrito')


def carrito(request):
    items, total, total_clp = _get_cart_details(request)
    return render(request, 'storeApp/carrito.html', {
        'items': items,
        'total': total,
        'total_clp': total_clp
    })


def checkout(request):
    items, total, total_clp = _get_cart_details(request)
    if not items:
        messages.error(request, "Tu carrito está vacío.")
        return redirect('carrito')

    stock_issue = False
    for item in items:
        if item['cantidad'] > item['stock']:
            stock_issue = True
            messages.error(request, f"El stock de {item['nombre']} ha cambiado. Stock disponible: {item['stock']}.")

    if stock_issue:
        return redirect('carrito')

    return render(request, 'storeApp/checkout.html', {
        'items': items,
        'total': total,
        'total_clp': total_clp
    })


def pago(request):
    items, total, total_clp = _get_cart_details(request)
    if not items:
        messages.error(request, "Tu carrito está vacío.")
        return redirect('carrito')

    return render(request, 'storeApp/pago.html', {
        'items': items,
        'total': total,
        'total_clp': total_clp
    })


@require_POST
def procesar_pago(request):
    items, total, total_clp = _get_cart_details(request)
    if not items:
        messages.error(request, "El carrito está vacío.")
        return redirect('carrito')

    numero_tarjeta = request.POST.get('numero_tarjeta', '').replace(' ', '').strip()

    # MOCK PAYMENT GATEWAY CHECK
    # Rejected test card: 4000 0000 0000 0002
    if numero_tarjeta == '4000000000000002':
        messages.error(request, "El pago fue rechazado. Tu carrito se mantiene intacto.")
        return render(request, 'storeApp/pago.html', {
            'items': items,
            'total': total,
            'total_clp': total_clp,
            'error_pago': 'El pago fue rechazado por el banco emisor. Tu carrito se mantiene intacto.'
        }, status=200)

    # TRANSACTIONAL ORDER CREATION & STOCK DEDUCTION
    try:
        with transaction.atomic():
            codes = [str(item['codigoBarra']) for item in items]
            productos_db = Producto.objects.select_for_update().filter(codigoBarra__in=codes)
            prod_map = {str(p.codigoBarra): p for p in productos_db}

            for item in items:
                code_str = str(item['codigoBarra'])
                if code_str not in prod_map:
                    raise ValueError(f"El producto {item['nombre']} ya no está disponible.")
                prod = prod_map[code_str]
                if prod.stock < item['cantidad']:
                    raise ValueError(f"Stock insuficiente para {prod.nombre}. Disponible: {prod.stock}.")

            num_pedido = f"JRB-{uuid.uuid4().hex[:8].upper()}"

            pedido_total = Decimal(0)
            pedido_items_data = []

            for item in items:
                prod = prod_map[str(item['codigoBarra'])]
                subtotal = Decimal(str(prod.precio)) * item['cantidad']
                pedido_total += subtotal
                pedido_items_data.append((prod, item['cantidad'], subtotal))

            pedido = Pedido.objects.create(
                numero_pedido=num_pedido,
                usuario=request.user if request.user.is_authenticated else None,
                total=pedido_total,
                estado='PAGADO'
            )

            for prod, cantidad, subtotal in pedido_items_data:
                PedidoItem.objects.create(
                    pedido=pedido,
                    producto=prod,
                    codigo_barra_historico=prod.codigoBarra,
                    nombre_producto_historico=prod.nombre,
                    precio_unitario_historico=prod.precio,
                    cantidad=cantidad,
                    subtotal=subtotal
                )
                prod.stock -= cantidad
                prod.save()

                if request.user.is_authenticated:
                    Venta.objects.create(
                        usuario=request.user,
                        producto=prod,
                        cantidad=cantidad,
                        precio_total=subtotal
                    )

        request.session['carrito'] = {}
        request.session.modified = True
        return redirect('confirmacion', numero_pedido=pedido.numero_pedido)

    except ValueError as e:
        messages.error(request, str(e))
        return redirect('carrito')
    except Exception:
        logger.exception("Error al procesar el pago transaccional")
        messages.error(request, "Ocurrió un error inesperado al procesar la compra. Inténtalo nuevamente.")
        return redirect('carrito')


def confirmacion(request, numero_pedido):
    pedido = get_object_or_404(Pedido, numero_pedido=numero_pedido)
    items = pedido.items.all()
    return render(request, 'storeApp/confirmacion.html', {
        'pedido': pedido,
        'items': items,
        'total_clp': format_clp(pedido.total)
    })


@login_required(login_url='login')
def ventas(request):
    mis_pedidos = Pedido.objects.filter(usuario=request.user).prefetch_related('items').order_by('-fecha_creacion')
    total_mis_compras = mis_pedidos.aggregate(total=Sum('total'))['total'] or 0

    todos_los_pedidos = []
    total_general_ventas = 0

    if request.user.is_superuser or request.user.is_staff:
        todos_los_pedidos = Pedido.objects.all().prefetch_related('items').order_by('-fecha_creacion')
        total_general_ventas = todos_los_pedidos.aggregate(total=Sum('total'))['total'] or 0

    return render(request, 'storeApp/ventas.html', {
        'mis_compras': mis_pedidos,
        'total_mis_compras': format_clp(total_mis_compras),
        'todas_las_ventas': todos_los_pedidos,
        'total_general_ventas': format_clp(total_general_ventas),
        'es_admin': request.user.is_superuser or request.user.is_staff
    })


@login_required(login_url='login')
def trigger_seed_catalog(request):
    from django.core.management import call_command
    call_command('seed_catalog')
    messages.success(request, "¡Catálogo inicial inyectado con éxito!")
    return redirect('listaproducto')

