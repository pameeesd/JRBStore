from django.db import migrations

INITIAL_TAXONOMY = {
    'Consolas': [
        'Switch 2', 'PlayStation 5', 'Switch', 'AsusNuevo', 'Lenovo', 'Steam Deck', 'PlayStation 4', 'Xbox Series S|X'
    ],
    'Nintendo': [
        'Switch 2', 'Consolas Switch 2', 'Juegos Switch 2', 'Accesorios Switch 2', 'Switch', 'Consolas Switch',
        'Juegos Switch', 'Accesorios Switch', 'WiiU', 'Juegos Wii U', 'Accesorios Wii U', 'Wii', 'Juegos Wii',
        'Accesorios Wii', '3DS', 'Juegos 3DS', 'Accesorios 3DS', 'Otros Accesorios', 'DS'
    ],
    'Playstation': [
        'PlayStation 5', 'Consolas PS5', 'Juegos PS5', 'Accesorios PS5', 'PlayStation 4', 'Consolas PS4',
        'Juegos PS4', 'Accesorios PS4', 'PlayStation 3', 'Juegos PS3', 'Accesorios PS3', 'Otros Accesorios',
        'Accesorios PS VITA', 'Accesorios PSP', 'Accesorios PS2'
    ],
    'Xbox': [
        'Xbox Series S|X', 'Consolas Xbox Series S|X', 'Juegos Xbox Series S|X', 'Accesorios Xbox Series S|X',
        'Xbox One', 'Juegos Xbox One', 'Accesorios Xbox One', 'Xbox 360', 'Juegos Xbox 360', 'Accesorios Xbox 360',
        'Membresías'
    ],
    'Accesorios': [
        'Periféricos', 'Audífonos', 'Bases enfriadoras', 'Cables', 'Cámaras web', 'Grabadores externos',
        'Monitores', 'Parlantes', 'Presentador', 'Teclados', 'Gamers - streamers', 'Controles', 'Mouse',
        'Mouse pad', 'Sillas', 'Micrófonos', 'Lentes', 'Volantes'
    ]
}

def seed_categories(apps, schema_editor):
    Categoria = apps.get_model('storeApp', 'Categoria')
    code_counter = 100000000001

    for cat_name, subcats in INITIAL_TAXONOMY.items():
        for subcat_name in subcats:
            code_str = str(code_counter)
            if not Categoria.objects.filter(categoria=cat_name, subcategoria=subcat_name).exists():
                Categoria.objects.create(
                    codigo=code_str,
                    categoria=cat_name,
                    subcategoria=subcat_name
                )
                code_counter += 1

def unseed_categories(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('storeApp', '0006_categoria_subcategoria_alter_producto_categoria_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_categories, unseed_categories),
    ]
