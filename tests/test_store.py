from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
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
