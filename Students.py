# Importaciones necesarias
from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
import json
import os
from uuid import uuid4

# Modelo de datos para los elementos
class Item(BaseModel):
    """
    Modelo de datos para representar un elemento en la API.
    Utiliza Pydantic para validación de datos.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    nombre: str = Field(..., min_length=2, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=200)
    precio: float = Field(..., gt=0)
    categoria: Optional[str] = None

# Clase para manejar operaciones con archivo JSON
class JSONDataManager:
    """
    Clase para gestionar operaciones de lectura y escritura 
    en archivo JSON de forma segura.
    """
    def __init__(self, filename='data.json'):
        self.filename = filename
        # Crear archivo si no existe
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                json.dump([], f)

    def read_data(self) -> List[dict]:
        """Leer datos del archivo JSON."""
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def write_data(self, data: List[dict]):
        """Escribir datos en el archivo JSON."""
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=2)

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="API de Gestión de Elementos",
    description="API CRUD para manejo de elementos con almacenamiento en JSON",
    version="1.0.0"
)

# Inicializar gestor de datos
data_manager = JSONDataManager()

# Endpoints CRUD

@app.post("/items/", response_model=Item, status_code=201)
async def crear_item(item: Item):
    """
    Crear un nuevo item
    - Genera un ID único
    - Valida los datos de entrada
    - Guarda en el archivo JSON
    """
    items = data_manager.read_data()
    
    # Verificar si ya existe un item con el mismo nombre
    if any(existing_item['nombre'] == item.nombre for existing_item in items):
        raise HTTPException(status_code=400, detail="Ya existe un item con este nombre")
    
    # Convertir el item a diccionario
    item_dict = item.model_dump()
    items.append(item_dict)
    
    # Guardar en archivo
    data_manager.write_data(items)
    
    return item

@app.get("/items/", response_model=List[Item])
async def listar_items(
    categoria: Optional[str] = Query(None, description="Filtrar por categoría"),
    limite: Optional[int] = Query(None, gt=0, le=100, description="Límite de items a retornar")
):
    """
    Listar todos los items con opciones de filtrado
    - Filtrado opcional por categoría
    - Límite opcional de resultados
    """
    items = data_manager.read_data()
    
    # Aplicar filtros si están presentes
    if categoria:
        items = [item for item in items if item['categoria'] == categoria]
    
    if limite:
        items = items[:limite]
    
    return items

@app.get("/items/{item_id}", response_model=Item)
async def obtener_item(
    item_id: str = Path(..., description="ID del item a buscar")
):
    """
    Obtener un item específico por su ID
    - Lanza excepción si no se encuentra
    """
    items = data_manager.read_data()
    
    item = next((item for item in items if item['id'] == item_id), None)
    
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    
    return item

@app.put("/items/{item_id}", response_model=Item)
async def actualizar_item(
    item_id: str = Path(..., description="ID del item a actualizar"),
    item_actualizado: Item = None
):
    """
    Actualizar un item existente
    - Valida la existencia del item
    - Actualiza todos los campos
    """
    items = data_manager.read_data()
    
    # Encontrar el índice del item
    item_index = next((index for (index, item) in enumerate(items) if item['id'] == item_id), None)
    
    if item_index is None:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    
    # Mantener el ID original
    item_actualizado.id = item_id
    
    # Convertir a diccionario
    item_dict = item_actualizado.model_dump()
    
    # Reemplazar el item
    items[item_index] = item_dict
    
    # Guardar cambios
    data_manager.write_data(items)
    
    return item_actualizado

@app.delete("/items/{item_id}", status_code=204)
async def eliminar_item(
    item_id: str = Path(..., description="ID del item a eliminar")
):
    """
    Eliminar un item por su ID
    - Valida la existencia del item
    - Elimina de forma segura
    """
    items = data_manager.read_data()
    
    # Encontrar el índice del item
    item_index = next((index for (index, item) in enumerate(items) if item['id'] == item_id), None)
    
    if item_index is None:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    
    # Eliminar item
    del items[item_index]
    
    # Guardar cambios
    data_manager.write_data(items)

# Configuración para ejecutar la aplicación
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)