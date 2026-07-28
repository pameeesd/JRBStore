from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from storeApp.models import Producto, Categoria, Venta
from storeApp.forms import ProductoForm, CategoriaForm, RegistroForm

def index(request):
    productos = Producto.objects.all()[:6]
    categorias = Categoria.objects.all()
    return render(request, 'index.html', {'productos': productos, 'categorias': categorias})

def Admin(request):
    total_productos = Producto.objects.count()
    total_categorias = Categoria.objects.count()
    total_ventas = Venta.objects.count()
    return render(request, 'Admin.html', {
        'total_productos': total_productos,
        'total_categorias': total_categorias,
        'total_ventas': total_ventas
    })

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

def listarProducto(request):
    productos = Producto.objects.all()
    return render(request, 'storeApp/prductosAd.html', {'lista': productos})

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

def eliminarProducto(request, codigo):
    prod = get_object_or_404(Producto, pk=codigo)
    if prod.foto:
        prod.foto.delete()
    prod.delete()
    messages.success(request, 'Producto eliminado con exito!')
    return redirect('listaproducto')

def crearCategoria(request):
    form = CategoriaForm()
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria creada con exito!')
            return redirect('listacategoria')
    return render(request, 'categoria/create2.html', {'titulo': 'Crear Categoria', 'formulario': form})

def listarCategoria(request):
    categorias = Categoria.objects.all()
    return render(request, 'categoria/categoria.html', {'lista': categorias})

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

def eliminarCategoria(request, codigo):
    cat = get_object_or_404(Categoria, pk=codigo)
    cat.delete()
    messages.success(request, 'Categoria eliminada con exito!')
    return redirect('listacategoria')

def Registrarse(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}! Tu cuenta ha sido registrada con exito.')
            return redirect('index')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
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

def productosAD(request):
    productos = Producto.objects.all()
    return render(request, 'storeApp/prductosAd.html', {'productos': productos}) 

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

def procesar_pago(request):
    if request.method == 'POST':
        carrito = request.session.get('carrito', [])
        usuario = request.user

        if not usuario.is_authenticated:
            messages.error(request, "Debes iniciar sesion para realizar la compra.")
            return redirect('login')

        if not carrito:
            messages.error(request, "El carrito esta vacio.")
            return redirect('carrito')

        for item in carrito:
            cantidad = int(request.POST.get(f'cantidad_{item["codigoBarra"]}', item['cantidad']))
            total = cantidad * float(item['precio'])

            try:
                prod = Producto.objects.get(codigoBarra=item['codigoBarra'])
                if prod.stock >= cantidad:
                    prod.stock -= cantidad
                    prod.save()

                Venta.objects.create(
                    usuario=usuario,
                    producto=prod,
                    cantidad=cantidad,
                    precio_total=total
                )
            except Exception as e:
                print(f"Error procesando producto {item['codigoBarra']}: {e}")

        request.session['carrito'] = []
        messages.success(request, "¡Pago realizado con exito! Tu pedido ha sido procesado.")
        return redirect('ventas')

    return redirect('carrito')

def ventas(request):
    if not request.user.is_authenticated:
        messages.error(request, "Debes iniciar sesion para ver tus compras.")
        return redirect('login')

    if request.user.is_superuser or request.user.is_staff:
        ventas_list = Venta.objects.all().order_by('-fecha')
    else:
        ventas_list = Venta.objects.filter(usuario=request.user).order_by('-fecha')

    total_ventas = sum(v.precio_total for v in ventas_list)
    return render(request, 'storeApp/ventas.html', {'ventas': ventas_list, 'total_ventas': total_ventas})
