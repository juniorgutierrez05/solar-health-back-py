from fastapi import APIRouter
import joblib
import numpy as np
from ml_app.models.schemas_peak_saving import PeakShavingInput

peak_saving = APIRouter()

# =========================
# Cargar modelo
# =========================
model = joblib.load("ml_app/modelos/peak_shaving_model.pkl")

# =========================
# Endpoint
# =========================
@peak_saving.post("/predict/peak-shaving")
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
