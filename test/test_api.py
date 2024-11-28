import pytest
from fastapi.testclient import TestClient
import sys
import os

# Agregar el directorio padre al path para importar la aplicación principal
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar la aplicación principal
from main import app, Item, data_manager

# Crear un cliente de pruebas
client = TestClient(app)

# Fixture para limpiar los datos antes de cada prueba
@pytest.fixture(autouse=True)
def limpiar_datos():
    """Limpiar el archivo de datos antes de cada prueba"""
    data_manager.write_data([])

def test_crear_item():
    """Prueba crear un nuevo item"""
    nuevo_item = {
        "nombre": "Producto de Prueba",
        "descripcion": "Un item para testing",
        "precio": 99.99,
        "categoria": "Test"
    }
    
    # Crear item
    response = client.post("/items/", json=nuevo_item)
    
    # Verificaciones
    assert response.status_code == 201
    datos_respuesta = response.json()
    
    assert datos_respuesta["nombre"] == nuevo_item["nombre"]
    assert datos_respuesta["descripcion"] == nuevo_item["descripcion"]
    assert datos_respuesta["precio"] == nuevo_item["precio"]
    assert datos_respuesta["categoria"] == nuevo_item["categoria"]
    assert "id" in datos_respuesta

def test_crear_item_duplicado():
    """Prueba crear un item con nombre duplicado"""
    item_base = {
        "nombre": "Producto Único",
        "descripcion": "Item de prueba",
        "precio": 50.00,
        "categoria": "Test"
    }
    
    # Crear primer item
    response1 = client.post("/items/", json=item_base)
    assert response1.status_code == 201
    
    # Intentar crear item con el mismo nombre
    response2 = client.post("/items/", json=item_base)
    assert response2.status_code == 400
    assert "Ya existe un item" in response2.json()["detail"]

def test_listar_items():
    """Prueba listar items"""
    # Crear algunos items de prueba
    items_prueba = [
        {
            "nombre": f"Producto {i}",
            "descripcion": f"Descripción {i}",
            "precio": 10.0 * i,
            "categoria": "Test" if i % 2 == 0 else "Otra"
        } for i in range(5)
    ]
    
    # Crear items
    for item in items_prueba:
        client.post("/items/", json=item)
    
    # Listar todos los items
    response = client.get("/items/")
    assert response.status_code == 200
    
    items_respuesta = response.json()
    assert len(items_respuesta) == 5
    
    # Probar filtrado por categoría
    response_filtrado = client.get("/items/?categoria=Test")
    items_filtrados = response_filtrado.json()
    assert len(items_filtrados) == 3  # Items con categoría "Test"

def test_obtener_item():
    """Prueba obtener un item específico"""
    # Crear un item
    nuevo_item = {
        "nombre": "Item para Búsqueda",
        "descripcion": "Item específico",
        "precio": 75.50,
        "categoria": "Especial"
    }
    
    # Crear item y obtener su ID
    response_crear = client.post("/items/", json=nuevo_item)
    item_creado = response_crear.json()
    item_id = item_creado["id"]
    
    # Obtener item por ID
    response_obtener = client.get(f"/items/{item_id}")
    assert response_obtener.status_code == 200
    
    item_obtenido = response_obtener.json()
    assert item_obtenido["id"] == item_id
    assert item_obtenido["nombre"] == nuevo_item["nombre"]

def test_actualizar_item():
    """Prueba actualizar un item existente"""
    # Crear un item inicial
    item_original = {
        "nombre": "Item Original",
        "descripcion": "Descripción inicial",
        "precio": 100.00,
        "categoria": "Inicial"
    }
    
    # Crear item y obtener su ID
    response_crear = client.post("/items/", json=item_original)
    item_creado = response_crear.json()
    item_id = item_creado["id"]
    
    # Datos para actualizar
    item_actualizado = {
        "nombre": "Item Actualizado",
        "descripcion": "Nueva descripción",
        "precio": 150.00,
        "categoria": "Actualizado"
    }
    
    # Actualizar item
    response_actualizar = client.put(f"/items/{item_id}", json=item_actualizado)
    assert response_actualizar.status_code == 200
    
    item_modificado = response_actualizar.json()
    assert item_modificado["id"] == item_id
    assert item_modificado["nombre"] == item_actualizado["nombre"]
    assert item_modificado["descripcion"] == item_actualizado["descripcion"]
    assert item_modificado["precio"] == item_actualizado["precio"]
    assert item_modificado["categoria"] == item_actualizado["categoria"]

def test_eliminar_item():
    """Prueba eliminar un item"""
    # Crear un item para eliminar
    item_a_eliminar = {
        "nombre": "Item para Eliminar",
        "descripcion": "Item que será borrado",
        "precio": 25.75,
        "categoria": "Temporal"
    }
    
    # Crear item y obtener su ID
    response_crear = client.post("/items/", json=item_a_eliminar)
    item_creado = response_crear.json()
    item_id = item_creado["id"]
    
    # Eliminar item
    response_eliminar = client.delete(f"/items/{item_id}")
    assert response_eliminar.status_code == 204
    
    # Intentar obtener item eliminado
    response_obtener = client.get(f"/items/{item_id}")
    assert response_obtener.status_code == 404

def test_item_no_encontrado():
    """Prueba operaciones con item inexistente"""
    # ID de item que no existe
    id_inexistente = "item-no-existente"
    
    # Intentar obtener item
    response_obtener = client.get(f"/items/{id_inexistente}")
    assert response_obtener.status_code == 404
    
    # Intentar actualizar item
    response_actualizar = client.put(f"/items/{id_inexistente}", json={
        "nombre": "Item Fantasma",
        "precio": 999.99,
        "descripcion": "No debería existir"
    })
    assert response_actualizar.status_code == 404
    
    # Intentar eliminar item
    response_eliminar = client.delete(f"/items/{id_inexistente}")
    assert response_eliminar.status_code == 404

# Validaciones adicionales
def test_validaciones_entrada():
    """Prueba validaciones de entrada"""
    # Item con nombre muy corto
    item_invalido = {
        "nombre": "A",  # Menos de 2 caracteres
        "precio": 10.00,
        "descripcion": "Item inválido"
    }
    
    response = client.post("/items/", json=item_invalido)
    assert response.status_code == 422  # Error de validación

    # Item con precio negativo
    item_precio_negativo = {
        "nombre": "ProductoInvalido",
        "precio": -50.00,
        "descripcion": "Precio negativo"
    }
    
    response = client.post("/items/", json=item_precio_negativo)
    assert response.status_code == 422  # Error de validación