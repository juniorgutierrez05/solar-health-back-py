"""
FastAPI - Predicción de Consumo Eléctrico y Facturación
========================================================
API para predecir consumo energético y calcular facturas
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ml_app.routes.tarifas import tarifas
from ml_app.routes.peak_shaving import peak_saving
import uvicorn
import os

# Crear aplicación FastAPI
app = FastAPI(
    title="API Predicción Consumo Eléctrico",
    description="Predice consumo energético y calcula facturas para campus universitario",
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
        "nombre": "API Predicción Consumo Eléctrico",
        "version": "1.0.0",
        "endpoints": {
            "prediccion_puntual": "/api/predict",
            "factura_mensual": "/api/predict/monthly",
            "health": "/api/health",
            "documentacion": "/docs"
        }
    }

# Endpoint de health check
@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "ml-prediccion"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))  # Puerto diferente al principal (8000)
    uvicorn.run(
        "ml_app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )