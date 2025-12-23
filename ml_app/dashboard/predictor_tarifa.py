"""
Módulo de predicción - Lógica del modelo ML
"""
import pandas as pd
import numpy as np
import joblib
from pathlib import Path

# Cargar modelo al inicio
MODEL_DIR = Path(__file__).parent.parent / "modelos"

import sys

# Definir la función que falta en __main__
def asignar_tarifa(ts):
    hora = ts.hour
    dia_semana = ts.dayofweek
    if dia_semana < 5 and 7 <= hora < 22:  # Laborables peak
        return 0.35  # AUD/kWh peak
    else:
        return 0.15  # AUD/kWh off-peak

# Inyectar la función en __main__ para que pickle la encuentre
import __main__
setattr(__main__, "asignar_tarifa", asignar_tarifa)

print("Cargando modelo ML...")
try:
    paquete = joblib.load(MODEL_DIR / 'paquete_completo_prediccion_factura.pkl')
except AttributeError as e:
    # Fallback si __main__ no funciona como esperamos (ej. en algunos entornos de test)
    # Intentamos inyectarlo en el módulo actual y decirle a sys.modules que __main__ es este módulo
    print(f"Advertencia: {e}. Intentando estrategia alternativa de carga...")
    # Esta parte es solo por si acaso, el setattr arriba debería ser suficiente
    raise e

paquete = joblib.load(MODEL_DIR / 'paquete_completo_prediccion_factura.pkl')

modelo = paquete['modelo']
features = paquete['features']
asignar_tarifa = paquete['tarifas']['funcion_tarifa']
df_historico = paquete['df_historico_ultimos_30_dias']

print("✓ Modelo ML cargado exitosamente\n")


def predecir_consumo_interno(timestamp_str: str, temperatura: float, 
                             es_periodo_clases: bool = True, 
                             es_feriado: bool = False,
                             es_examen: bool = False) -> dict:
    """
    Función de predicción usando el modelo ML
    """
    timestamp = pd.Timestamp(timestamp_str)
    
    # Extraer info del timestamp
    hora = timestamp.hour
    dia_semana = timestamp.dayofweek
    mes = timestamp.month
    es_fin_semana = 1 if dia_semana >= 5 else 0
    
    # Features cíclicas
    hour_sin = np.sin(2 * np.pi * hora / 24)
    hour_cos = np.cos(2 * np.pi * hora / 24)
    dayofweek_sin = np.sin(2 * np.pi * dia_semana / 7)
    dayofweek_cos = np.cos(2 * np.pi * dia_semana / 7)
    
    # Features de clima
    temp_squared = temperatura ** 2
    
    # Obtener lags del histórico
    consumo_historico = df_historico['consumo_neto_kwh']
    mask_similar = (df_historico.index.hour == hora) & (df_historico.index.dayofweek == dia_semana)
    
    if mask_similar.sum() > 0:
        consumo_similar = consumo_historico[mask_similar].mean()
    else:
        consumo_similar = consumo_historico.mean()
    
    lag_1d = consumo_similar
    lag_2d = consumo_similar * 0.98
    lag_1w = consumo_similar * 1.02
    rolling_mean_24h = consumo_similar
    rolling_max_24h = consumo_similar * 1.2
    
    # Features de volatilidad
    std_1d = consumo_historico.rolling(96).std().mean()
    std_2h = std_1d * 0.5
    max_1d = consumo_similar * 1.2
    min_1d = consumo_similar * 0.7
    range_1d = max_1d - min_1d
    
    # Features de cambio
    diff_1 = 0
    diff_4 = 0
    
    # Features de interacción
    es_hora_pico = 1 if (dia_semana < 5 and 7 <= hora < 22) else 0
    temp_x_peak = temperatura * es_hora_pico
    workday_semester = 1 if (dia_semana < 5 and es_periodo_clases) else 0
    
    # Crear DataFrame con todas las features
    datos = pd.DataFrame({
        'hour': [hora],
        'dayofweek': [dia_semana],
        'month': [mes],
        'is_weekend': [es_fin_semana],
        'hour_sin': [hour_sin],
        'hour_cos': [hour_cos],
        'dayofweek_sin': [dayofweek_sin],
        'dayofweek_cos': [dayofweek_cos],
        'is_holiday': [1 if es_feriado else 0],
        'is_semester': [1 if es_periodo_clases else 0],
        'is_exam': [1 if es_examen else 0],
        'air_temperature': [temperatura],
        'temp_squared': [temp_squared],
        'lag_1d': [lag_1d],
        'lag_2d': [lag_2d],
        'lag_1w': [lag_1w],
        'rolling_mean_24h': [rolling_mean_24h],
        'rolling_max_24h': [rolling_max_24h],
        'std_1d': [std_1d],
        'std_2h': [std_2h],
        'max_1d': [max_1d],
        'min_1d': [min_1d],
        'range_1d': [range_1d],
        'diff_1': [diff_1],
        'diff_4': [diff_4],
        'is_peak_hour': [es_hora_pico],
        'temp_x_peak': [temp_x_peak],
        'workday_semester': [workday_semester]
    })
    
    # Hacer predicción
    consumo = modelo.predict(datos[features])[0]
    precio = asignar_tarifa(timestamp)
    costo = consumo * precio
    
    return {
        'timestamp': timestamp_str,
        'dia_semana': timestamp.day_name(),
        'consumo_kwh': round(consumo, 2),
        'precio_aud_kwh': precio,
        'costo_aud_15min': round(costo, 4),
        'costo_aud_hora': round(costo * 4, 2),
        'es_horario_peak': precio == 0.35
    }