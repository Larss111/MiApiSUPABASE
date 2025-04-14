from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncpg
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL")
print("DATABASE_URL =", DATABASE_URL)
conn = None

# Modelo 
class Producto(BaseModel):
    nombre: str
    descripcion: str
    stock: int
    costo: float
    precio: float

# Conexión 
@app.on_event("startup")
async def startup():
    global conn
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        print("Conectado a la base de datos")
    except Exception as e:
        print("Error al conectar a la base de datos:", e)

# Cierre de conexión 
@app.on_event("shutdown")
async def shutdown():
    await conn.close()
    print("🔒 Conexión cerrada")

# Endpoint de prueba 
@app.get("/")
async def root():
    return {"message": "FastAPI está funcionando con Supabase"}

#GET
@app.get("/productos")
async def listar_productos():
    if not conn:
        raise HTTPException(status_code=500, detail="Conexión no establecida")
    rows = await conn.fetch("SELECT * FROM producto")
    return [dict(row) for row in rows]


# POST 
@app.post("/productos")
async def agregar_producto(producto: Producto):
    if not conn:
        raise HTTPException(status_code=500, detail="Conexión no establecida")
    await conn.execute(
        "INSERT INTO producto (nombre, descripcion, stock, costo, precio) VALUES ($1, $2, $3, $4, $5)",
        producto.nombre, producto.descripcion, producto.stock, producto.costo, producto.precio
    )
    return {"mensaje": "Producto agregado"}

# PUT 
@app.put("/productos/{id}")
async def actualizar_producto(id: int, producto: Producto):
    if not conn:
        raise HTTPException(status_code=500, detail="Conexión no establecida")
    await conn.execute(
        "UPDATE producto SET nombre=$1, descripcion=$2, stock=$3, costo=$4, precio=$5 WHERE id=$6",
        producto.nombre, producto.descripcion, producto.stock, producto.costo, producto.precio, id
    )
    return {"mensaje": "Producto actualizado"}


# DELETE 
@app.delete("/productos/{id}")
async def eliminar_producto(id: int):
    if not conn:
        raise HTTPException(status_code=500, detail="Conexión no establecida")
    await conn.execute("DELETE FROM producto WHERE id=$1", id)
    return {"mensaje": "Producto eliminado"}