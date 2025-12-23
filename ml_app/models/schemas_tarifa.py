from pydantic import BaseModel, Field
from typing import Optional

class PrediccionPuntualRequest(BaseModel):
    """Request para predicción de un momento específico"""
    timestamp: str = Field(
        ..., 
        example="2026-06-15T14:30:00",
        description="Fecha y hora en formato ISO 8601"
    )
    temperatura: float = Field(
        ..., 
        ge=-10, 
        le=50, 
        example=18.5,
        description="Temperatura en grados Celsius"
    )
    es_periodo_clases: Optional[bool] = Field(
        True, 
        example=True,
        description="¿El campus está en período de clases?"
    )
    es_feriado: Optional[bool] = Field(
        False, 
        example=False,
        description="¿Es un día feriado?"
    )
    es_examen: Optional[bool] = Field(
        False, 
        example=False,
        description="¿Es período de exámenes?"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2026-06-15T14:30:00",
                "temperatura": 18.5,
                "es_periodo_clases": True,
                "es_feriado": False,
                "es_examen": False
            }
        }


class PrediccionPuntualResponse(BaseModel):
    """Response con predicción puntual"""
    timestamp: str = Field(..., description="Fecha y hora de la predicción")
    dia_semana: str = Field(..., description="Día de la semana")
    consumo_kwh: float = Field(..., description="Consumo en kWh para 15 minutos")
    precio_aud_kwh: float = Field(..., description="Tarifa aplicada en AUD/kWh")
    costo_aud_15min: float = Field(..., description="Costo del intervalo de 15 min")
    costo_aud_hora: float = Field(..., description="Costo por hora en AUD")
    es_horario_peak: bool = Field(..., description="True si es horario peak")

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2026-06-15T14:30:00",
                "dia_semana": "Monday",
                "consumo_kwh": 285.43,
                "precio_aud_kwh": 0.35,
                "costo_aud_15min": 99.9001,
                "costo_aud_hora": 399.60,
                "es_horario_peak": True
            }
        }


class FacturaMensualRequest(BaseModel):
    """Request para cálculo de factura mensual"""
    mes_año: str = Field(
        ..., 
        pattern=r'^\d{4}-\d{2}$',
        example="2026-06",
        description="Mes en formato YYYY-MM"
    )
    temperatura_promedio: float = Field(
        ..., 
        ge=-10, 
        le=50, 
        example=16.0,
        description="Temperatura promedio del mes en °C"
    )
    es_periodo_clases: Optional[bool] = Field(
        True, 
        example=True,
        description="¿El mes está dentro del período académico?"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "mes_año": "2026-06",
                "temperatura_promedio": 16.0,
                "es_periodo_clases": True
            }
        }


class FacturaMensualResponse(BaseModel):
    """Response con factura mensual completa"""
    mes: str = Field(..., description="Mes calculado")
    consumo_total_kwh: float = Field(..., description="Consumo total del mes")
    factura_total_aud: float = Field(..., description="Factura total del mes")
    costo_peak_aud: float = Field(..., description="Costo en horario peak")
    costo_offpeak_aud: float = Field(..., description="Costo en horario off-peak")
    porcentaje_peak: float = Field(..., description="Porcentaje del costo en peak")
    costo_promedio_diario: float = Field(..., description="Costo promedio por día")
    consumo_promedio_diario: float = Field(..., description="Consumo promedio por día")
    intervalos_peak: int = Field(..., description="Número de intervalos en peak")
    intervalos_offpeak: int = Field(..., description="Número de intervalos en off-peak")

    class Config:
        json_schema_extra = {
            "example": {
                "mes": "2026-06",
                "consumo_total_kwh": 234567.89,
                "factura_total_aud": 82345.67,
                "costo_peak_aud": 58241.97,
                "costo_offpeak_aud": 24103.70,
                "porcentaje_peak": 70.7,
                "costo_promedio_diario": 2744.86,
                "consumo_promedio_diario": 7818.93,
                "intervalos_peak": 1260,
                "intervalos_offpeak": 1620
            }
        }
