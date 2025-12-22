from fastapi import APIRouter
from pydantic import BaseModel
import joblib
import numpy as np

router = APIRouter()

# =========================
# Cargar modelo
# =========================
model = joblib.load("modelos/")

# =========================
# Esquema de entrada
# =========================
class PeakShavingInput(BaseModel):
    hour: int
    day_of_week: int
    ghi: float
    cloud_opacity: float

# =========================
# Endpoint
# =========================
@router.post("/predict/peak-shaving")
def predict_peak_shaving(data: PeakShavingInput):

    X = np.array([[
        data.hour,
        data.day_of_week,
        data.ghi,
        data.cloud_opacity
    ]])

    prediction = model.predict(X)[0]
    probability = model.predict_proba(X)[0][1]

    return {
        "peak_shaving": bool(prediction),
        "label": "High Consumption Peak" if prediction == 1 else "Normal Consumption",
        "confidence": round(probability, 3)
    }
