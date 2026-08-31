from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from storeApp.forms import CategoriaForm, ProductoForm, RegistroForm
from storeApp.models import Categoria, Producto, Venta


def index(request):
    productos = Producto.objects.all()[:6]
    categorias = Categoria.objects.all()
    return render(request, 'index.html', {'productos': productos, 'categorias': categorias})

@staff_member_required(login_url='login')
def Admin(request):
    total_productos = Producto.objects.count()
    total_categorias = Categoria.objects.count()
    total_ventas = Venta.objects.count()
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
            messages.success(request, 'Producto creado con exito!')
            return redirect('listaproducto')
        else:
            messages.error(request, 'Error en el formulario.')
    return render(request, 'storeApp/create.html', {'titulo': 'Crear Producto', 'formulario': form})

@staff_member_required(login_url='login')
def listarProducto(request):
    productos = Producto.objects.all()
    return render(request, 'storeApp/productosad.html', {'lista': productos})

@staff_member_required(login_url='login')
def editarProducto(request, codigo):
    prod = get_object_or_404(Producto, pk=codigo)
    form = ProductoForm(instance=prod)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=prod)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto editado con exito!')
            return redirect('listaproducto')
    return render(request, 'storeApp/create.html', {
        'titulo': 'Editar Producto',
        'formulario': form,
        'foto_actual': prod.foto.url if prod.foto else None
    })

@staff_member_required(login_url='login')
def eliminarProducto(request, codigo):
    prod = get_object_or_404(Producto, pk=codigo)
    if prod.foto:
        prod.foto.delete()
    prod.delete()
    messages.success(request, 'Producto eliminado con exito!')
    return redirect('listaproducto')

@staff_member_required(login_url='login')
def crearCategoria(request):
    form = CategoriaForm()
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria creada con exito!')
            return redirect('listacategoria')
    return render(request, 'categoria/create2.html', {'titulo': 'Crear Categoria', 'formulario': form})

@staff_member_required(login_url='login')
def listarCategoria(request):
    categorias = Categoria.objects.all()
    return render(request, 'categoria/categoria.html', {'lista': categorias})

@staff_member_required(login_url='login')
def editarCategoria(request, codigo):
    cat = get_object_or_404(Categoria, pk=codigo)
    form = CategoriaForm(instance=cat)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, 'La Categoria ha sido modificada con exito!')
            return redirect('listacategoria')
    return render(request, 'categoria/create2.html', {'titulo': 'Editar Categoria', 'formulario': form})

@staff_member_required(login_url='login')
def eliminarCategoria(request, codigo):
    cat = get_object_or_404(Categoria, pk=codigo)
    cat.delete()
    messages.success(request, 'Categoria eliminada con exito!')
    return redirect('listacategoria')

import logging

from django.db import IntegrityError

logger = logging.getLogger(__name__)


def Registrarse(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        try:
            if form.is_valid():
                user = form.save()
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
    messages.success(request, "Has cerrado sesion con exito.")
    return redirect('index')

def productos(request):
    query = request.GET.get('q', '').strip()
    cat_id = request.GET.get('categoria', '').strip()

    lista_productos = Producto.objects.all()

    if query:
        lista_productos = lista_productos.filter(nombre__icontains=query)

    if cat_id and cat_id.isdigit():
        lista_productos = lista_productos.filter(categoria_id=int(cat_id))

    categorias = Categoria.objects.all()

    return render(request, 'storeApp/productos.html', {
        'productos': lista_productos,
        'categorias': categorias,
        'search_query': query,
        'selected_cat': int(cat_id) if cat_id.isdigit() else ''
    })

@staff_member_required(login_url='login')
def productosAD(request):
    productos = Producto.objects.all()
    return render(request, 'storeApp/productosad.html', {'productos': productos}) 

def inicioSesion(request):
    return render(request, 'Usuario/login.html') 

def agregar_al_carrito(request, codigo):
    producto = get_object_or_404(Producto, pk=codigo)
    carrito = request.session.get('carrito', [])

    encontrado = False
    for item in carrito:
        if str(item['codigoBarra']) == str(producto.codigoBarra):
            item['cantidad'] += 1
            item['total'] = item['cantidad'] * float(item['precio'])
            encontrado = True
            break

    if not encontrado:
        carrito.append({
            'codigoBarra': producto.codigoBarra,
            'nombre': producto.nombre,
            'precio': float(producto.precio),
            'cantidad': 1,
            'total': float(producto.precio)
        })

    request.session['carrito'] = carrito
    messages.success(request, f"¡{producto.nombre} agregado al carrito!")
    return redirect('productos')

def carrito(request):
    carrito = request.session.get('carrito', [])

    if not isinstance(carrito, list):
        carrito = []
        request.session['carrito'] = carrito

    total = sum(item['total'] for item in carrito)
    return render(request, 'storeApp/carrito.html', {'carrito': carrito, 'total': total})

def eliminar_producto_carrito(request, codigo):
    carrito = request.session.get('carrito', [])
    carrito = [item for item in carrito if str(item['codigoBarra']) != str(codigo)]
    request.session['carrito'] = carrito
    messages.info(request, "Producto eliminado del carrito.")
    return redirect('carrito')

@login_required(login_url='login')
def procesar_pago(request):
    if request.method == 'POST':
        carrito = request.session.get('carrito', [])
        usuario = request.user

        if not carrito:
            messages.error(request, "El carrito esta vacio.")
            return redirect('carrito')

        try:
            with transaction.atomic():
                items_to_process = []
                for item in carrito:
                    codigo = item.get('codigoBarra')
                    try:
                        cantidad = int(request.POST.get(f'cantidad_{codigo}', item.get('cantidad', 1)))
                    except (ValueError, TypeError):
                        messages.error(request, f"Cantidad invalida para el producto {item.get('nombre', '')}.")
                        return redirect('carrito')

                    if cantidad <= 0:
                        messages.error(request, "La cantidad comprada debe ser mayor a cero.")
                        return redirect('carrito')

                    try:
                        prod = Producto.objects.select_for_update().get(codigoBarra=codigo)
                    except Producto.DoesNotExist:
                        messages.error(request, f"El producto {item.get('nombre', '')} ya no esta disponible.")
                        return redirect('carrito')

                    if prod.stock < cantidad:
                        messages.error(request, f"Stock insuficiente para {prod.nombre}. Stock disponible: {prod.stock}.")
                        return redirect('carrito')

                    precio_unitario = float(prod.precio)
                    total_item = cantidad * precio_unitario
                    items_to_process.append((prod, cantidad, total_item))

                for prod, cantidad, total_item in items_to_process:
                    prod.stock -= cantidad
                    prod.save()

                    Venta.objects.create(
                        usuario=usuario,
                        producto=prod,
                        cantidad=cantidad,
                        precio_total=total_item
                    )

            request.session['carrito'] = []
            messages.success(request, "¡Pago realizado con exito! Tu pedido ha sido procesado.")
            return redirect('ventas')

        except Exception:
            messages.error(request, "Ocurrio un error al procesar la compra. Intentalo nuevamente.")
            return redirect('carrito')

    return redirect('carrito')

@login_required(login_url='login')
def ventas(request):
    mis_compras = Venta.objects.filter(usuario=request.user).select_related('producto', 'usuario').order_by('-fecha')
    total_mis_compras = mis_compras.aggregate(total=Sum('precio_total'))['total'] or 0

    todas_las_ventas = []
    total_general_ventas = 0

    if request.user.is_superuser or request.user.is_staff:
        todas_las_ventas = Venta.objects.all().select_related('producto', 'usuario').order_by('-fecha')
        total_general_ventas = todas_las_ventas.aggregate(total=Sum('precio_total'))['total'] or 0

    return render(request, 'storeApp/ventas.html', {
        'mis_compras': mis_compras,
        'total_mis_compras': total_mis_compras,
        'todas_las_ventas': todas_las_ventas,
        'total_general_ventas': total_general_ventas,
        'es_admin': request.user.is_superuser or request.user.is_staff
    })
