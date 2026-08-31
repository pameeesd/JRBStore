import io
from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase
from PIL import Image

from storeApp.management.commands.seed_catalog import PRODUCTS_DATA
from storeApp.models import Producto


class SeedCatalogCommandTests(TestCase):
    def test_01_first_execution_creates_10_products(self):
        call_command('seed_catalog')
        seeded_barcodes = [p['barcode'] for p in PRODUCTS_DATA]
        prods = Producto.objects.filter(codigoBarra__in=seeded_barcodes)
        self.assertEqual(prods.count(), 10)

    def test_02_second_execution_does_not_duplicate_products(self):
        call_command('seed_catalog')
        call_command('seed_catalog')
        seeded_barcodes = [p['barcode'] for p in PRODUCTS_DATA]
        prods = Producto.objects.filter(codigoBarra__in=seeded_barcodes)
        self.assertEqual(prods.count(), 10)

    def test_03_barcodes_have_exactly_12_digits(self):
        call_command('seed_catalog')
        for pdata in PRODUCTS_DATA:
            code = pdata['barcode']
            self.assertEqual(len(code), 12)
            self.assertTrue(code.isdigit())
            prod = Producto.objects.get(codigoBarra=code)
            self.assertIsNotNone(prod)

    def test_04_categories_and_subcategories_are_correct(self):
        call_command('seed_catalog')
        for pdata in PRODUCTS_DATA:
            prod = Producto.objects.get(codigoBarra=pdata['barcode'])
            self.assertEqual(prod.categoria.categoria.lower(), pdata['category'].lower())
            if pdata['subcategory']:
                self.assertEqual(prod.categoria.subcategoria.lower(), pdata['subcategory'].lower())

    def test_05_prices_are_stored_as_decimal(self):
        call_command('seed_catalog')
        for pdata in PRODUCTS_DATA:
            prod = Producto.objects.get(codigoBarra=pdata['barcode'])
            self.assertIsInstance(prod.precio, Decimal)
            self.assertEqual(prod.precio, pdata['price'])

    def test_06_initial_stocks_are_correct(self):
        call_command('seed_catalog')
        for pdata in PRODUCTS_DATA:
            prod = Producto.objects.get(codigoBarra=pdata['barcode'])
            self.assertEqual(prod.stock, pdata['stock'])

    def test_07_images_are_associated(self):
        call_command('seed_catalog')
        for pdata in PRODUCTS_DATA:
            prod = Producto.objects.get(codigoBarra=pdata['barcode'])
            self.assertTrue(bool(prod.foto))
            self.assertIn(pdata['filename'], prod.foto.name)

    def test_08_invalid_image_is_rejected(self):
        with self.assertRaises((OSError, SyntaxError)):
            bad_bytes = b"NOT_AN_IMAGE_CONTENT"
            check_img = Image.open(io.BytesIO(bad_bytes))
            check_img.verify()

    def test_09_repeat_seed_preserves_existing_modified_stock(self):
        call_command('seed_catalog')
        prod = Producto.objects.get(codigoBarra='900000000001')
        prod.stock = 3  # Stock changed after sale
        prod.save()

        # Re-run seed
        call_command('seed_catalog')

        prod.refresh_from_db()
        self.assertEqual(prod.stock, 3)  # Stock must stay 3, not reset to 8

    def test_10_no_duplicates_created(self):
        initial_total = Producto.objects.count()
        call_command('seed_catalog')
        after_first = Producto.objects.count()
        self.assertEqual(after_first, initial_total + 10)

        call_command('seed_catalog')
        after_second = Producto.objects.count()
        self.assertEqual(after_second, after_first)
