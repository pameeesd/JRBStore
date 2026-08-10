# 🛒 JRBStore — Plataforma Web E-Commerce

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.1-green?logo=django)
![CI](https://img.shields.io/badge/CI-GitHub_Actions-blue?logo=github-actions)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Descripción

**JRBStore** es una plataforma web de comercio electrónico desarrollada con **Django 5.1** y **Python 3.11+**. Permite navegar un catálogo de productos, filtrar por categorías, gestionar un carrito de compras basado en sesiones HTTP y procesar compras con descuento automático de inventario.

**JRBStore** is an e-commerce web platform built with **Django 5.1** and **Python 3.11+**. It features product catalog browsing, category filtering, session-based shopping cart, and checkout with automatic inventory management.

---

## Objetivo del Proyecto

Proyecto de portfolio que demuestra competencias en desarrollo web full-stack con Python/Django, incluyendo:

- Desarrollo de aplicaciones web con **Django** (MVT)
- Modelado de **bases de datos** relacionales
- **Testing** automatizado con Django TestCase
- Contenerización con **Docker** y **Gunicorn**
- Integración continua con **GitHub Actions**
- Buenas prácticas de **seguridad** y configuración

---

## Funcionalidades Principales

| Funcionalidad | Descripción |
|---|---|
| **Catálogo de productos** | Listado con búsqueda por nombre y filtrado por categoría |
| **Carrito de compras** | Basado en sesiones HTTP, sin necesidad de cuenta para agregar productos |
| **Checkout con inventario** | Procesamiento de compras con descuento automático de stock |
| **Autenticación** | Registro de usuarios, login/logout, roles (Admin / Cliente) |
| **Panel administrativo** | CRUD completo de productos y categorías con dashboard de KPIs |
| **Historial de ventas** | Vista de compras por usuario y vista global para administradores |

---

## Arquitectura

```
JRBStore/
├── .github/workflows/       # CI pipeline (GitHub Actions)
│   └── ci.yml
├── docker/                  # Dockerfile (Gunicorn, non-root)
│   └── Dockerfile
├── src/                     # Código fuente Django
│   ├── jrbstore/            # Configuración del proyecto (settings, urls, wsgi)
│   ├── storeApp/            # Aplicación principal
│   │   ├── models.py        # Categoria, Producto, Registro, Venta
│   │   ├── views.py         # Vistas (catálogo, carrito, checkout, auth)
│   │   ├── forms.py         # Formularios (productos, categorías, registro)
│   │   ├── urls.py          # Rutas de la aplicación
│   │   ├── templates/       # Templates HTML (Bootstrap 5)
│   │   ├── static/          # CSS, JS, imágenes estáticas
│   │   └── migrations/      # Migraciones de base de datos
│   ├── media/               # Archivos subidos por usuarios (no versionados)
│   └── manage.py
├── tests/                   # Suite de tests automatizados
│   └── test_store.py
├── docker-compose.yml       # Orquestación local con Docker Compose
├── requirements.txt         # Dependencias de producción
├── requirements-dev.txt     # Dependencias de desarrollo (incluye linter)
├── pyproject.toml           # Configuración de Ruff (linter)
├── .env.example             # Variables de entorno (template)
├── CHANGELOG.md             # Registro de cambios (SemVer)
└── LICENSE                  # MIT
```

---

## Stack Tecnológico

| Capa | Tecnología |
|---|---|
| Lenguaje | Python 3.11+ |
| Framework | Django 5.1 |
| Base de Datos | SQLite3 (desarrollo) · MySQL (opcional) |
| Frontend | HTML5, CSS3, JavaScript, Bootstrap 5 |
| Servidor WSGI | Gunicorn |
| Contenedor | Docker |
| CI | GitHub Actions |
| Linter | Ruff |
| Imágenes | Pillow |

---

## Testing

La suite de tests cubre las funcionalidades principales de la aplicación:

- **Catálogo**: Carga de página, búsqueda por nombre, filtrado, búsqueda vacía
- **Carrito**: Vista vacía, agregar productos, cantidades duplicadas, eliminar, checkout vacío
- **Autenticación**: Login válido/inválido, registro, logout, rutas protegidas
- **Ventas**: Historial de cliente, vista administrativa
- **Checkout**: Procesamiento de pago completo con descuento de stock

```bash
# Ejecutar tests (desde la raíz del proyecto)
python src/manage.py test tests --verbosity=2
```

> **Nota**: Los tests usan una base de datos SQLite en memoria; no modifican datos locales.

---

## Docker

La aplicación está contenerizada con Docker usando **Gunicorn** como servidor WSGI de producción.

```bash
# Construir la imagen
docker build -f docker/Dockerfile -t jrbstore .

# Ejecutar el contenedor
docker run -p 8000:8000 \
  -e SECRET_KEY="genera-una-clave-segura" \
  -e DEBUG=False \
  -e ALLOWED_HOSTS="localhost,127.0.0.1" \
  jrbstore

# O usando Docker Compose (requiere archivo .env)
cp .env.example .env  # Editar con valores reales
docker compose up --build
```

Características del Dockerfile:
- Imagen base `python:3.11-slim`
- Servidor WSGI Gunicorn (no usa `runserver`)
- Usuario no-root para seguridad
- Collectstatic durante el build
- `.dockerignore` para contexto de build mínimo

---

## CI/CD

El pipeline de GitHub Actions ejecuta automáticamente en cada push/PR a `main` y `develop`:

| Paso | Descripción |
|---|---|
| **Lint** | Análisis estático con Ruff |
| **Django Check** | Validación de configuración Django |
| **Migraciones** | Ejecución de migraciones de BD |
| **Tests** | Suite completa de 20 tests |
| **Docker Build** | Validación de construcción de imagen |

---

## Instalación Local

### Requisitos
- Python 3.11 o superior
- pip

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/pameeesd/JRBStore.git
cd JRBStore

# 2. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env: generar SECRET_KEY y configurar DEBUG=True

# 5. Ejecutar migraciones
python src/manage.py migrate

# 6. Crear usuario administrador
python src/manage.py createsuperuser

# 7. Iniciar servidor de desarrollo
python src/manage.py runserver
```

Navegar a `http://127.0.0.1:8000/`

---

## Variables de Entorno

| Variable | Descripción | Requerida | Default |
|---|---|---|---|
| `SECRET_KEY` | Clave secreta de Django | Sí (producción) | Auto-generada en DEBUG |
| `DEBUG` | Modo de depuración | No | `False` |
| `ALLOWED_HOSTS` | Hosts permitidos (separados por coma) | No | `localhost,127.0.0.1` |
| `USE_MYSQL` | Usar MySQL en lugar de SQLite | No | `False` |
| `DB_HOST` | Host de MySQL | No | `localhost` |
| `DB_PORT` | Puerto de MySQL | No | `3306` |
| `DB_NAME` | Nombre de la BD MySQL | No | `storeapp` |
| `DB_USER` | Usuario de MySQL | No | `root` |
| `DB_PASSWORD` | Contraseña de MySQL | No | `""` |

Para generar una SECRET_KEY segura:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Comandos Principales

| Comando | Descripción |
|---|---|
| `python src/manage.py runserver` | Iniciar servidor de desarrollo |
| `python src/manage.py test tests --verbosity=2` | Ejecutar suite de tests |
| `python src/manage.py migrate` | Aplicar migraciones de BD |
| `python src/manage.py createsuperuser` | Crear usuario administrador |
| `python src/manage.py collectstatic` | Recopilar archivos estáticos |
| `python -m ruff check src/ tests/` | Ejecutar linter |
| `docker build -f docker/Dockerfile -t jrbstore .` | Construir imagen Docker |
| `docker compose up --build` | Levantar con Docker Compose |

---

## Estado Actual

**v1.2.0 — Demo Funcional** 🟢

El proyecto se encuentra estable con suite de tests automatizada, pipeline CI completo y contenerización Docker funcional.

---

## Roadmap

- [x] v1.0.0: Plataforma base con carrito de compras y autenticación
- [x] v1.1.0: Búsqueda de productos, filtro por categorías, descuento de stock y tests
- [x] v1.2.0: Revisión de seguridad, Docker con Gunicorn, CI/CD mejorado, testing ampliado
- [ ] v2.0.0: Pasarela de pagos (Webpay / Stripe) e integración REST API

---

## Licencia

Este proyecto está liberado bajo la [Licencia MIT](LICENSE).
