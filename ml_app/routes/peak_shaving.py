from fastapi import APIRouter
import joblib
import numpy as np
from ml_app.models.schemas_peak_saving import PeakShavingInput
from pathlib import Path

MODEL_DIR = Path(__file__).parent.parent / "modelos"

peak_saving = APIRouter(prefix="/api", tags=["peak-shaving"])   

# =========================
# Cargar modelo
# =========================
model = joblib.load(MODEL_DIR / "peak_shaving_model.pkl")

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

    try:
        prediction = model.predict(X)[0]
        # Check if the model supports probability prediction
        if hasattr(model, "predict_proba"):
            probability = model.predict_proba(X)[0][1]
        else:
            # Fallback if model is a Regressor or doesn't support proba
            probability = 1.0 if prediction == 1 else 0.0
    except Exception as e:
        print(f"Error during prediction: {e}")
        # Return a safe fallback or re-raise with better message
        # For now, we return default values to avoid 500 in dev, 
        # or we could raise HTTPException.
        # Let's raise HTTPException for visibility in client
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Model prediction failed: {str(e)}")

    return {
        "peak_shaving": bool(prediction),
        "label": "High Consumption Peak" if prediction == 1 else "Normal Consumption",
        "confidence": round(probability, 3)
    }
