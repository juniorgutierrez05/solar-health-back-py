from pydantic import BaseModel
# =========================
# Esquema de entrada
# =========================

class PeakShavingInput(BaseModel):
    hour: int
    day_of_week: int
    ghi: float
    cloud_opacity: float