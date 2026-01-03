# Sistema de Gestión de Reservas Hoteleras (SOA)

Este proyecto implementa una arquitectura SOA con FastAPI para gestionar reservas hoteleras: autenticación, clientes, disponibilidad, tarifas, pagos (simulado), reservas y notificaciones.
## Servicios

- Auth Service (puerto 8000)
- Customers Service (puerto 8001)
- Availability Service (puerto 8002)
- Pricing Service (puerto 8003)
- Payments Service (puerto 8004)
- Reservations Service (puerto 8005)
- Notifications Service (puerto 8006)

Cada servicio expone Swagger/OpenAPI automáticamente en `/docs` y `/openapi.json`.
## Requisitos

- Python 3.11+
- Docker y Docker Compose

## Configuración rápida

1. Crear archivo `.env` basado en `.env.example`.
2. Construir y levantar con Docker Compose:

```bash
docker compose up -d --build
```

3. Acceder a Swagger de cada servicio:
  - Auth: http://localhost:8000/docs
  - Customers: http://localhost:8001/docs
  - Availability: http://localhost:8002/docs
  - Pricing: http://localhost:8003/docs
  - Payments: http://localhost:8004/docs
  - Reservations: http://localhost:8005/docs
  - Notifications: http://localhost:8006/docs

## Estructura

Ver especificación detallada en el PR y en este repositorio. Los módulos compartidos se encuentran en `shared/` y son incluidos en las imágenes de cada servicio usando el contexto raíz en Docker.

## Desarrollo local (opcional)

Instalar dependencias:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Ejecutar un servicio (ejemplo Auth):

```bash
uvicorn services.auth.main:app --reload --port 8000
```

## Tests

```bash
pytest -q
```

## Notas

- Configuración de DB via variables de entorno, usando MySQL 8.
- Seguridad JWT centralizada en `shared/security.py`.
- Event Bus mejorado en `shared/events.py`.
# PROYECTO: Sistema de Gestión de Reservas Hoteleras - Arquitectura SOA

Eres un arquitecto de software experto en SOA (Service-Oriented Architecture) y desarrollo con Python/FastAPI. Tu tarea es implementar un sistema completo de gestión de reservas hoteleras siguiendo los diseños y especificaciones proporcionados.

## 📋 CONTEXTO DEL PROYECTO

Sistema empresarial para cadena hotelera que gestiona reservas, pagos, disponibilidad, clientes y notificaciones mediante arquitectura SOA con servicios independientes y comunicación orientada a eventos.

## 🎯 OBJETIVOS

Implementar los 6 servicios core del sistema con:
- ✅ API REST completa con FastAPI y documentación OpenAPI
- ✅ Persistencia en MySQL con SQLAlchemy
- ✅ Sistema de eventos para comunicación asíncrona
- ✅ Autenticación JWT centralizada
- ✅ Validaciones robustas con Pydantic
- ✅ Pruebas unitarias, integración y rendimiento con Pytest
- ✅ Dockerización de todos los servicios

## 🏗️ ARQUITECTURA DEL SISTEMA

### Servicios a Implementar (Prioridad)

1. **Servicio de Autenticación (Auth Service)** - NUEVO ⭐
   - Gestión de usuarios y roles
   - Generación y validación de tokens JWT
   - Endpoints: registro, login, refresh token, logout

2. **Servicio de Clientes (Customer Service)** - NUEVO ⭐
   - CRUD de perfiles de clientes
   - Historial de reservas del cliente
   - Endpoints: crear, obtener, actualizar, listar clientes

3. **Servicio de Disponibilidad (Availability Service)** - NUEVO ⭐
   - Consultar disponibilidad de habitaciones
   - Bloqueo temporal (15 min) durante reserva
   - Liberar/confirmar bloqueos
   - Endpoints: consultar, bloquear, liberar, confirmar

4. **Servicio de Tarifas (Pricing Service)** - NUEVO ⭐
   - Cálculo de precios dinámicos
   - Aplicación de descuentos y promociones
   - Validación de cupones
   - Endpoints: calcular precio, validar cupón

5. **Servicio de Pagos (Payment Service)** - NUEVO ⭐ (SIMULADO)
   - Procesamiento simulado de pagos
   - Aprobación/rechazo aleatorio con reglas
   - Gestión de reembolsos simulados
   - Endpoints: procesar pago, reembolsar, consultar transacción

6. **Servicio de Reservas (Reservation Service)** - MEJORAR ✨
   - CRUD completo de reservas
   - Orquestación de otros servicios
   - Gestión de políticas de cancelación
   - Endpoints: crear, obtener, listar, modificar, cancelar

7. **Servicio de Notificaciones (Notification Service)** - MEJORAR ✨
   - Sistema orientado a eventos
   - Envío simulado de emails
   - Suscripción a eventos: reserva.creada, reserva.cancelada, pago.aprobado, pago.rechazado

## 📐 ESTRUCTURA DEL PROYECTO
```
hotel-reservations-soa/
│
├── services/
│   ├── auth/                    # 🆕 Servicio de Autenticación
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app
│   │   ├── models.py           # Modelos SQLAlchemy (Usuario, Role)
│   │   ├── schemas.py          # Schemas Pydantic
│   │   ├── service.py          # Lógica de negocio
│   │   ├── repository.py       # Acceso a datos
│   │   ├── security.py         # JWT utilities
│   │   ├── config.py
│   │   └── Dockerfile
│   │
│   ├── customers/               # 🆕 Servicio de Clientes
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py           # Modelo Cliente
│   │   ├── schemas.py
│   │   ├── service.py
│   │   ├── repository.py
│   │   ├── config.py
│   │   └── Dockerfile
│   │
│   ├── availability/            # 🆕 Servicio de Disponibilidad
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py           # Modelos: Habitacion, Bloqueo
│   │   ├── schemas.py
│   │   ├── service.py
│   │   ├── repository.py
│   │   ├── config.py
│   │   └── Dockerfile
│   │
│   ├── pricing/                 # 🆕 Servicio de Tarifas
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py           # Modelos: Tarifa, Promocion
│   │   ├── schemas.py
│   │   ├── service.py
│   │   ├── rules_engine.py     # Motor de reglas de pricing
│   │   ├── config.py
│   │   └── Dockerfile
│   │
│   ├── payments/                # 🆕 Servicio de Pagos (SIMULADO)
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py           # Modelo Transaccion
│   │   ├── schemas.py
│   │   ├── service.py
│   │   ├── simulator.py        # Simulador de gateway de pagos
│   │   ├── config.py
│   │   └── Dockerfile
│   │
│   ├── reservations/            # ✨ MEJORAR EXISTENTE
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── service.py          # Agregar orquestación completa
│   │   ├── repository.py
│   │   ├── orchestrator.py     # 🆕 Orquestador de creación de reserva
│   │   ├── events.py
│   │   ├── config.py
│   │   └── Dockerfile
│   │
│   └── notifications/           # ✨ MEJORAR EXISTENTE
│       ├── __init__.py
│       ├── main.py
│       ├── service.py          # Expandir con más eventos
│       ├── templates/          # 🆕 Templates de emails
│       ├── config.py
│       └── Dockerfile
│
├── shared/                      # Código compartido
│   ├── __init__.py
│   ├── database.py             # Configuración MySQL
│   ├── events.py               # Event Bus mejorado
│   ├── exceptions.py           # Excepciones personalizadas
│   ├── security.py             # Middleware JWT
│   └── http_client.py          # 🆕 Cliente HTTP para comunicación inter-servicios
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Fixtures compartidos
│   ├── test_auth.py            # 🆕
│   ├── test_customers.py       # 🆕
│   ├── test_availability.py   # 🆕
│   ├── test_pricing.py         # 🆕
│   ├── test_payments.py        # 🆕
│   ├── test_reservations.py   # Expandir
│   ├── test_notifications.py  # Expandir
│   ├── test_integration.py    # Tests de flujo completo
│   └── test_performance.py    # Tests de carga
│
├── docker-compose.yml          # Orquestación de servicios
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🔧 ESPECIFICACIONES TÉCNICAS

### Stack Tecnológico
- **Python**: 3.11+
- **Framework**: FastAPI 0.104+
- **Base de Datos**: MySQL 8.0
- **ORM**: SQLAlchemy 2.0+
- **Validación**: Pydantic 2.5+
- **Testing**: Pytest 7.4+
- **Servidor**: Uvicorn
- **Contenedores**: Docker + Docker Compose

### Dependencias Principales (requirements.txt)
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
sqlalchemy==2.0.23
pymysql==1.1.0
python-dotenv==1.0.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
httpx==0.25.0
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
```

## 📝 ESPECIFICACIONES DETALLADAS POR SERVICIO

### 1. SERVICIO DE AUTENTICACIÓN (Auth Service)

**Puerto**: 8000

**Base de Datos**: Tabla `usuarios`, `roles`

**Modelo Usuario (SQLAlchemy)**:
```python
class UsuarioDB(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(String(50), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    username = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    nombre_completo = Column(String(255))
    telefono = Column(String(20), nullable=True)
    rol = Column(Enum('admin', 'staff', 'cliente'), default='cliente')
    activo = Column(Boolean, default=True)
    creado_en = Column(DateTime, server_default=func.now())
    ultimo_login = Column(DateTime, nullable=True)
```

**Endpoints Requeridos**:
```python
POST   /api/v1/auth/register          # Registrar nuevo usuario
POST   /api/v1/auth/login             # Login (retorna access + refresh token)
POST   /api/v1/auth/refresh           # Refrescar access token
POST   /api/v1/auth/logout            # Logout (invalidar token)
GET    /api/v1/auth/me                # Obtener info del usuario actual
PUT    /api/v1/auth/me                # Actualizar perfil
GET    /health                        # Health check
```

**Schemas Pydantic**:
```python
class RegistroRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)
    nombre_completo: str
    telefono: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UsuarioResponse(BaseModel):
    usuario_id: str
    email: str
    username: str
    nombre_completo: str
    rol: str
    activo: bool
```

**Seguridad JWT**:
- Secret key: Variable de entorno `JWT_SECRET_KEY`
- Algoritmo: HS256
- Access token expira en: 30 minutos
- Refresh token expira en: 7 días
- Incluir en payload: `usuario_id`, `username`, `rol`, `exp`, `iat`

**Reglas de Negocio**:
- Password debe tener mínimo 8 caracteres, 1 mayúscula, 1 número
- Email debe ser único
- Username debe ser único
- Por defecto, usuarios nuevos tienen rol "cliente"
- Hash passwords con bcrypt (passlib)

---

### 2. SERVICIO DE CLIENTES (Customer Service)

**Puerto**: 8001

**Base de Datos**: Tabla `clientes`

**Modelo Cliente (SQLAlchemy)**:
```python
class ClienteDB(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(String(50), unique=True, index=True)
    usuario_id = Column(String(50), index=True, nullable=True)  # Relación con Auth
    nombre_completo = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    telefono = Column(String(20))
    fecha_nacimiento = Column(Date, nullable=True)
    direccion = Column(String(500), nullable=True)
    ciudad = Column(String(100), nullable=True)
    pais = Column(String(100), nullable=True)
    documento_identidad = Column(String(50), nullable=True)
    tipo_documento = Column(Enum('dni', 'pasaporte', 'cedula'), nullable=True)
    creado_en = Column(DateTime, server_default=func.now())
    actualizado_en = Column(DateTime, onupdate=func.now())
```

**Endpoints Requeridos**:
```python
POST   /api/v1/customers              # Crear cliente
GET    /api/v1/customers/{cliente_id} # Obtener cliente
PUT    /api/v1/customers/{cliente_id} # Actualizar cliente
GET    /api/v1/customers              # Listar clientes (paginado)
GET    /api/v1/customers/{cliente_id}/reservations  # Historial de reservas
GET    /health                        # Health check
```

**Schemas Principales**:
```python
class CrearClienteRequest(BaseModel):
    usuario_id: Optional[str] = None
    nombre_completo: str = Field(min_length=3)
    email: EmailStr
    telefono: str = Field(pattern=r'^\+?[0-9]{10,15}$')
    fecha_nacimiento: Optional[date] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None

class ClienteResponse(BaseModel):
    cliente_id: str
    nombre_completo: str
    email: str
    telefono: str
    ciudad: Optional[str]
    pais: Optional[str]
    creado_en: datetime
```

**Seguridad**: Requiere JWT token válido en header `Authorization: Bearer <token>`

---

### 3. SERVICIO DE DISPONIBILIDAD (Availability Service)

**Puerto**: 8002

**Base de Datos**: Tablas `habitaciones`, `bloqueos`

**Modelos SQLAlchemy**:
```python
class HabitacionDB(Base):
    __tablename__ = "habitaciones"
    
    id = Column(Integer, primary_key=True)
    habitacion_id = Column(String(50), unique=True, index=True)
    hotel_id = Column(String(50), index=True)
    numero = Column(String(20))
    tipo = Column(Enum('standard', 'deluxe', 'suite'))
    piso = Column(Integer)
    capacidad_maxima = Column(Integer)
    precio_base = Column(Numeric(10, 2))
    caracteristicas = Column(JSON)  # Lista de características
    activa = Column(Boolean, default=True)

class BloqueoHabitacionDB(Base):
    __tablename__ = "bloqueos_habitacion"
    
    id = Column(Integer, primary_key=True)
    bloqueo_id = Column(String(50), unique=True, index=True)
    habitacion_id = Column(String(50), index=True)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    tipo = Column(Enum('temporal', 'reserva', 'mantenimiento'))
    reserva_id = Column(String(50), nullable=True)
    creado_en = Column(DateTime, server_default=func.now())
    expira_en = Column(DateTime, nullable=True)
    estado = Column(Enum('activo', 'expirado', 'confirmado'), default='activo')
```

**Endpoints Requeridos**:
```python
POST   /api/v1/availability/search    # Consultar disponibilidad
POST   /api/v1/availability/block     # Bloquear habitación temporalmente
DELETE /api/v1/availability/block/{bloqueo_id}  # Liberar bloqueo
POST   /api/v1/availability/confirm   # Confirmar bloqueo como reserva
GET    /api/v1/availability/rooms     # Listar habitaciones por hotel
GET    /health
```

**Schemas Principales**:
```python
class ConsultaDisponibilidadRequest(BaseModel):
    hotel_id: str
    fecha_inicio: date
    fecha_fin: date
    tipo_habitacion: Optional[str] = None
    numero_huespedes: int = Field(ge=1, le=10)
    precio_maximo: Optional[Decimal] = None

class HabitacionDisponible(BaseModel):
    habitacion_id: str
    numero: str
    tipo: str
    piso: int
    precio_por_noche: Decimal
    precio_total: Decimal
    caracteristicas: List[str]

class DisponibilidadResponse(BaseModel):
    hotel_id: str
    fecha_inicio: date
    fecha_fin: date
    noches: int
    habitaciones: List[HabitacionDisponible]
    total_disponibles: int

class BloquearHabitacionRequest(BaseModel):
    habitacion_id: str
    fecha_inicio: date
    fecha_fin: date
    duracion_minutos: int = 15

class BloqueoResponse(BaseModel):
    bloqueo_id: str
    habitacion_id: str
    expira_en: datetime
    estado: str
```

**Lógica de Negocio**:
- Bloqueos temporales expiran automáticamente después de `duracion_minutos`
- No permitir doble bloqueo de la misma habitación en las mismas fechas
- Al consultar disponibilidad, excluir habitaciones con bloqueos activos
- Background task que limpia bloqueos expirados cada 5 minutos

**Seguridad**: Requiere JWT

---

### 4. SERVICIO DE TARIFAS (Pricing Service)

**Puerto**: 8003

**Base de Datos**: Tablas `tarifas_base`, `promociones`

**Modelos SQLAlchemy**:
```python
class TarifaBaseDB(Base):
    __tablename__ = "tarifas_base"
    
    id = Column(Integer, primary_key=True)
    hotel_id = Column(String(50), index=True)
    tipo_habitacion = Column(Enum('standard', 'deluxe', 'suite'))
    temporada = Column(Enum('baja', 'media', 'alta'))
    precio_noche = Column(Numeric(10, 2))
    vigente_desde = Column(Date)
    vigente_hasta = Column(Date, nullable=True)

class PromocionDB(Base):
    __tablename__ = "promociones"
    
    id = Column(Integer, primary_key=True)
    codigo = Column(String(20), unique=True, index=True)
    descripcion = Column(String(255))
    tipo_descuento = Column(Enum('porcentaje', 'monto_fijo'))
    valor_descuento = Column(Numeric(10, 2))
    minimo_noches = Column(Integer, nullable=True)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    usos_maximos = Column(Integer, nullable=True)
    usos_actuales = Column(Integer, default=0)
    activa = Column(Boolean, default=True)
```

**Endpoints Requeridos**:
```python
POST   /api/v1/pricing/calculate      # Calcular precio de reserva
POST   /api/v1/pricing/validate-coupon # Validar código promocional
GET    /api/v1/pricing/promotions     # Listar promociones activas
GET    /health
```

**Schemas Principales**:
```python
class CalcularPrecioRequest(BaseModel):
    hotel_id: str
    tipo_habitacion: str
    fecha_inicio: date
    fecha_fin: date
    servicios_adicionales: Optional[List[str]] = []
    codigo_promocional: Optional[str] = None

class DetallesPrecio(BaseModel):
    subtotal: Decimal
    impuestos: Decimal
    servicios_adicionales: Decimal
    descuentos: Decimal
    total: Decimal
    moneda: str = "USD"
    desglose: List[dict]

class ValidarCuponRequest(BaseModel):
    codigo: str
    monto: Decimal
    fecha_reserva: date
    noches: int

class ValidarCuponResponse(BaseModel):
    codigo: str
    valido: bool
    descuento: Decimal
    mensaje: str
```

**Reglas de Pricing**:
- Precios base por tipo de habitación: standard=$100, deluxe=$180, suite=$300
- Temporada alta (dic, ene, jul, ago): +30% sobre precio base
- Temporada media (nov, feb, jun): +15% sobre precio base
- Impuestos: 18% sobre subtotal
- Servicios adicionales: desayuno=$20/día, parking=$10/día, spa=$50/servicio
- Descuentos por estancia larga: 7+ noches = 5%, 14+ noches = 10%

**Seguridad**: Requiere JWT

---

### 5. SERVICIO DE PAGOS (Payment Service) - SIMULADO ⚠️

**Puerto**: 8004

**Base de Datos**: Tabla `transacciones`

**Modelo Transacción (SQLAlchemy)**:
```python
class TransaccionDB(Base):
    __tablename__ = "transacciones"
    
    id = Column(Integer, primary_key=True)
    transaccion_id = Column(String(50), unique=True, index=True)
    reserva_id = Column(String(50), index=True, nullable=True)
    cliente_id = Column(String(50), index=True)
    monto = Column(Numeric(10, 2))
    moneda = Column(String(3), default='USD')
    tipo = Column(Enum('cargo', 'reembolso'))
    metodo_pago = Column(String(50))
    estado = Column(Enum('pendiente', 'aprobado', 'rechazado', 'reembolsado'))
    codigo_aprobacion = Column(String(50), nullable=True)
    codigo_error = Column(String(10), nullable=True)
    mensaje_error = Column(String(255), nullable=True)
    procesado_en = Column(DateTime, nullable=True)
    creado_en = Column(DateTime, server_default=func.now())
```

**Endpoints Requeridos**:
```python
POST   /api/v1/payments/process       # Procesar pago
POST   /api/v1/payments/refund        # Procesar reembolso
GET    /api/v1/payments/{transaccion_id}  # Consultar transacción
GET    /api/v1/payments/by-reservation/{reserva_id}  # Transacciones de una reserva
GET    /health
```

**Schemas Principales**:
```python
class ProcesarPagoRequest(BaseModel):
    cliente_id: str
    reserva_id: Optional[str] = None
    monto: Decimal = Field(gt=0)
    moneda: str = "USD"
    metodo_pago: MetodoPago
    descripcion: Optional[str] = None

class MetodoPago(BaseModel):
    tipo: str = Field(pattern="^(tarjeta_credito|tarjeta_debito|paypal)$")
    token: str = Field(min_length=10)
    titular: Optional[str] = None

class TransaccionResponse(BaseModel):
    transaccion_id: str
    estado: str
    monto: Decimal
    codigo_aprobacion: Optional[str]
    mensaje: str
    procesado_en: datetime

class ReembolsarRequest(BaseModel):
    transaccion_id: str
    monto: Decimal
    razon: Optional[str] = None
```

**LÓGICA DE SIMULACIÓN (IMPORTANTE)**:
```python
# En simulator.py

def simular_procesamiento_pago(monto: Decimal, token: str) -> dict:
    """
    Simula el procesamiento de un pago con reglas de aprobación/rechazo.
    """
    # Regla 1: Tokens de prueba
    if token == "tok_visa_4242":
        return {"aprobado": True, "codigo": "APR_" + generar_codigo()}
    
    if token == "tok_rechazado":
        return {"aprobado": False, "codigo": "ERR_001", "mensaje": "Fondos insuficientes"}
    
    # Regla 2: Montos muy altos se rechazan (> $10,000)
    if monto > Decimal("10000.00"):
        return {"aprobado": False, "codigo": "ERR_002", "mensaje": "Monto excede límite"}
    
    # Regla 3: Simular latencia de red (100-500ms)
    time.sleep(random.uniform(0.1, 0.5))
    
    # Regla 4: 10% de probabilidad de rechazo aleatorio
    if random.random() < 0.1:
        errores = [
            ("ERR_003", "Tarjeta expirada"),
            ("ERR_004", "Transacción sospechosa"),
            ("ERR_005", "Límite diario excedido")
        ]
        codigo, mensaje = random.choice(errores)
        return {"aprobado": False, "codigo": codigo, "mensaje": mensaje}
    
    # Regla 5: Por defecto, aprobar
    return {"aprobado": True, "codigo": "APR_" + generar_codigo()}
```

**Publicar Eventos**:
- Cuando pago es aprobado → `evento: "pago.aprobado"`
- Cuando pago es rechazado → `evento: "pago.rechazado"`

**Seguridad**: Requiere JWT

---

### 6. SERVICIO DE RESERVAS (Reservation Service) - MEJORAR

**Puerto**: 8005

**Ya implementado parcialmente, mejorar con**:

1. **Orquestador completo** (orchestrator.py):
```python
class CrearReservaOrchestrator:
    """
    Orquesta el proceso completo de crear una reserva:
    1. Validar datos
    2. Obtener info cliente (Customer Service)
    3. Consultar disponibilidad (Availability Service)
    4. Calcular precio (Pricing Service)
    5. Bloquear habitación (Availability Service)
    6. Procesar pago (Payment Service)
    7. Crear reserva en BD
    8. Confirmar bloqueo (Availability Service)
    9. Publicar evento "reserva.creada"
    
    Si algo falla, implementar compensaciones (Saga pattern).
    """
```

2. **Cliente HTTP** para comunicación inter-servicios (shared/http_client.py):
```python
class ServiceClient:
    """Cliente HTTP para comunicarse con otros servicios"""
    
    async def get_customer(self, cliente_id: str, token: str) -> dict:
        url = f"{CUSTOMER_SERVICE_URL}/api/v1/customers/{cliente_id}"
        headers = {"Authorization": f"Bearer {token}"}
        # Hacer request con httpx
    
    async def check_availability(self, params: dict, token: str) -> dict:
        url = f"{AVAILABILITY_SERVICE_URL}/api/v1/availability/search"
        # ...
    
    async def calculate_price(self, params: dict, token: str) -> dict:
        # ...
    
    async def process_payment(self, params: dict, token: str) -> dict:
        # ...
```

3. **Endpoints adicionales**:
```python
PUT    /api/v1/reservations/{reserva_id}  # Modificar reserva
POST   /api/v1/reservations/{reserva_id}/checkin   # Check-in
POST   /api/v1/reservations/{reserva_id}/checkout  # Check-out
```

---

### 7. SERVICIO DE NOTIFICACIONES - MEJORAR

**Puerto**: 8006

**Expandir con**:

1. **Suscripción a más eventos**:
   - `reserva.creada` → Email de confirmación
   - `reserva.cancelada` → Email de cancelación
   - `pago.aprobado` → Email de comprobante
   - `pago.rechazado` → Email de pago fallido
   - `reserva.modificada` → Email de cambios

2. **Templates de emails** (templates/):
```
templates/
├── confirmacion_reserva.html
├── cancelacion_reserva.html
├── pago_aprobado.html
├── pago_rechazado.html
└── recordatorio_checkin.html
```

3. **Endpoint de historial**:
```python
GET    /api/v1/notifications/history?cliente_id={id}  # Historial de notificaciones
GET    /api/v1/notifications/stats  # Estadísticas de envíos
```

---

## 🔐 SEGURIDAD Y MIDDLEWARE

### Middleware JWT (shared/security.py)
```python
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Middleware que valida el token JWT en todas las peticiones protegidas.
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        usuario_id = payload.get("usuario_id")
        if usuario_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

# Uso en endpoints:
@app.get("/api/v1/clientes/me")
async def obtener_perfil(current_user: dict = Depends(verify_token)):
    usuario_id = current_user["usuario_id"]
    # ...
```

---

## 🎪 SISTEMA DE EVENTOS MEJORADO

### Event Bus Mejorado (shared/events.py)
```python
class EventBus:
    """Event Bus con soporte para eventos asíncronos y logging mejorado"""
    
    _instance = None
    _suscriptores: Dict[str, List[Callable]] = {}
    _event_history: List[dict] = []  # Para auditoría
    
    def publicar(self, tipo_evento: str, datos: dict):
        """Publica un evento a todos los suscriptores"""
        evento = {
            "tipo": tipo_evento,
            "datos": datos,
            "timestamp": datetime.now(),
            "evento_id": str(uuid.uuid4())
        }
        
        # Guardar en historial
        self._event_history.append(evento)
        
        # Notificar suscriptores
        if tipo_evento in self._suscriptores:
            for callback in self._suscriptores[tipo_evento]:
                try:
                    callback(datos)
                except Exception as e:
                    logger.error(f"Error en callback: {e}")
    
    def obtener_historial(self, filtro_tipo: str = None) -> List[dict]:
        """Obtiene el historial de eventos para auditoría"""
        if filtro_tipo:
            return [e for e in self._event_history if e["tipo"] == filtro_tipo]
        return self._event_history
```

---

## 🐳 DOCKER COMPOSE COMPLETO
```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: hotel-mysql
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: hotel_reservations
      MYSQL_USER: hotel_user
      MYSQL_PASSWORD: hotel_pass
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      timeout: 20s
      retries: 10

  auth-service:
    build: ./services/auth
    container_name: auth-service
    ports:
      - "8000:8000"
    environment:
      MYSQL_HOST: mysql
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
    depends_on:
      mysql:
        condition: service_healthy

  customers-service:
    build: ./services/customers
    container_name: customers-service
    ports:
      - "8001:8000"
    environment:
      MYSQL_HOST: mysql
      AUTH_SERVICE_URL: http://auth-service:8000
    depends_on:
      - mysql
      - auth-service

  availability-service:
    build: ./services/availability
    container_name: availability-service
    ports:
      - "8002:8000"
    environment:
      MYSQL_HOST: mysql
    depends_on:
      - mysql

  pricing-service:
    build: ./services/pricing
    container_name: pricing-service
    ports:
      - "8003:8000"
    environment:
      MYSQL_HOST: mysql
    depends_on:
      - mysql

  payments-service:
    build: ./services/payments
    container_name: payments-service
    ports:
      - "8004:8000"
    environment:
      MYSQL_HOST: mysql
    depends_on:
      - mysql

  reservations-service:
    build: ./services/reservations
    container_name: reservations-service
    ports:
      - "8005:8000"
    environment:
      MYSQL_HOST: mysql
      CUSTOMERS_SERVICE_URL: http://customers-service:8000
      AVAILABILITY_SERVICE_URL: http://availability-service:8000
      PRICING_SERVICE_URL: http://pricing-service:8000
      PAYMENTS_SERVICE_URL: http://payments-service:8000
    depends_on:
      - mysql
      - customers-service
      - availability-service
      - pricing-service
      - payments-service

  notifications-service:
    build: ./services/notifications
    container_name: notifications-service
    ports:
      - "8006:8000"
    depends_on:
      - mysql

volumes:
  mysql_data:
```

---

## 🧪 TESTING COMPLETO

### Test por Servicio

Cada servicio debe tener:

1. **Tests Unitarios** (test_<servicio>.py):
   - Probar cada método del service layer
   - Mockar dependencias externas
   - Cobertura > 80%

2. **Tests de Integración** (test_integration.py):
   - Probar flujos completos end-to-end
   - Ejemplo: crear reserva completa que invoca todos los servicios

3. **Tests de Rendimiento** (test_performance.py):
   - Latencia de endpoints < 500ms
   - Throughput mínimo: 100 req/min
   - Test de carga concurrente

### Ejemplo Test de Integración
```python
def test_flujo_completo_crear_reserva():
    """
    Test end-to-end del flujo completo de crear una reserva:
    1. Registrar usuario
    2. Login para obtener token
    3. Crear cliente
    4. Consultar disponibilidad
    5. Crear reserva (que internamente llama a pricing, payments, etc.)
    6. Verificar que se envió notificación
    """
    # 1. Registrar
    response = client.post("/api/v1/auth/register", json={...})
    assert response.status_code == 201
    
    # 2. Login
    response = client.post("/api/v1/auth/login", json={...})
    token = response.json()["access_token"]
    
    # 3. Crear cliente
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/customers", json={...}, headers=headers)
    cliente_id = response.json()["cliente_id"]
    
    # 4. Consultar disponibilidad
    response = client.post("/api/v1/availability/search", json={...}, headers=headers)
    assert response.json()["total_disponibles"] > 0
    
    # 5. Crear reserva
    response = client.post("/api/v1/reservations", json={
        "cliente_id": cliente_id,
        ...
    }, headers=headers)
    assert response.status_code == 201
    reserva = response.json()
    assert reserva["estado"] == "CONFIRMADA"
    
    # 6. Verificar notificación
    time.sleep(1)  # Dar tiempo para evento asíncrono
    response = client.get(f"/api/v1/notifications/history?cliente_id={cliente_id}")
    assert len(response.json()["notificaciones"]) > 0
```

---

## 📊 ACTIVIDADES A COMPLETAR

### Actividad 13: Desarrollo de Servicios
- ✅ Implementar los 7 servicios con FastAPI
- ✅ Persistencia MySQL con SQLAlchemy
- ✅ Validación con Pydantic
- ✅ Documentación OpenAPI automática
- ✅ Dockerización

### Actividad 14: Servicios Orientados a Eventos
- ✅ Event Bus mejorado con historial
- ✅ Servicio de Notificaciones suscrito a 5+ eventos
- ✅ Templates HTML para emails
- ✅ Logging de eventos para auditoría

### Actividad 15: Pruebas
- ✅ Tests unitarios por servicio (cobertura > 80%)
- ✅ Tests de integración de flujos completos
- ✅ Tests de rendimiento con métricas
- ✅ Documentar problemas encontrados y soluciones

---

## 🎯 CRITERIOS DE ÉXITO

El proyecto está completo cuando:
- [x] Los 7 servicios están implementados y funcionando
- [x] Todos los servicios tienen tests con cobertura > 80%
- [x] El flujo completo de crear reserva funciona end-to-end
- [x] El sistema de eventos funciona correctamente
- [x] La documentación OpenAPI está completa
- [x] Docker Compose levanta todos los servicios sin errores
- [x] Los tests de integración pasan exitosamente
- [x] Hay logging estructurado en todos los servicios

---

## 📌 NOTAS IMPORTANTES

1. **Código limpio**: Seguir PEP 8, type hints, docstrings
2. **Manejo de errores**: Try-except en todos los endpoints
3. **Logging**: Usar logging estándar de Python
4. **Variables de entorno**: Usar pydantic-settings
5. **Seguridad**: NUNCA hardcodear secrets, usar .env
6. **Commits**: Commits atómicos con mensajes descriptivos
7. **Documentación**: Cada endpoint debe tener docstring completo

---

## 🚀 ORDEN DE IMPLEMENTACIÓN SUGERIDO

1. **Fase 1 - Fundamentos**:
   - shared/database.py
   - shared/exceptions.py
   - shared/events.py
   - docker-compose.yml base

2. **Fase 2 - Servicios Base**:
   - Auth Service (primero, porque otros dependen de JWT)
   - Customers Service
   - Availability Service
   - Pricing Service
   - Payments Service (simulado)

3. **Fase 3 - Orquestación**:
   - shared/http_client.py
   - Mejorar Reservations Service con orchestrator
   - Mejorar Notifications Service

4. **Fase 4 - Testing**:
   - Tests unitarios por servicio
   - Tests de integración
   - Tests de rendimiento

---

## 🎓 ENTREGABLES

1. Código fuente completo en repositorio Git
2. README.md con instrucciones de instalación y uso
3. Docker Compose funcional
4. Colección Postman/Insomnia con ejemplos de requests
5. Reporte de cobertura de tests
6. Documento con problemas encontrados y soluciones (Actividad 15)

---

¡Manos a la obra! 🚀