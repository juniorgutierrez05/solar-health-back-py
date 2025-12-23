from fastapi import APIRouter
import joblib
import os

router = APIRouter(
    prefix="/ml/peak-shaving",
    tags=["Machine Learning - Peak Shaving"]
)

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "modelos",
    "peak_shaving_model.pkl"
)

model = joblib.load(MODEL_PATH)
print("Features del modelo:", model.feature_names_in_)



class PeakShavingInput(BaseModel):
    hour: int           # 0–23
    dayofweek: int      # 0=lunes ... 6=domingo
    solar_generation: float



import pandas as pd

@router.post("/predict")
def predict_peak_shaving(data: PeakShavingInput):

    X = pd.DataFrame([{
        "hour": data.hour,
        "dayofweek": data.dayofweek,
        "SolarGeneration": data.solar_generation
    }])

    prediction = model.predict(X)[0]

    return {
        "hour": data.hour,
        "dayofweek": data.dayofweek,
        "solar_generation": data.solar_generation,
        "peak_shaving": bool(prediction)
    }

