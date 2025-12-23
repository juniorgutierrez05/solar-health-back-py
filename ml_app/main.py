"""
FastAPI - Machine Learning | Solar Health
=========================================
Microservicio de Machine Learning para:
- Peak Shaving
- Predicción de consumo y tarifas
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ml_app.routes.tarifas import tarifas
from ml_app.routes.peak_shaving import peak_saving
import uvicorn
import os

# Routers ML
from app.routes import peak_shaving
from ml_app.routes.routers_tarifas import router_prediccion

# Crear aplicación FastAPI
app = FastAPI(
    title="Solar Health - Machine Learning API",
    description="Microservicio ML para análisis y predicción energética",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(tarifas)
app.include_router(peak_saving)

# Endpoint raíz
@app.get("/")
def root():
    return {
        "service": "Solar Health ML API",
        "version": "1.0.0",
        "modules": [
            "Peak Shaving",
            "Predicción de consumo y facturación"
        ],
        "docs": "/docs"
    }

# Health check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "solar-health-ml"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))  # ML corre en puerto separado
    uvicorn.run(
        "ml_app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
