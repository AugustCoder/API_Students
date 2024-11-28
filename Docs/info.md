# API de Gestión de Elementos con FastAPI

### Requisitos Previos

- Python 3.8+
- pip
- venv (incluido en Python estándar)

## Instalación

Clonar el repositorio

```python
bashCopygit clone <url-del-repositorio>
cd <nombre-del-proyecto>
```

Ejecutar script de instalación

```python
bashCopypython install.py
```

### Endpoints

- POST /items/: Crear un nuevo item
- GET /items/: Listar items (con filtros opcionales)
- GET /items/{item_id}: Obtener un item específico
- PUT /items/{item_id}: Actualizar un item
- DELETE /items/{item_id}: Eliminar un item