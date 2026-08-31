import io
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image

from storeApp.models import Categoria, Pedido, Producto


def create_dummy_image(filename="test.jpg", format_type="JPEG"):
    file_obj = io.BytesIO()
    image = Image.new("RGB", (100, 100), color="red")
    image.save(file_obj, format=format_type)
    file_obj.seek(0)
    return SimpleUploadedFile(filename, file_obj.read(), content_type=f"image/{format_type.lower()}")


class EcommerceComprehensiveTestSuite(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Staff Admin User
        self.staff_user = User.objects.create_user(
            username='staffadmin',
            email='staff@example.com',
            password='Password123!',
            is_staff=True,
            is_superuser=True
        )

        
        # Regular Customer User
        self.normal_user = User.objects.create_user(
            username='customer1',
            email='customer@example.com',
            password='Password123!'
        )

        # Seed initial Category
        self.cat1, _ = Categoria.objects.get_or_create(
            categoria='Consolas',
            subcategoria='PlayStation 5',
            defaults={'codigo': '100000000001'}
        )


        # Seed initial Product
        self.img_file = create_dummy_image()
        self.prod1, _ = Producto.objects.get_or_create(
            codigoBarra='123456789012',
            defaults={
                'nombre': 'PlayStation 5 Console',
                'categoria': self.cat1,
                'precio': Decimal(500000),
                'stock': 10,
                'descripcion': 'Consola de videojuegos PS5',
                'foto': self.img_file
            }
        )


    # =========================================================================
    # CATEGORÍAS (1 - 11)
    # =========================================================================
    def test_01_crear_categoria_valida(self):
        self.client.login(username='staffadmin', password='Password123!')
        response = self.client.post(reverse('crearcategoria'), {
            'codigo': '200000000001',
            'categoria': 'Nintendo',
            'subcategoria': 'Switch 2'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Categoria.objects.filter(codigo='200000000001').exists())

    def test_02_codigo_categoria_invalido(self):
        self.client.login(username='staffadmin', password='Password123!')
        response = self.client.post(reverse('crearcategoria'), {
            'codigo': '123',  # Menos de 12 dígitos
            'categoria': 'Xbox',
            'subcategoria': 'Series X'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Categoria.objects.filter(categoria='Xbox').exists())

    def test_03_codigo_categoria_duplicado(self):
        self.client.login(username='staffadmin', password='Password123!')
        response = self.client.post(reverse('crearcategoria'), {
            'codigo': '100000000001',  # Ya existe en setUp
            'categoria': 'Accesorios',
            'subcategoria': 'Teclados'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Este código de categoría ya está registrado.', str(response.content))

    def test_04_categoria_vacia(self):
        self.client.login(username='staffadmin', password='Password123!')
        response = self.client.post(reverse('crearcategoria'), {
            'codigo': '300000000001',
            'categoria': '',
            'subcategoria': 'Switch 2'
        })
        self.assertEqual(response.status_code, 200)

    def test_05_categoria_larga_mayor_20(self):
        self.client.login(username='staffadmin', password='Password123!')
        response = self.client.post(reverse('crearcategoria'), {
            'codigo': '400000000001',
            'categoria': 'A' * 21,
            'subcategoria': 'Subcat'
        })
        self.assertEqual(response.status_code, 200)

    def test_06_subcategoria_vacia(self):
        self.client.login(username='staffadmin', password='Password123!')
        response = self.client.post(reverse('crearcategoria'), {
            'codigo': '500000000001',
            'categoria': 'Nintendo',
            'subcategoria': ''
        })
        self.assertEqual(response.status_code, 200)

    def test_07_subcategoria_larga_mayor_20(self):
        self.client.login(username='staffadmin', password='Password123!')
        response = self.client.post(reverse('crearcategoria'), {
            'codigo': '600000000001',
            'categoria': 'Nintendo',
            'subcategoria': 'B' * 21
        })
        self.assertEqual(response.status_code, 200)

    def test_08_duplicacion_categoria_subcategoria(self):
        self.client.login(username='staffadmin', password='Password123!')
        response = self.client.post(reverse('crearcategoria'), {
            'codigo': '700000000001',
            'categoria': 'Consolas',
            'subcategoria': 'PlayStation 5'  # Ya existe la combinación
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('Ya existe esta combinación', response.content.decode('utf-8'))

    def test_09_editar_categoria(self):
        self.client.login(username='staffadmin', password='Password123!')
        response = self.client.post(reverse('editarcategoria', args=[self.cat1.codigo]), {
            'codigo': '100000000001',
            'categoria': 'Consolas',
            'subcategoria': 'PS5 Editada'
        })
        self.assertEqual(response.status_code, 302)
        self.cat1.refresh_from_db()
        self.assertEqual(self.cat1.subcategoria, 'PS5 Editada')

    def test_10_eliminar_categoria_post(self):
        self.client.login(username='staffadmin', password='Password123!')
        cat_temp = Categoria.objects.create(codigo='999999999999', categoria='Temp', subcategoria='Temp')
        response = self.client.post(reverse('eliminarcategoria', args=[cat_temp.codigo]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Categoria.objects.filter(codigo='999999999999').exists())

    def test_11_usuario_no_autorizado_categoria(self):
        self.client.login(username='customer1', password='Password123!')
        response = self.client.get(reverse('crearcategoria'))
        self.assertEqual(response.status_code, 302)  # Redirigido a login

    # =========================================================================
    # PRODUCTOS (12 - 23)
    # =========================================================================
    def test_12_crear_producto_valido(self):
        self.client.login(username='staffadmin', password='Password123!')
        img = create_dummy_image('newprod.jpg', 'JPEG')
        response = self.client.post(reverse('crearproducto'), {
            'codigoBarra': '987654321098',
            'nombre': 'Nintendo Switch OLED',
            'categoria': self.cat1.codigo,
            'precio': 350000,
            'stock': 15,
            'descripcion': 'Consola Nintendo Switch OLED blanca',
            'foto': img
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Producto.objects.filter(codigoBarra='987654321098').exists())

    def test_13_codigo_producto_invalido(self):
        self.client.login(username='staffadmin', password='Password123!')
        img = create_dummy_image()
        response = self.client.post(reverse('crearproducto'), {
            'codigoBarra': '123',  # Menos de 12 dígitos
            'nombre': 'Producto Test',
            'categoria': self.cat1.codigo,
            'precio': 10000,
            'stock': 5,
            'descripcion': 'Test',
            'foto': img
        })
        self.assertEqual(response.status_code, 200)

    def test_14_codigo_producto_duplicado(self):
        self.client.login(username='staffadmin', password='Password123!')
        img = create_dummy_image()
        response = self.client.post(reverse('crearproducto'), {
            'codigoBarra': '123456789012',  # Ya existe prod1
            'nombre': 'Otro Producto',
            'categoria': self.cat1.codigo,
            'precio': 10000,
            'stock': 5,
            'descripcion': 'Test',
            'foto': img
        })
        self.assertEqual(response.status_code, 200)

    def test_15_nombre_producto_largo_mayor_100(self):
        self.client.login(username='staffadmin', password='Password123!')
        img = create_dummy_image()
        response = self.client.post(reverse('crearproducto'), {
            'codigoBarra': '111122223333',
            'nombre': 'N' * 101,
            'categoria': self.cat1.codigo,
            'precio': 10000,
            'stock': 5,
            'descripcion': 'Test',
            'foto': img
        })
        self.assertEqual(response.status_code, 200)

    def test_16_precio_producto_invalido(self):
        self.client.login(username='staffadmin', password='Password123!')
        img = create_dummy_image()
        response = self.client.post(reverse('crearproducto'), {
            'codigoBarra': '111122223333',
            'nombre': 'Producto Gratis',
            'categoria': self.cat1.codigo,
            'precio': 0,  # Debe ser > 0
            'stock': 5,
            'descripcion': 'Test',
            'foto': img
        })
        self.assertEqual(response.status_code, 200)

    def test_17_stock_negativo(self):
        self.client.login(username='staffadmin', password='Password123!')
        img = create_dummy_image()
        response = self.client.post(reverse('crearproducto'), {
            'codigoBarra': '111122223333',
            'nombre': 'Producto Stock Negativo',
            'categoria': self.cat1.codigo,
            'precio': 10000,
            'stock': -5,
            'descripcion': 'Test',
            'foto': img
        })
        self.assertEqual(response.status_code, 200)

    def test_18_stock_mayor_100(self):
        self.client.login(username='staffadmin', password='Password123!')
        img = create_dummy_image()
        response = self.client.post(reverse('crearproducto'), {
            'codigoBarra': '111122223333',
            'nombre': 'Producto Exceso Stock',
            'categoria': self.cat1.codigo,
            'precio': 10000,
            'stock': 150,  # Max 100
            'descripcion': 'Test',
            'foto': img
        })
        self.assertEqual(response.status_code, 200)

    def test_19_descripcion_larga_mayor_500(self):
        self.client.login(username='staffadmin', password='Password123!')
        img = create_dummy_image()
        response = self.client.post(reverse('crearproducto'), {
            'codigoBarra': '111122223333',
            'nombre': 'Producto Desc Larga',
            'categoria': self.cat1.codigo,
            'precio': 10000,
            'stock': 10,
            'descripcion': 'D' * 501,
            'foto': img
        })
        self.assertEqual(response.status_code, 200)

    def test_20_foto_jpg_valida(self):
        self.client.login(username='staffadmin', password='Password123!')
        img = create_dummy_image('valid.jpg', 'JPEG')
        response = self.client.post(reverse('crearproducto'), {
            'codigoBarra': '888877776666',
            'nombre': 'Producto JPG',
            'categoria': self.cat1.codigo,
            'precio': 10000,
            'stock': 10,
            'descripcion': 'Valido JPG',
            'foto': img
        })
        self.assertEqual(response.status_code, 302)

    def test_21_foto_png_valida(self):
        self.client.login(username='staffadmin', password='Password123!')
        img = create_dummy_image('valid.png', 'PNG')
        response = self.client.post(reverse('crearproducto'), {
            'codigoBarra': '555544443333',
            'nombre': 'Producto PNG',
            'categoria': self.cat1.codigo,
            'precio': 15000,
            'stock': 10,
            'descripcion': 'Valido PNG',
            'foto': img
        })
        self.assertEqual(response.status_code, 302)

    def test_22_archivo_foto_invalido(self):
        self.client.login(username='staffadmin', password='Password123!')
        txt_file = SimpleUploadedFile("bad.txt", b"text content", content_type="text/plain")
        response = self.client.post(reverse('crearproducto'), {
            'codigoBarra': '444433332222',
            'nombre': 'Producto Bad File',
            'categoria': self.cat1.codigo,
            'precio': 10000,
            'stock': 10,
            'descripcion': 'Bad File',
            'foto': txt_file
        })
        self.assertEqual(response.status_code, 200)

    def test_23_usuario_no_autorizado_producto(self):
        self.client.login(username='customer1', password='Password123!')
        response = self.client.get(reverse('crearproducto'))
        self.assertEqual(response.status_code, 302)

    # =========================================================================
    # CARRITO (24 - 34)
    # =========================================================================
    def test_24_agregar_producto_al_carrito(self):
        response = self.client.get(reverse('agregar_al_carrito', args=[self.prod1.codigoBarra]))
        self.assertEqual(response.status_code, 302)
        cart = self.client.session['carrito']
        self.assertEqual(cart.get('123456789012'), 1)

    def test_25_agregar_mismo_producto_incrementa(self):
        self.client.get(reverse('agregar_al_carrito', args=[self.prod1.codigoBarra]))
        self.client.get(reverse('agregar_al_carrito', args=[self.prod1.codigoBarra]))
        cart = self.client.session['carrito']
        self.assertEqual(cart.get('123456789012'), 2)

    def test_26_incrementar_cantidad_post(self):
        self.client.get(reverse('agregar_al_carrito', args=[self.prod1.codigoBarra]))
        response = self.client.post(reverse('incrementar_cantidad', args=[self.prod1.codigoBarra]))
        self.assertEqual(response.status_code, 302)
        cart = self.client.session['carrito']
        self.assertEqual(cart.get('123456789012'), 2)

    def test_27_decrementar_cantidad_post(self):
        self.client.get(reverse('agregar_al_carrito', args=[self.prod1.codigoBarra]))
        self.client.get(reverse('agregar_al_carrito', args=[self.prod1.codigoBarra]))
        response = self.client.post(reverse('decrementar_cantidad', args=[self.prod1.codigoBarra]))
        self.assertEqual(response.status_code, 302)
        cart = self.client.session['carrito']
        self.assertEqual(cart.get('123456789012'), 1)

    def test_28_eliminar_producto_del_carrito(self):
        self.client.get(reverse('agregar_al_carrito', args=[self.prod1.codigoBarra]))
        response = self.client.post(reverse('eliminar_producto_carrito', args=[self.prod1.codigoBarra]))
        self.assertEqual(response.status_code, 302)
        cart = self.client.session['carrito']
        self.assertNotIn('123456789012', cart)

    def test_29_vaciar_carrito(self):
        self.client.get(reverse('agregar_al_carrito', args=[self.prod1.codigoBarra]))
        response = self.client.post(reverse('vaciar_carrito'))
        self.assertEqual(response.status_code, 302)
        cart = self.client.session['carrito']
        self.assertEqual(cart, {})

    def test_30_agregar_producto_inexistente_404(self):
        response = self.client.get(reverse('agregar_al_carrito', args=['000000000000']))
        self.assertEqual(response.status_code, 404)

    def test_31_producto_sin_stock(self):
        prod_zero = Producto.objects.create(
            codigoBarra='999000999000',
            nombre='Agotado',
            categoria=self.cat1,
            precio=1000,
            stock=0,
            descripcion='Sin stock',
            foto=self.img_file
        )
        response = self.client.get(reverse('agregar_al_carrito', args=[prod_zero.codigoBarra]))
        self.assertEqual(response.status_code, 302)
        cart = self.client.session.get('carrito', {})
        self.assertNotIn('999000999000', cart)

    def test_32_superar_stock_disponible(self):
        prod_low = Producto.objects.create(
            codigoBarra='111222333444',
            nombre='Low Stock',
            categoria=self.cat1,
            precio=1000,
            stock=1,
            descripcion='Poco stock',
            foto=self.img_file
        )
        self.client.get(reverse('agregar_al_carrito', args=[prod_low.codigoBarra]))
        self.client.post(reverse('incrementar_cantidad', args=[prod_low.codigoBarra]))
        cart = self.client.session['carrito']
        self.assertEqual(cart.get('111222333444'), 1)  # No incrementa a 2

    def test_33_total_correcto_backend(self):
        self.client.get(reverse('agregar_al_carrito', args=[self.prod1.codigoBarra]))
        response = self.client.get(reverse('carrito'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('$500.000', response.content.decode('utf-8'))

    def test_34_anti_tampering_precio_cliente(self):
        """Test explícito enviando precio=1 en POST; el backend debe ignorarlo."""
        self.client.get(reverse('agregar_al_carrito', args=[self.prod1.codigoBarra]))
        # Intentar manipular el checkout/pago enviando precio modificado
        response = self.client.post(reverse('procesar_pago'), {
            'numero_tarjeta': '4242424242424242',
            'precio': 1,
            'total': 1
        })
        self.assertEqual(response.status_code, 302)
        pedido = Pedido.objects.last()
        self.assertIsNotNone(pedido)
        self.assertEqual(pedido.total, Decimal(500000))  # Precio real devuelto desde BD

    # =========================================================================
    # CHECKOUT & PAGOS (35 - 50)
    # =========================================================================
    def test_35_checkout_carrito_vacio(self):
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302)

    def test_36_checkout_valido(self):
        self.client.get(reverse('agregar_al_carrito', args=[self.prod1.codigoBarra]))
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('PlayStation 5 Console', response.content.decode('utf-8'))

    def test_37_38_39_revalidacion_stock_checkout(self):
        self.client.get(reverse('agregar_al_carrito', args=[self.prod1.codigoBarra]))
        # Reducir stock a 0 antes del checkout
        self.prod1.stock = 0
        self.prod1.save()
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302)

    def test_42_43_44_45_pago_rechazado_mantiene_carrito_y_stock(self):
        self.client.get(reverse('agregar_al_carrito', args=[self.prod1.codigoBarra]))
        response = self.client.post(reverse('procesar_pago'), {
            'numero_tarjeta': '4000000000000002'  # Tarjeta Rechazada
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('El pago fue rechazado. Tu carrito se mantiene intacto.', response.content.decode('utf-8'))
        cart = self.client.session['carrito']
        self.assertIn('123456789012', cart)
        self.prod1.refresh_from_db()
        self.assertEqual(self.prod1.stock, 10)  # Stock no cambia

    def test_46_47_48_49_50_pago_aprobado_descuenta_stock_crea_pedido(self):
        self.client.login(username='customer1', password='Password123!')
        self.client.get(reverse('agregar_al_carrito', args=[self.prod1.codigoBarra]))
        response = self.client.post(reverse('procesar_pago'), {
            'numero_tarjeta': '4242424242424242'  # Tarjeta Aprobada
        })
        self.assertEqual(response.status_code, 302)
        
        pedido = Pedido.objects.last()
        self.assertIsNotNone(pedido)
        self.assertTrue(pedido.numero_pedido.startswith('JRB-'))
        self.assertEqual(pedido.estado, 'PAGADO')
        self.assertEqual(pedido.total, Decimal(500000))
        
        # Descuento de stock
        self.prod1.refresh_from_db()
        self.assertEqual(self.prod1.stock, 9)
        
        # Carrito vacío
        cart = self.client.session.get('carrito', {})
        self.assertEqual(cart, {})

    # =========================================================================
    # SEGURIDAD & CSRF (51 - 55)
    # =========================================================================
    def test_51_visitante_no_accede_crud_admin(self):
        response = self.client.get(reverse('Admin'))
        self.assertEqual(response.status_code, 302)

    def test_52_usuario_normal_no_accede_crud_admin(self):
        self.client.login(username='customer1', password='Password123!')
        response = self.client.get(reverse('Admin'))
        self.assertEqual(response.status_code, 302)

    def test_53_staff_si_accede_crud_admin(self):
        self.client.login(username='staffadmin', password='Password123!')
        response = self.client.get(reverse('Admin'))
        self.assertEqual(response.status_code, 200)

    def test_55_eliminacion_no_funciona_mediante_get(self):
        self.client.login(username='staffadmin', password='Password123!')
        cat_temp = Categoria.objects.create(codigo='888999888999', categoria='GetTest', subcategoria='GetTest')
        response = self.client.get(reverse('eliminarcategoria', args=[cat_temp.codigo]))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
        self.assertTrue(Categoria.objects.filter(codigo='888999888999').exists())
