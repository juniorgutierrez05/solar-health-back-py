from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.routers import router_departamentos, router_ciudades, router_ips, router_registro
from app.db_config.database import engine
from app.models.models import Base
import os

# Crear las tablas (equivalente a JPA)
# Base.metadata.create_all(bind=engine)  # Descomenta si quieres crear tablas automáticamente

# Crear aplicación FastAPI
app = FastAPI(
    title="Solar Health Backend",
    description="Sistema backend para evaluación de proyectos solares fotovoltaicos en instituciones de salud",
    version="1.0.0"
)

# Configurar CORS (equivalente a @CrossOrigin en Spring)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(router_departamentos)
app.include_router(router_ciudades)
app.include_router(router_ips)
app.include_router(router_registro)

# Endpoint raíz
@app.get("/")
def root():
    return {
        "message": "Solar Health Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

# Endpoint de health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)