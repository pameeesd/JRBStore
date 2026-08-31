from decimal import Decimal
from django.contrib.auth.hashers import make_password
from django.db import migrations


def reset_admin_and_seed_products(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Categoria = apps.get_model('storeApp', 'Categoria')
    Producto = apps.get_model('storeApp', 'Producto')

    # Get or create admin staff user and ALWAYS enforce password & staff privileges
    u, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@jrbstore.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    u.password = make_password('AdminPassword123!')
    u.is_staff = True
    u.is_superuser = True
    u.save()

    # Get or create category
    cat, _ = Categoria.objects.get_or_create(
        categoria='Consolas',
        subcategoria='PlayStation 5',
        defaults={'codigo': '100000000001'}
    )

    # Seed demo product
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
        ('storeApp', '0008_seed_products'),
    ]

    operations = [
        migrations.RunPython(reset_admin_and_seed_products),
    ]
