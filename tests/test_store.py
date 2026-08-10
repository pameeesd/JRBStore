from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from storeApp.models import Categoria, Producto, Venta


class StoreAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.cat = Categoria.objects.create(codigo="CAT1", categoria="Tecnologia")
        self.producto = Producto.objects.create(
            codigoBarra="1001",
            nombre="Notebook Gamer TX",
            precio=899990,
            stock=10,
            categoria=self.cat,
            descripcion="Laptop de alto rendimiento",
            foto="productos/sample.png"
        )
        self.user = User.objects.create_user(username="testuser", password="password123")

    def test_catalog_view(self):
        response = self.client.get(reverse('productos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Notebook Gamer TX")

    def test_search_filter(self):
        response = self.client.get(reverse('productos') + '?q=Notebook')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Notebook Gamer TX")

    def test_cart_add_and_checkout(self):
        self.client.login(username="testuser", password="password123")
        # Agregar al carrito
        response = self.client.get(reverse('agregar_al_carrito', args=["1001"]))
        self.assertEqual(response.status_code, 302)

        # Procesar pago
        response_checkout = self.client.post(reverse('procesar_pago'))
        self.assertEqual(response_checkout.status_code, 302)

        # Verificar descuento de stock
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 9)
        self.assertEqual(Venta.objects.count(), 1)


class CatalogFilterTests(TestCase):
    """Tests for catalog search and category filtering."""

    def setUp(self):
        self.client = Client()
        self.cat1 = Categoria.objects.create(codigo="CAT1", categoria="Videojuegos")
        self.cat2 = Categoria.objects.create(codigo="CAT2", categoria="Consolas")
        self.prod1 = Producto.objects.create(
            codigoBarra="P1", nombre="Elden Ring", precio=49990,
            stock=25, categoria=self.cat1, descripcion="RPG", foto="productos/a.png"
        )
        self.prod2 = Producto.objects.create(
            codigoBarra="P2", nombre="PlayStation 5", precio=549990,
            stock=10, categoria=self.cat2, descripcion="Console", foto="productos/b.png"
        )

    def test_search_no_results(self):
        response = self.client.get(reverse('productos') + '?q=ProductoInexistente')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Elden Ring")
        self.assertNotContains(response, "PlayStation 5")

    def test_empty_search_returns_all(self):
        response = self.client.get(reverse('productos') + '?q=')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Elden Ring")
        self.assertContains(response, "PlayStation 5")

    def test_index_page(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)


class CartTests(TestCase):
    """Tests for cart operations."""

    def setUp(self):
        self.client = Client()
        self.cat = Categoria.objects.create(codigo="CAT1", categoria="Tech")
        self.producto = Producto.objects.create(
            codigoBarra="P1", nombre="Test Product", precio=10000,
            stock=5, categoria=self.cat, descripcion="Test", foto="productos/t.png"
        )
        self.user = User.objects.create_user(username="buyer", password="testpass123")

    def test_view_empty_cart(self):
        response = self.client.get(reverse('carrito'))
        self.assertEqual(response.status_code, 200)

    def test_add_product_to_cart(self):
        response = self.client.get(reverse('agregar_al_carrito', args=["P1"]))
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertEqual(len(session.get('carrito', [])), 1)

    def test_add_same_product_twice_increments_quantity(self):
        self.client.get(reverse('agregar_al_carrito', args=["P1"]))
        self.client.get(reverse('agregar_al_carrito', args=["P1"]))
        session = self.client.session
        carrito = session.get('carrito', [])
        self.assertEqual(len(carrito), 1)
        self.assertEqual(carrito[0]['cantidad'], 2)

    def test_remove_product_from_cart(self):
        self.client.get(reverse('agregar_al_carrito', args=["P1"]))
        response = self.client.get(reverse('eliminar_producto_carrito', args=["P1"]))
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        self.assertEqual(len(session.get('carrito', [])), 0)

    def test_checkout_empty_cart(self):
        self.client.login(username="buyer", password="testpass123")
        response = self.client.post(reverse('procesar_pago'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Venta.objects.count(), 0)


class AuthTests(TestCase):
    """Tests for authentication flows."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="authuser", password="securepass123")

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_register_page_loads(self):
        response = self.client.get(reverse('registrarse'))
        self.assertEqual(response.status_code, 200)

    def test_login_valid_user(self):
        response = self.client.post(reverse('login'), {
            'username': 'authuser',
            'password': 'securepass123',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_invalid_user(self):
        response = self.client.post(reverse('login'), {
            'username': 'authuser',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)  # Re-renders form

    def test_logout(self):
        self.client.login(username="authuser", password="securepass123")
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_checkout_requires_login(self):
        response = self.client.post(reverse('procesar_pago'))
        self.assertEqual(response.status_code, 302)

    def test_ventas_requires_login(self):
        response = self.client.get(reverse('ventas'))
        self.assertEqual(response.status_code, 302)


class VentasTests(TestCase):
    """Tests for sales history view."""

    def setUp(self):
        self.client = Client()
        self.cat = Categoria.objects.create(codigo="CAT1", categoria="Tech")
        self.producto = Producto.objects.create(
            codigoBarra="P1", nombre="Test Product", precio=10000,
            stock=5, categoria=self.cat, descripcion="Test", foto="productos/t.png"
        )
        self.user = User.objects.create_user(username="customer", password="testpass123")
        self.admin = User.objects.create_superuser(username="admin", password="adminpass123")

    def test_customer_sees_own_purchases(self):
        Venta.objects.create(
            usuario=self.user, producto=self.producto,
            cantidad=1, precio_total=10000
        )
        self.client.login(username="customer", password="testpass123")
        response = self.client.get(reverse('ventas'))
        self.assertEqual(response.status_code, 200)

    def test_admin_sees_all_purchases(self):
        Venta.objects.create(
            usuario=self.user, producto=self.producto,
            cantidad=1, precio_total=10000
        )
        self.client.login(username="admin", password="adminpass123")
        response = self.client.get(reverse('ventas'))
        self.assertEqual(response.status_code, 200)
