from fastapi import FastAPI
from routes.peak_shaving import router as peak_shaving_router

app = FastAPI(
    title="Energy Optimization API",
    version="1.0"
)

# Registrar rutas
app.include_router(peak_shaving_router, prefix="/api")
