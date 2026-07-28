# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

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
