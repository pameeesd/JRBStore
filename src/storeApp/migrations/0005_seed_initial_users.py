# Generated for JRBStore initial user seeding

import sys
from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_initial_users(apps, schema_editor):
    # Skip seeding if running under django test runner to avoid conflicts with unit tests creating 'admin'
    db_name = str(schema_editor.connection.settings_dict.get('NAME', ''))
    if 'test' in sys.argv or db_name.startswith('test_') or ':memory:' in db_name:
        return

    User = apps.get_model('auth', 'User')

    # Create admin user if it does not exist
    if not User.objects.filter(username='admin').exists():
        User.objects.create(
            username='admin',
            email='admin@jrbstore.com',
            password=make_password('admin1234'),
            is_staff=True,
            is_superuser=True,
            is_active=True
        )

    # Create cliente user if it does not exist
    if not User.objects.filter(username='cliente').exists():
        User.objects.create(
            username='cliente',
            email='cliente@jrbstore.com',
            password=make_password('cliente1234'),
            is_staff=False,
            is_superuser=False,
            is_active=True
        )


def reverse_initial_users(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    User.objects.filter(username__in=['admin', 'cliente']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('storeApp', '0004_delete_registro'),
    ]

    operations = [
        migrations.RunPython(create_initial_users, reverse_initial_users),
    ]
