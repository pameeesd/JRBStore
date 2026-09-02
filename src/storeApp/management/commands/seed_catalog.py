import hashlib
import io
import logging
import os
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image, ImageDraw

from storeApp.models import Categoria, Producto

logger = logging.getLogger(__name__)

PRODUCTS_DATA = [
    {
        'barcode': '900000000001',
        'name': 'PlayStation 5',
        'category': 'Consolas',
        'subcategory': 'PlayStation 5',
        'price': Decimal(549990),
        'stock': 8,
        'description': 'Consola PlayStation 5 con tecnología de nueva generación, almacenamiento SSD de alta velocidad y control inalámbrico DualSense. Diseñada para disfrutar juegos en resolución 4K y una experiencia de juego inmersiva.',
        'filename': 'play_5.png',
        'color': (30, 60, 150)
    },
    {
        'barcode': '900000000002',
        'name': 'AUDIFONO G325 BLACK',
        'category': 'Accesorios',
        'subcategory': 'Audífonos',
        'price': Decimal(39990),
        'stock': 15,
        'description': 'Audífonos G325 Black con diseño cómodo y sonido envolvente. Ideales para gaming, entretenimiento y uso diario.',
        'filename': 'audifono_g325_black.png',
        'color': (40, 40, 40)
    },
    {
        'barcode': '900000000003',
        'name': 'Demon Slayer -Kimetsu no Yaiba- The Hinokami Chronicles PS5',
        'category': 'Playstation',
        'subcategory': 'Juegos PS5',
        'price': Decimal(29990),
        'stock': 12,
        'description': 'Vive la historia de Demon Slayer en una aventura de acción basada en el popular anime. Combate con tus personajes favoritos y disfruta gráficos optimizados para PlayStation 5.',
        'filename': 'demon_slayer_ps5.png',
        'color': (180, 40, 40)
    },
    {
        'barcode': '900000000004',
        'name': 'Grand Theft Auto V',
        'category': 'Playstation',
        'subcategory': 'Juegos PS5',
        'price': Decimal(24990),
        'stock': 10,
        'description': 'Grand Theft Auto V ofrece una extensa aventura de acción en mundo abierto, con una campaña protagonizada por tres personajes y una gran variedad de actividades y misiones.',
        'filename': 'gta_v.png',
        'color': (50, 120, 50)
    },
    {
        'barcode': '900000000005',
        'name': 'Elden Ring PS5',
        'category': 'Playstation',
        'subcategory': 'Juegos PS5',
        'price': Decimal(49990),
        'stock': 7,
        'description': 'RPG de acción desarrollado por FromSoftware. Explora un enorme mundo de fantasía, descubre secretos y enfréntate a desafiantes enemigos y jefes.',
        'filename': 'elden_ring_ps5.png',
        'color': (140, 100, 30)
    },
    {
        'barcode': '900000000006',
        'name': 'Lego Batman Legacy of The Dark Knight PS5',
        'category': 'Playstation',
        'subcategory': 'Juegos PS5',
        'price': Decimal(59990),
        'stock': 6,
        'description': 'Aventura de acción LEGO protagonizada por Batman. Explora Gotham, resuelve desafíos y disfruta una experiencia inspirada en el universo del Caballero Oscuro.',
        'filename': 'lego_batman_ps5.png',
        'color': (30, 30, 70)
    },
    {
        'barcode': '900000000007',
        'name': 'Super Mario 3D World + Bowser´s Fury Switch',
        'category': 'Nintendo',
        'subcategory': 'Juegos Switch',
        'price': Decimal(49990),
        'stock': 10,
        'description': 'Aventura de plataformas de Super Mario que combina Super Mario 3D World con la expansión Bowser\'s Fury. Juega solo o acompañado y explora coloridos mundos.',
        'filename': 'super_mario_3d_world_switch.png',
        'color': (220, 50, 50)
    },
    {
        'barcode': '900000000008',
        'name': 'Marvel´s Guardians of The Galaxy XBS',
        'category': 'Xbox',
        'subcategory': 'Juegos Xbox Series S|X',
        'price': Decimal(34990),
        'stock': 8,
        'description': 'Aventura de acción protagonizada por los Guardianes de la Galaxia. Forma equipo con Star-Lord y disfruta una historia cargada de combates, exploración y humor.',
        'filename': 'guardians_galaxy_xbs.png',
        'color': (120, 40, 160)
    },
    {
        'barcode': '900000000009',
        'name': 'Monitor MSI G242L E14',
        'category': 'Accesorios',
        'subcategory': 'Monitores',
        'price': Decimal(129990),
        'stock': 5,
        'description': 'Monitor gaming MSI de 24 pulgadas con panel IPS, resolución Full HD y frecuencia de actualización de 144 Hz. Ideal para gaming y entretenimiento.',
        'filename': 'monitor_msi_g242l_e14.png',
        'color': (60, 60, 60)
    },
    {
        'barcode': '900000000010',
        'name': 'Consola Nintendo Switch 2 + Pokémon Legends: Z-A Edition Bundle',
        'category': 'Nintendo',
        'subcategory': 'Consolas Switch 2',
        'price': Decimal(649990),
        'stock': 4,
        'description': 'Bundle de Nintendo Switch 2 con temática de Pokémon Legends: Z-A. Disfruta una consola de nueva generación y una experiencia portátil y doméstica.',
        'filename': 'switch_2_pokemon_za.png',
        'color': (230, 80, 20)
    }
]

def get_product_image_bytes(filename, fallback_name, fallback_color):
    """Retrieve image bytes from local media/productos if present, validating with Pillow.
    Otherwise generate a clean Pillow-validated PNG byte payload as fallback."""
    local_media_path = os.path.join(settings.BASE_DIR, 'media', 'productos', filename)
    if os.path.exists(local_media_path):
        try:
            with open(local_media_path, 'rb') as f:
                data = f.read()
            img = Image.open(io.BytesIO(data))
            img.verify()
            return data
        except Exception as e:
            logger.warning(f"Local image {filename} invalid or unreadable: {e}")

    # Fallback synthetic image generation
    img = Image.new('RGB', (400, 400), color=fallback_color)
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 20, 380, 380], outline=(255, 255, 255), width=3)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    img_bytes = buf.getvalue()

    check_img = Image.open(io.BytesIO(img_bytes))
    fmt = check_img.format
    check_img.verify()
    if not fmt or fmt.lower() not in ['jpeg', 'png', 'jpg']:
        raise ValidationError("Formato de imagen generado no es válido.")

    return img_bytes


class Command(BaseCommand):
    help = 'Seeds initial 10 product catalog idempotently with images and categories.'

    def log_msg(self, msg):
        try:
            self.stdout.write(str(msg))
        except Exception as err:
            logger.warning(f"Could not write to stdout: {err}")

    def handle(self, *args, **options):
        self.log_msg("Iniciando inyeccion controlada del catalogo inicial JRBStore...")

        created_count = 0
        updated_count = 0
        total_inventory_value = Decimal(0)
        total_initial_stock = 0

        for pdata in PRODUCTS_DATA:
            barcode = pdata['barcode']
            name = pdata['name']
            cat_name = pdata['category']
            subcat_name = pdata['subcategory']
            price = pdata['price']
            stock = pdata['stock']
            desc = pdata['description']
            filename = pdata['filename']
            color = pdata['color']

            try:
                with transaction.atomic():
                    # Get or create Category
                    cat_obj = Categoria.objects.filter(categoria__iexact=cat_name, subcategoria__iexact=subcat_name).first()
                    if not cat_obj:
                        cat_obj = Categoria.objects.filter(categoria__iexact=cat_name).first()

                    if not cat_obj:
                        # Deterministic 12-digit numeric code from md5 hash
                        hash_int = int(hashlib.md5(f"{cat_name}:{subcat_name}".encode()).hexdigest()[:12], 16)
                        code_gen = str(100000000000 + (hash_int % 899999999999))
                        cat_obj, created = Categoria.objects.get_or_create(
                            categoria=cat_name,
                            subcategoria=subcat_name,
                            defaults={'codigo': code_gen}
                        )
                        if created:
                            self.log_msg(f"Categoria creada: {cat_name} - {subcat_name} ({code_gen})")

                    storage_path = f"productos/{filename}"
                    if not default_storage.exists(storage_path):
                        try:
                            img_bytes = get_product_image_bytes(filename, name, color)
                            default_storage.save(storage_path, ContentFile(img_bytes))
                        except Exception as img_err:
                            self.log_msg(f"Aviso al guardar imagen {storage_path}: {img_err}")

                    # Check if product exists by barcode
                    prod = Producto.objects.filter(codigoBarra=barcode).first()

                    if not prod:
                        prod = Producto(
                            codigoBarra=barcode,
                            nombre=name,
                            categoria=cat_obj,
                            precio=price,
                            stock=stock,
                            descripcion=desc,
                            foto=storage_path
                        )
                        prod.save()
                        created_count += 1
                        self.log_msg(f"[NUEVO] Producto creado: {name} ({barcode}) - ${price:,.0f} - Stock: {stock}")
                    else:
                        updated_count += 1
                        prod.nombre = name
                        prod.categoria = cat_obj
                        prod.precio = price
                        prod.descripcion = desc
                        if not prod.foto:
                            prod.foto = storage_path
                        prod.save()
                        self.log_msg(f"[EXISTENTE] Producto actualizado (Stock intacto: {prod.stock}): {name} ({barcode})")

                    total_inventory_value += prod.precio * prod.stock
                    total_initial_stock += prod.stock
            except Exception as e:
                self.log_msg(f"Error procesando producto {name} ({barcode}): {e}")

        self.log_msg("\n" + "=" * 60)
        self.log_msg(" RESUMEN DE CARGA DE CATALOGO:")
        self.log_msg(f" Productos creados: {created_count}")
        self.log_msg(f" Productos existentes: {updated_count}")
        self.log_msg(f" Stock total acumulado: {total_initial_stock} unidades")
        self.log_msg(f" Valor total del inventario: ${total_inventory_value:,.0f} CLP")
        self.log_msg("=" * 60 + "\n")
