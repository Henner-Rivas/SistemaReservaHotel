# Sistema de Reservas Hoteleras (SOA con FastAPI)

Proyecto de ejemplo con arquitectura de microservicios (SOA) para gestionar reservas de hotel: autenticación, clientes, disponibilidad, precios, pagos (simulado), reservas y notificaciones. Cada servicio es una API FastAPI independiente con documentación Swagger en `/docs`.

## Servicios y Puertos

- Auth: 8000
- Customers: 8001
- Availability: 8002
- Pricing: 8003
- Payments: 8004
- Reservations: 8005
- Notifications: 8006

## Requisitos

- Python 3.11+
- Docker y Docker Compose

## Variables de entorno (.env)

Crear un archivo `.env` en la raíz del proyecto con las claves JWT y, si lo deseas, sobrescribir valores de MySQL (por defecto se usan los del `docker-compose.yml`). Ejemplo:

```env
# JWT
JWT_SECRET_KEY=supersecreto-cambialo
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# MySQL (opcional, ya configurado en docker-compose)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=hotel_reservations
MYSQL_USER=hotel_user
MYSQL_PASSWORD=hotel_pass
```

## Ejecución con Docker Compose (recomendado)

1) Construir y levantar todos los servicios:

```bash
docker compose up -d --build
```

2) Verificar salud y documentación:

- Auth: http://localhost:8000/health | http://localhost:8000/docs
- Customers: http://localhost:8001/health | http://localhost:8001/docs
- Availability: http://localhost:8002/health | http://localhost:8002/docs
- Pricing: http://localhost:8003/health | http://localhost:8003/docs
- Payments: http://localhost:8004/health | http://localhost:8004/docs
- Reservations: http://localhost:8005/health | http://localhost:8005/docs
- Notifications: http://localhost:8006/health | http://localhost:8006/docs

3) Apagar los servicios:

```bash
docker compose down
```

## Ejecución local (sin Docker)

1) Crear entorno virtual e instalar dependencias:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) Asegúrate de tener una instancia de MySQL accesible y configura `.env` según corresponda.

3) Levantar un servicio (ejemplo: Auth):

```bash
uvicorn services.auth.main:app --reload --port 8000
```

Repite con los demás servicios cambiando el módulo y el puerto.

## Flujo básico de uso

1) Registro y login (Auth):

- Registrar usuario: `POST /api/v1/auth/register`
- Login: `POST /api/v1/auth/login` → devuelve `access_token` y `refresh_token`

2) Consumir endpoints protegidos:

- Enviar `Authorization: Bearer <access_token>` en llamadas a otros servicios (Availability, Customers, etc.).

3) Disponibilidad de habitaciones (Availability):

- Buscar: `POST /api/v1/availability/search`
- Bloquear: `POST /api/v1/availability/block`
- Liberar: `DELETE /api/v1/availability/block/{bloqueo_id}`
- Confirmar: `POST /api/v1/availability/confirm`

Otros servicios (pricing, payments, reservations, notifications) siguen una estructura similar y exponen su documentación en `/docs`.

## Base de datos

- Se usa MySQL 8 con credenciales definidas en `docker-compose.yml`.
- Los servicios leen la configuración desde `shared/database.py` y `.env`.
- Al iniciar Availability, se crean tablas y se siembran habitaciones de ejemplo si no existen.

## Seguridad

- JWT centralizado mediante `shared/security.py`.
- Las rutas protegidas requieren `Authorization: Bearer <token>`.
- La emisión de tokens se realiza en `services/auth/security.py`.

## Tests

Ejecutar pruebas:

```bash
pytest -q
```

Incluye tests de salud y disponibilidad (carpeta `tests/`).

## Estructura del repositorio

```
services/
  auth/           # Autenticación (JWT, registro, login)
  customers/      # Clientes
  availability/   # Disponibilidad y bloqueos de habitaciones
  pricing/        # Precios y reglas de tarifas
  payments/       # Pagos (simulado)
  reservations/   # Orquestación de reservas
  notifications/  # Notificaciones de eventos
shared/           # Módulos compartidos (DB, seguridad, eventos, HTTP)
tests/            # Pruebas (salud, disponibilidad)
docker-compose.yml
requirements.txt
README.md
```

## Troubleshooting

- Si MySQL no levanta, borra el volumen y vuelve a crear:

```bash
docker compose down -v
docker compose up -d --build
```

- Error 401 en APIs: asegúrate de enviar `Authorization: Bearer <access_token>` válido.
- Cambia `JWT_SECRET_KEY` en `.env` para producción.

## Licencia

Proyecto de demostración educativo.
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
