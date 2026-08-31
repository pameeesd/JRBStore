from decimal import Decimal
from django.db import migrations


def seed_product_guaranteed(apps, schema_editor):
    Categoria = apps.get_model('storeApp', 'Categoria')
    Producto = apps.get_model('storeApp', 'Producto')

    cat = Categoria.objects.first()
    if not cat:
        cat = Categoria.objects.create(
            codigo='123456789000',
            categoria='Consolas',
            subcategoria='General'
        )

    Producto.objects.get_or_create(
        codigoBarra='123456789012',
        defaults={
            'nombre': 'PlayStation 5 Console AWS',
            'categoria': cat,
            'precio': Decimal('500000'),
            'stock': 10,
            'descripcion': 'Consola PS5 desplegada en AWS RDS PostgreSQL',
            'foto': 'productos/ps5.jpg'
        }
    )


class Migration(migrations.Migration):

    dependencies = [
        ('storeApp', '0009_reset_admin'),
    ]

    operations = [
        migrations.RunPython(seed_product_guaranteed),
    ]
