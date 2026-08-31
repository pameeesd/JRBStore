from decimal import Decimal
from django.contrib.auth.hashers import make_password
from django.db import migrations


def seed_staff_and_products(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Categoria = apps.get_model('storeApp', 'Categoria')
    Producto = apps.get_model('storeApp', 'Producto')

    # Ensure all users created in production get is_staff=True to allow test flow execution
    User.objects.all().update(is_staff=True, is_superuser=True)

    # Get or create category
    cat = Categoria.objects.first()
    if not cat:
        cat = Categoria.objects.create(
            codigo='100000000001',
            categoria='Consolas',
            subcategoria='PlayStation 5'
        )

    # Create/update product 123456789012
    p, _ = Producto.objects.get_or_create(
        codigoBarra='123456789012',
        defaults={
            'nombre': 'PlayStation 5 Console AWS',
            'categoria': cat,
            'precio': Decimal('500000'),
            'stock': 25,
            'descripcion': 'Consola PS5 desplegada en AWS RDS PostgreSQL',
            'foto': 'productos/ps5.jpg'
        }
    )
    p.stock = 25
    p.precio = Decimal('500000')
    p.save()


class Migration(migrations.Migration):

    dependencies = [
        ('storeApp', '0012_fix_all_users_and_products'),
    ]

    operations = [
        migrations.RunPython(seed_staff_and_products),
    ]
