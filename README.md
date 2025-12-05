# Backend de Solar Health

Este proyecto ofrece un **backend en Python** para evaluar la viabilidad financiera de instalar sistemas de paneles solares en centros de salud. Incluye un modelo financiero completo que calcula:

- Área disponible del techo según el número de consultorios y equipos.
- Potencial de generación de energía usando datos de irradiación solar.
- Gastos de capital (CAPEX) y gastos operacionales (OPEX).
- Ahorro anual, Valor Presente Neto (VPN), Tasa Interna de Retorno (TIR) y período de retorno de la inversión.

La lógica principal se encuentra en `app/calculadora_financiera.py`, que expone métodos estáticos para realizar los cálculos. El backend puede integrarse con un servicio FastAPI (ver `main.py`) para ofrecer estos insights financieros a través de endpoints REST.

## Inicio rápido

1. Instale las dependencias (FastAPI, Uvicorn, etc.).
2. Ejecute la API con `uvicorn main:app --reload`.

El repositorio está estructurado para ser fácilmente extensible a nuevos modelos de energía o parámetros de costo.

# Estructura del Proyecto Python con FastAPI

```
solar-health-backend-python/
│
├── app/
│   ├── __init__.py
│   ├── database.py              # Configuración de SQLAlchemy
│   ├── models.py                # Modelos ORM (equivalente a entidades JPA)
│   ├── schemas.py               # Schemas Pydantic (validación)
│   ├── routers.py               # Endpoints REST (equivalente a Controllers)
│   └── calculadora_financiera.py # Lógica de cálculos financieros
│
├── .env                         # Variables de entorno
├── requirements.txt             # Dependencias Python
├── main.py                      # Aplicación principal
└── README.md
```

## Comparación Spring Boot vs FastAPI

| Aspecto | Spring Boot | FastAPI |
|---------|-------------|---------|
| **Entidades** | `@Entity`, JPA | SQLAlchemy ORM |
| **Controllers** | `@RestController` | `APIRouter` |
| **Dependency Injection** | `@Autowired` | `Depends()` |
| **Transacciones** | `@Transactional` | `db.commit()` |
| **Validación** | Bean Validation | Pydantic |
| **CORS** | `@CrossOrigin` | `CORSMiddleware` |
| **Precisión decimal** | `BigDecimal` | `Decimal` |
| **Configuración** | `application.properties` | `.env` |

## Pasos para Ejecutar

### 1. Crear entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar base de datos

Edita el archivo `.env` con tus credenciales de MySQL:

```env
DATABASE_URL=mysql+pymysql://root:@localhost:3306/solar-health
```

### 4. Ejecutar la aplicación

```bash
python main.py
```

O usando uvicorn directamente:

```bash
uvicorn main:app --reload --port 8000
```

### 5. Acceder a la documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints Disponibles

### Departamentos
- `GET /api/departamentos/` - Listar todos
- `GET /api/departamentos/{id}` - Obtener por ID

### Ciudades
- `GET /api/ciudades/` - Listar todas

### IPS
- `GET /api/ips/` - Listar todas
- `GET /api/ips/{id}` - Obtener por ID
- `POST /api/ips/registrar` - Registrar nueva IPS

### Registro Completo
- `POST /api/registro/completo` - Registro completo con cálculos financieros

## Ejemplo de Request

```json
POST /api/registro/completo
{
  "nombre_ips": "Hospital San José",
  "tipo_ips": "Hospital",
  "num_consultorios": 15,
  "num_equipos": 30,
  "id_ciudad": 1,
  "mes_consumo": "Enero",
  "año_consumo": 2024,
  "consumo_kwh": 5000
}
```

## Ventajas de FastAPI sobre Spring Boot

1. **Velocidad de desarrollo**: Menos código boilerplate
2. **Documentación automática**: Swagger UI incluido
3. **Validación automática**: Pydantic valida datos automáticamente
4. **Alto rendimiento**: Comparable con Node.js y Go
5. **Type hints**: Python moderno con tipado estático
6. **Async nativo**: Soporte para operaciones asíncronas
7. **Menor consumo de recursos**: Más ligero que la JVM

## Migraciones de Base de Datos (Opcional)

Para manejar migraciones como en Spring Boot, usa Alembic:

```bash
# Inicializar Alembic
alembic init alembic

# Crear migración
alembic revision --autogenerate -m "Initial migration"

# Aplicar migración
alembic upgrade head
```

## Testing

Para pruebas unitarias, instala:

```bash
pip install pytest pytest-asyncio httpx
```

Y crea pruebas en el directorio `tests/`.

## Deployment

### Con Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Con Gunicorn (producción)

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```