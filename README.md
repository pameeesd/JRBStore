# 🛒 JRBStore — Plataforma Web E-Commerce

![PEP Level 4](https://img.shields.io/badge/PEP_Standard-Level_4_DevOps_Ready-blue?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![Django](https://img.shields.io/badge/Framework-Django_5.1-green?logo=django)
![Database](https://img.shields.io/badge/Database-SQLite%20%2F%20MySQL-orange)
![Version](https://img.shields.io/badge/Version-v1.1.0-brightgreen)

---

## 1. Descripción

**JRBStore** es una plataforma web completa de comercio electrónico (E-Commerce) desarrollada en **Django 5.1**. El sistema permite navegar por catálogos de productos tecnológicos y retail, realizar búsquedas con filtros por categorías, gestionar un carrito de compras basado en sesiones, procesar compras con descuento de stock en tiempo real y consultar el historial de ventas tanto para clientes como para administradores.

---

## 2. Objetivos

- **Catálogo Interactivo**: Facilitar la búsqueda y filtrado dinámico de productos por categoría y palabra clave.
- **Carrito de Compras y Checkout**: Ofrecer un flujo de compra fluido basado en sesiones HTTP con control de inventario automático.
- **Gestión Administrativa**: Proveer paneles CRUD para que los administradores gestionen productos, fotografías, precios y categorías.
- **Calidad e Ingeniería PEP**: Adherir al **Persevera Engineering Playbook (PEP)** con arquitectura modular, pruebas de integración y pipeline CI.

---

## 3. Tecnologías

- **Lenguaje**: Python 3.11+
- **Framework Web**: Django 5.1.3
- **Base de Datos**: SQLite3 (autónoma) & conector opcional MySQL
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Imágenes**: Pillow (PIL)
- **CI/CD & DevOps**: GitHub Actions & Docker

---

## 4. Arquitectura

El proyecto sigue una arquitectura modular compatible con **PEP Nivel 4 (DevOps Ready)**:

```
JRBStore/
├── .github/              # Pipeline CI y plantillas de Issues/PRs
│   ├── workflows/ci.yml
│   └── ISSUE_TEMPLATE/
├── docs/                 # Documentación y diagramas
├── src/                  # Aplicación Django
│   ├── jrbstore/         # Configuración global del proyecto (settings, urls)
│   ├── storeApp/         # Aplicación principal (modelos, vistas, plantillas)
│   ├── media/            # Archivos multimedia cargados (imágenes de productos)
│   ├── db.sqlite3        # Base de datos SQLite local
│   └── manage.py         # Gestor de comandos de Django
├── tests/                # Pruebas de integración automatizadas
├── assets/               # Recursos estáticos globales
├── docker/               # Dockerfile contenerizado
├── .gitignore
├── LICENSE               # Licencia MIT
├── README.md             # Documentación oficial
├── CHANGELOG.md          # Registro de cambios SemVer (v1.0.0 & v1.1.0)
└── requirements.txt      # Dependencias del proyecto
```

---

## 5. Instalación

### Requisitos Previos
- Python 3.11 o superior.

### Pasos de Instalación
```bash
# 1. Clonar el repositorio
git clone https://github.com/pameeesd/JRBStore.git
cd JRBStore

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar migraciones de base de datos
python src/manage.py migrate

# 4. Ejecutar pruebas unitarias
python src/manage.py test tests

# 5. Iniciar el servidor de desarrollo
python src/manage.py runserver
```

Navega a `http://127.0.0.1:8000/` en tu navegador.

#### Credenciales Administrador por Defecto:
- **Usuario**: `admin`
- **Contraseña**: `admin1234`

---

## 6. Capturas

*(Vista principal del catálogo, carrito de compras y panel de administración)*.

---

## 7. Roadmap

- [x] v1.0.0: Estructuración PEP, base de datos local SQLite y carrito basado en sesiones.
- [x] v1.1.0: Descuento automático de stock, buscador de productos, filtro por categorías y suite de tests.
- [ ] v2.0.0: Pasarela de pagos en línea (Webpay / Stripe) e integración de REST API.

---

## 8. Estado

**v1.1.0 - Production Ready** 🚀  
El sistema se encuentra estable, probado y listo para su despliegue o publicación.

---

## 9. Licencia

Este proyecto está liberado bajo la Licencia MIT. Consulte el archivo [LICENSE](LICENSE) para más información.
