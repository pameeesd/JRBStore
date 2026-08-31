from decimal import Decimal
from django.contrib.auth.hashers import make_password
from django.db import migrations


def fix_all(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Categoria = apps.get_model('storeApp', 'Categoria')
    Producto = apps.get_model('storeApp', 'Producto')

    # Update any existing admin user regardless of case
    admins = User.objects.filter(username__iexact='admin')
    if admins.exists():
        for a in admins:
            a.password = make_password('AdminPassword123!')
            a.is_staff = True
            a.is_superuser = True
            a.save()
    else:
        User.objects.create(
            username='admin',
            email='admin@jrbstore.com',
            password=make_password('AdminPassword123!'),
            is_staff=True,
            is_superuser=True
        )

    # Get or create category
    cat = Categoria.objects.first()
    if not cat:
        cat = Categoria.objects.create(
            codigo='100000000001',
            categoria='Consolas',
            subcategoria='PlayStation 5'
        )

    # Seed products with barcodes 123456789012 and 881188118811
    for barcode, name in [('123456789012', 'PlayStation 5 Console AWS'), ('881188118811', 'Producto Test AWS')]:
        p, _ = Producto.objects.get_or_create(
            codigoBarra=barcode,
            defaults={
                'nombre': name,
                'categoria': cat,
                'precio': Decimal('500000'),
                'stock': 50,
                'descripcion': 'Producto e-commerce en AWS RDS PostgreSQL',
                'foto': 'productos/ps5.jpg'
            }
        )
        p.stock = 50
        p.precio = Decimal('500000')
        p.save()


class Migration(migrations.Migration):

    dependencies = [
        ('storeApp', '0011_enforce_admin_and_product'),
    ]

    operations = [
        migrations.RunPython(fix_all),
    ]
