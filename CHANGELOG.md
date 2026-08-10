# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [1.2.0] - 2026-08-09

### Seguridad (`security`)
- Eliminada SECRET_KEY hardcodeada de `settings.py`; ahora es obligatoria vía variable de entorno en producción.
- `DEBUG` cambiado a `False` por defecto.
- `ALLOWED_HOSTS` configurable mediante variable de entorno (antes era `['*']`).
- Creado `.gitignore` (no existía); `db.sqlite3`, `__pycache__/` y `media/` dejaron de versionarse.
- Eliminado placeholder de SECRET_KEY real en `.env.example`.
- Eliminadas credenciales de administrador del README.

### Corregido (`fix`)
- Corregido bug en `views.py` L175: expresión `waterfall` (variable inexistente) reemplazada por `if not encontrado`.
- Corregida variable `password1` no utilizada en `forms.py`; `clean_password2()` ahora delega al padre.
- Corregido descubrimiento de tests en CI (antes apuntaba a archivo vacío).

### Añadido (`feat`)
- Dockerfile reescrito: Gunicorn como servidor WSGI, usuario no-root, `collectstatic` en build.
- Creado `.dockerignore` para minimizar contexto de build.
- Creado `docker-compose.yml` para desarrollo local.
- Suite de tests ampliada de 3 a 20 tests (catálogo, carrito, auth, ventas, checkout).
- Pipeline CI actualizado: `actions/checkout@v4`, `setup-python@v5`, cache de pip, linting con Ruff, Docker build.
- Creado `requirements-dev.txt` con Ruff.
- Creado `pyproject.toml` con configuración de Ruff.
- Agregado `gunicorn` a `requirements.txt`.
- Agregado `STATIC_ROOT` a `settings.py` para `collectstatic`.

### Documentación (`docs`)
- README reescrito como portfolio profesional con descripción bilingüe, arquitectura, stack, testing, Docker, CI, variables de entorno y comandos.
- Eliminada referencia "Production Ready"; reemplazada por "Demo Funcional".

## [1.1.0] - 2026-07-28

### Añadido (`feat`)
- Descuento automático de stock en inventario al procesar un pago exitoso (`procesar_pago`).
- Barra de búsqueda por nombre de producto y selector de filtro por categorías en el catálogo (`productos.html`).
- Contador dinámico de artículos en el icono del carrito dentro de la barra de navegación.
- Pruebas automatizadas de integración para vistas de catálogo, carrito y checkout (`tests/test_store.py`).

## [1.0.0] - 2026-07-28

### Añadido (`feat`)
- Plataforma Web E-Commerce basada en Django 5.1 para venta de productos tecnológicos y retail.
- Carrito de compras funcional basado en sesiones HTTP.
- Módulo de procesamiento de pagos y registro de ventas por usuario y acumulado general de administración.
- Autenticación completa de usuarios con control de roles (`Admin` y `Cliente`).

### Arreglado (`fix`)
- Corrección de `SyntaxError` crítico en `storeApp/urls.py` generado por etiquetas de plantilla accidentales.
- Implementación de conector híbrido de base de datos con fallback automático a `sqlite3`.
