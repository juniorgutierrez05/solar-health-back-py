from fastapi import APIRouter, HTTPException
from ml_app.models.schemas_tarifa import (
    PrediccionPuntualRequest, PrediccionPuntualResponse,
    FacturaMensualRequest, FacturaMensualResponse
)
from ml_app.dashboard.predictor_tarifa import predecir_consumo_interno
import pandas as pd
import numpy as np

# Router principal
router_prediccion = APIRouter(prefix="/api", tags=["prediccion"])


@router_prediccion.post("/predict", response_model=PrediccionPuntualResponse)
def predecir_consumo_endpoint(request: PrediccionPuntualRequest):
    """
    Predice consumo y costo para un momento específico
    
    - **timestamp**: Fecha y hora (ISO 8601)
    - **temperatura**: Temperatura en °C
    - **es_periodo_clases**: Período académico (opcional)
    - **es_feriado**: Día feriado (opcional)
    - **es_examen**: Período de exámenes (opcional)
    """
    try:
        resultado = predecir_consumo_interno(
            timestamp_str=request.timestamp,
            temperatura=request.temperatura,
            es_periodo_clases=request.es_periodo_clases,
            es_feriado=request.es_feriado,
            es_examen=request.es_examen
        )
        return resultado
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en predicción: {str(e)}")


@router_prediccion.post("/predict/monthly", response_model=FacturaMensualResponse)
def calcular_factura_endpoint(request: FacturaMensualRequest):
    """
    Calcula la factura completa de un mes
    
    - **mes_año**: Mes en formato YYYY-MM
    - **temperatura_promedio**: Temperatura promedio del mes en °C
    - **es_periodo_clases**: Período académico (opcional)
    
    ⚠️ Este endpoint puede tardar ~30-60 segundos
    """
    try:
        # Crear todos los intervalos del mes
        start = f'{request.mes_año}-01 00:00:00'
        end = pd.Timestamp(start) + pd.DateOffset(months=1) - pd.Timedelta(minutes=15)
        timestamps = pd.date_range(start=start, end=end, freq='15min')
        
        consumo_total = 0
        costo_total = 0
        costo_peak = 0
        costo_offpeak = 0
        intervalos_peak = 0
        intervalos_offpeak = 0
        
        # Procesar todos los intervalos
        for ts in timestamps:
            # Variar temperatura según hora del día
            temp = request.temperatura_promedio + 4 * np.sin(2 * np.pi * (ts.hour - 6) / 24)
            
            # Ajustar por día de semana
            if ts.dayofweek >= 5:
                es_clases = False
            else:
                es_clases = request.es_periodo_clases
            
            # Predicción
            r = predecir_consumo_interno(
                timestamp_str=str(ts),
                temperatura=temp,
                es_periodo_clases=es_clases
            )
            
            consumo_total += r['consumo_kwh']
            costo_total += r['costo_aud_15min']
            
            if r['es_horario_peak']:
                costo_peak += r['costo_aud_15min']
                intervalos_peak += 1
            else:
                costo_offpeak += r['costo_aud_15min']
                intervalos_offpeak += 1
        
        num_dias = timestamps[-1].day
        
        return {
            'mes': request.mes_año,
            'consumo_total_kwh': round(consumo_total, 2),
            'factura_total_aud': round(costo_total, 2),
            'costo_peak_aud': round(costo_peak, 2),
            'costo_offpeak_aud': round(costo_offpeak, 2),
            'porcentaje_peak': round(costo_peak / costo_total * 100, 1),
            'costo_promedio_diario': round(costo_total / num_dias, 2),
            'consumo_promedio_diario': round(consumo_total / num_dias, 2),
            'intervalos_peak': intervalos_peak,
            'intervalos_offpeak': intervalos_offpeak
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en cálculo de factura: {str(e)}")