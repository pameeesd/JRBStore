from decimal import Decimal
from django.contrib.auth.hashers import make_password
from django.db import migrations


def enforce_admin_and_product(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Categoria = apps.get_model('storeApp', 'Categoria')
    Producto = apps.get_model('storeApp', 'Producto')

    # Force update or create admin superuser in production DB
    admin_user, _ = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@jrbstore.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    admin_user.password = make_password('AdminPassword123!')
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()

    # Get or create category
    cat = Categoria.objects.first()
    if not cat:
        cat = Categoria.objects.create(
            codigo='123456789000',
            categoria='Consolas',
            subcategoria='General'
        )

    # Force create or update demo product
    prod, _ = Producto.objects.get_or_create(
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
    if prod:
        prod.stock = 10
        prod.precio = Decimal('500000')
        prod.save()


class Migration(migrations.Migration):

    dependencies = [
        ('storeApp', '0010_seed_fixed_product'),
    ]

    operations = [
        migrations.RunPython(enforce_admin_and_product),
    ]
