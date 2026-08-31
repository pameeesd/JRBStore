from decimal import Decimal
from django.db import migrations


def seed_admin_and_products(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Categoria = apps.get_model('storeApp', 'Categoria')
    Producto = apps.get_model('storeApp', 'Producto')

    # Ensure admin staff user exists
    if not User.objects.filter(username='admin').exists():
        u = User.objects.create_superuser(
            username='admin',
            email='admin@jrbstore.com',
            password='AdminPassword123!'
        )
        u.is_staff = True
        u.is_superuser = True
        u.save()

    # Ensure category exists
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
        ('storeApp', '0007_seed_categories'),
    ]

    operations = [
        migrations.RunPython(seed_admin_and_products),
    ]
