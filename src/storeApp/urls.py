# storeApp urls

from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('Admin/', views.Admin, name='Admin'),
    path('crearproducto/', views.crearProducto, name='crearproducto'),
    path('listaproducto/', views.listarProducto, name='listaproducto'),
    path('editarproducto/<str:codigo>', views.editarProducto, name='editarproducto'),
    path('eliminarproducto/<str:codigo>', views.eliminarProducto, name='eliminarproducto'),
    path('crearcategoria/', views.crearCategoria, name='crearcategoria'),
    path('listacategoria/', views.listarCategoria, name='listacategoria'),
    path('editarcategoria/<str:codigo>', views.editarCategoria, name='editarcategoria'),
    path('eliminarcategoria/<str:codigo>', views.eliminarCategoria, name='eliminarcategoria'),
    path('productos/', views.productos, name='productos'),
    path('productosad/', views.productosAD, name='productosad'),
    path('iniciosesion/', views.inicioSesion, name='iniciosesion'),
    path('carrito/', views.carrito, name='carrito'),
    path('registrarse/', views.Registrarse, name='registrarse'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('carrito/agregar/<str:codigo>', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<str:codigo>', views.eliminar_producto_carrito, name='eliminar_producto_carrito'),
    path('carrito/pagar/', views.procesar_pago, name='procesar_pago'),
    path('ventas/', views.ventas, name='ventas'),
    path('Ventas/', views.ventas, name='Ventas'),
]
