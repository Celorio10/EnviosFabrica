from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import jwt
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import bcrypt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT configuration
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security
security = HTTPBearer()

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Predefined users
USERS = {
    "Marco": "B33388091",
    "Mariano": "B33388091", 
    "Jesus": "B33388091",
    "Diego": "B33388091",
    "admin": "ASCb33388091_"
}

# Models
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str

class Client(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nombre: str
    cif: str
    telefono: str
    email: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ClientCreate(BaseModel):
    nombre: str
    cif: str
    telefono: str
    email: Optional[str] = None

class Equipment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    orden_trabajo: str
    cliente_id: str
    cliente_nombre: str
    tipo_equipo: str
    modelo: str
    ato: Optional[str] = None
    fabricante: str
    numero_serie: str
    fecha_fabricacion: Optional[datetime] = None
    tipo_fallo: str
    observaciones: Optional[str] = None
    numero_serie_sensor: Optional[str] = None
    fecha_instalacion_sensor: Optional[datetime] = None
    estado: str = "Pendiente"  # Pendiente, Enviado, En Fabricante, Recibido
    numero_orden_compra: Optional[str] = None
    numero_recepcion_fabricante: Optional[str] = None
    en_garantia: Optional[bool] = None
    numero_presupuesto: Optional[str] = None
    presupuesto_aceptado: Optional[bool] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class EquipmentCreate(BaseModel):
    orden_trabajo: str
    cliente_id: str
    cliente_nombre: str
    tipo_equipo: str
    modelo: str
    ato: Optional[str] = None
    fabricante: str
    numero_serie: str
    fecha_fabricacion: Optional[str] = None  # Changed to string to handle empty dates
    tipo_fallo: str
    observaciones: Optional[str] = None
    numero_serie_sensor: Optional[str] = None
    fecha_instalacion_sensor: Optional[str] = None  # Changed to string to handle empty dates

class Manufacturer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nombre: str

class Model(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nombre: str
    tipo_equipo: str

class FaultType(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nombre: str
    requiere_sensor: bool = False

class PurchaseOrder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    numero_orden: str
    equipments: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AssignPurchaseOrderRequest(BaseModel):
    numero_orden: str
    equipment_ids: List[str]

class ManufacturerResponseRequest(BaseModel):
    equipment_ids: List[str]
    numero_recepcion_fabricante: str
    en_garantia: bool
    numero_presupuesto: Optional[str] = None
    presupuesto_aceptado: Optional[bool] = None

class ReceiveEquipmentRequest(BaseModel):
    equipment_ids: List[str]

# JWT functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return User(username=username)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# Authentication routes
@api_router.post("/auth/login", response_model=Token)
async def login(request: LoginRequest):
    if request.username not in USERS or USERS[request.username] != request.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": request.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.get("/auth/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Client routes
@api_router.post("/clientes", response_model=Client)
async def create_client(client: ClientCreate, current_user: User = Depends(get_current_user)):
    client_dict = client.dict()
    client_obj = Client(**client_dict)
    await db.clients.insert_one(client_obj.dict())
    return client_obj

@api_router.get("/clientes", response_model=List[Client])
async def get_clients(current_user: User = Depends(get_current_user)):
    clients = await db.clients.find().to_list(1000)
    return [Client(**client) for client in clients]

# Equipment routes
@api_router.post("/equipos", response_model=Equipment)
async def create_equipment(equipment: EquipmentCreate, current_user: User = Depends(get_current_user)):
    equipment_dict = equipment.dict()
    
    # Convert date strings to datetime objects or None
    if equipment_dict.get('fecha_fabricacion'):
        try:
            equipment_dict['fecha_fabricacion'] = datetime.fromisoformat(equipment_dict['fecha_fabricacion'].replace('Z', '+00:00'))
        except:
            equipment_dict['fecha_fabricacion'] = None
    else:
        equipment_dict['fecha_fabricacion'] = None
    
    if equipment_dict.get('fecha_instalacion_sensor'):
        try:
            equipment_dict['fecha_instalacion_sensor'] = datetime.fromisoformat(equipment_dict['fecha_instalacion_sensor'].replace('Z', '+00:00'))
        except:
            equipment_dict['fecha_instalacion_sensor'] = None
    else:
        equipment_dict['fecha_instalacion_sensor'] = None
    
    # Handle empty strings as None for optional fields
    for field in ['ato', 'observaciones', 'numero_serie_sensor']:
        if equipment_dict.get(field) == '':
            equipment_dict[field] = None
    
    equipment_obj = Equipment(**equipment_dict)
    await db.equipment.insert_one(equipment_obj.dict())
    return equipment_obj

@api_router.get("/equipos", response_model=List[Equipment])
async def get_equipment(current_user: User = Depends(get_current_user)):
    equipment = await db.equipment.find().to_list(1000)
    return [Equipment(**eq) for eq in equipment]

@api_router.get("/equipos/pendientes", response_model=List[Equipment])
async def get_pending_equipment(current_user: User = Depends(get_current_user)):
    equipment = await db.equipment.find({"estado": "Pendiente"}).to_list(1000)
    return [Equipment(**eq) for eq in equipment]

@api_router.get("/equipos/para-recepcion", response_model=List[Equipment])
async def get_equipment_for_reception(current_user: User = Depends(get_current_user)):
    # Equipment that has warranty or budget and is ready for reception
    equipment = await db.equipment.find({
        "estado": "En Fabricante",
        "$or": [
            {"en_garantia": True},
            {"numero_presupuesto": {"$ne": None}}
        ]
    }).to_list(1000)
    return [Equipment(**eq) for eq in equipment]

@api_router.get("/equipos/completados", response_model=List[Equipment])
async def get_completed_equipment(current_user: User = Depends(get_current_user)):
    equipment = await db.equipment.find({"estado": "Recibido"}).to_list(1000)
    return [Equipment(**eq) for eq in equipment]

@api_router.get("/equipos/{equipment_id}", response_model=Equipment)
async def get_equipment_by_id(equipment_id: str, current_user: User = Depends(get_current_user)):
    equipment = await db.equipment.find_one({"id": equipment_id})
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    return Equipment(**equipment)

@api_router.put("/equipos/{equipment_id}", response_model=Equipment)
async def update_equipment(equipment_id: str, updates: dict, current_user: User = Depends(get_current_user)):
    updates["updated_at"] = datetime.utcnow()
    result = await db.equipment.update_one({"id": equipment_id}, {"$set": updates})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    
    equipment = await db.equipment.find_one({"id": equipment_id})
    return Equipment(**equipment)

# Reference data routes
@api_router.get("/fabricantes", response_model=List[Manufacturer])
async def get_manufacturers(current_user: User = Depends(get_current_user)):
    manufacturers = await db.manufacturers.find().to_list(1000)
    return [Manufacturer(**mf) for mf in manufacturers]

@api_router.post("/fabricantes", response_model=Manufacturer)
async def create_manufacturer(name: str, current_user: User = Depends(get_current_user)):
    manufacturer = Manufacturer(nombre=name)
    await db.manufacturers.insert_one(manufacturer.dict())
    return manufacturer

@api_router.get("/modelos", response_model=List[Model])
async def get_models(current_user: User = Depends(get_current_user)):
    models = await db.models.find().to_list(1000)
    return [Model(**model) for model in models]

@api_router.post("/modelos", response_model=Model)
async def create_model(name: str, equipment_type: str, current_user: User = Depends(get_current_user)):
    model = Model(nombre=name, tipo_equipo=equipment_type)
    await db.models.insert_one(model.dict())
    return model

@api_router.get("/tipos-fallo", response_model=List[FaultType])
async def get_fault_types(current_user: User = Depends(get_current_user)):
    fault_types = await db.fault_types.find().to_list(1000)
    if not fault_types:
        # Initialize default fault types
        default_fault_types = [
            FaultType(nombre="SENSOR LEAKING ACID, PCB DAMAGED", requiere_sensor=True),
            FaultType(nombre="SENSOR FAILURE", requiere_sensor=True),
            FaultType(nombre="AIR LEAK", requiere_sensor=False),
            FaultType(nombre="LOW SOUND", requiere_sensor=False),
            FaultType(nombre="OTHER", requiere_sensor=False)
        ]
        for ft in default_fault_types:
            await db.fault_types.insert_one(ft.dict())
        return default_fault_types
    return [FaultType(**ft) for ft in fault_types]

@api_router.post("/tipos-fallo", response_model=FaultType)
async def create_fault_type(name: str, requires_sensor: bool = False, current_user: User = Depends(get_current_user)):
    fault_type = FaultType(nombre=name, requiere_sensor=requires_sensor)
    await db.fault_types.insert_one(fault_type.dict())
    return fault_type

# Purchase order routes
@api_router.get("/ordenes-compra", response_model=List[PurchaseOrder])
async def get_purchase_orders(current_user: User = Depends(get_current_user)):
    orders = await db.purchase_orders.find().to_list(1000)
    return [PurchaseOrder(**order) for order in orders]

@api_router.get("/ordenes-compra/activas")
async def get_active_purchase_orders(current_user: User = Depends(get_current_user)):
    # Get purchase orders that have equipment in "Enviado" state
    equipment_with_po = await db.equipment.find(
        {"estado": "Enviado", "numero_orden_compra": {"$ne": None}}
    ).to_list(1000)
    
    active_pos = list(set([eq["numero_orden_compra"] for eq in equipment_with_po]))
    return {"active_orders": active_pos}

@api_router.get("/ordenes-compra/{order_number}/equipos", response_model=List[Equipment])
async def get_equipment_by_purchase_order(order_number: str, current_user: User = Depends(get_current_user)):
    equipment = await db.equipment.find({"numero_orden_compra": order_number}).to_list(1000)
    return [Equipment(**eq) for eq in equipment]

@api_router.get("/ordenes-compra/{order_number}/equipos/enviados", response_model=List[Equipment])
async def get_sent_equipment_by_purchase_order(order_number: str, current_user: User = Depends(get_current_user)):
    # Only equipment that is still in "Enviado" state (not processed by manufacturer yet)
    equipment = await db.equipment.find({
        "numero_orden_compra": order_number, 
        "estado": "Enviado"
    }).to_list(1000)
    return [Equipment(**eq) for eq in equipment]

@api_router.post("/ordenes-compra/asignar")
async def assign_purchase_order(request: AssignPurchaseOrderRequest, current_user: User = Depends(get_current_user)):
    # Create or update purchase order
    existing_order = await db.purchase_orders.find_one({"numero_orden": request.numero_orden})
    if existing_order:
        await db.purchase_orders.update_one(
            {"numero_orden": request.numero_orden},
            {"$addToSet": {"equipments": {"$each": request.equipment_ids}}}
        )
    else:
        order = PurchaseOrder(numero_orden=request.numero_orden, equipments=request.equipment_ids)
        await db.purchase_orders.insert_one(order.dict())
    
    # Update equipment status
    await db.equipment.update_many(
        {"id": {"$in": request.equipment_ids}},
        {"$set": {
            "numero_orden_compra": request.numero_orden, 
            "estado": "Enviado", 
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {"message": "Orden de compra asignada correctamente", "assigned_count": len(request.equipment_ids)}

@api_router.post("/ordenes-compra/{order_number}/respuesta-fabricante")
async def manufacturer_response(order_number: str, request: ManufacturerResponseRequest, current_user: User = Depends(get_current_user)):
    # Update selected equipment with manufacturer response
    updates = {
        "numero_recepcion_fabricante": request.numero_recepcion_fabricante,
        "en_garantia": request.en_garantia,
        "estado": "En Fabricante",
        "updated_at": datetime.utcnow()
    }
    
    if not request.en_garantia:
        updates["numero_presupuesto"] = request.numero_presupuesto
        updates["presupuesto_aceptado"] = request.presupuesto_aceptado
    
    result = await db.equipment.update_many(
        {"id": {"$in": request.equipment_ids}, "numero_orden_compra": order_number},
        {"$set": updates}
    )
    
    return {
        "message": "Respuesta de fabricante registrada correctamente", 
        "updated_count": result.modified_count
    }

@api_router.post("/equipos/recibir")
async def receive_equipment(request: ReceiveEquipmentRequest, current_user: User = Depends(get_current_user)):
    # Mark equipment as received
    result = await db.equipment.update_many(
        {"id": {"$in": request.equipment_ids}},
        {"$set": {
            "estado": "Recibido",
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {
        "message": "Equipos marcados como recibidos correctamente",
        "received_count": result.modified_count
    }

# Database cleanup endpoint (for development/testing)
@api_router.post("/admin/clear-database")
async def clear_database(current_user: User = Depends(get_current_user)):
    if current_user.username != "admin":
        raise HTTPException(status_code=403, detail="Solo el administrador puede limpiar la base de datos")
    
    try:
        # Get all collection names
        collection_names = await db.list_collection_names()
        
        # Clear all collections
        cleared_collections = []
        for collection_name in collection_names:
            result = await db[collection_name].delete_many({})
            cleared_collections.append({
                "collection": collection_name,
                "deleted_count": result.deleted_count
            })
        
        return {
            "message": "Base de datos limpiada exitosamente",
            "collections_cleared": cleared_collections,
            "total_collections": len(collection_names)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al limpiar la base de datos: {str(e)}")

# CSV Export endpoint
@api_router.get("/ordenes-compra/{order_number}/export-csv")
async def export_purchase_order_csv(order_number: str, current_user: User = Depends(get_current_user)):
    equipment = await db.equipment.find({"numero_orden_compra": order_number}).to_list(1000)
    
    if not equipment:
        raise HTTPException(status_code=404, detail="No se encontraron equipos para esta orden de compra")
    
    # Generate CSV content
    csv_header = "Orden de Trabajo,Cliente,Tipo de Equipo,Modelo,Fabricante,Numero de Serie,Estado,Fecha Creacion\n"
    csv_rows = []
    
    for eq in equipment:
        row = f"{eq['orden_trabajo']},{eq['cliente_nombre']},{eq['tipo_equipo']},{eq['modelo']},{eq['fabricante']},{eq['numero_serie']},{eq['estado']},{eq['created_at'].strftime('%Y-%m-%d')}\n"
        csv_rows.append(row)
    
    csv_content = csv_header + "".join(csv_rows)
    
    return {
        "filename": f"orden_compra_{order_number}.csv",
        "content": csv_content,
        "equipment_count": len(equipment)
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()