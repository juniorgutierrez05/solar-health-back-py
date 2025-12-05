from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime

# Schemas para Departamento
class DepartamentoBase(BaseModel):
    nombre: str

class DepartamentoResponse(DepartamentoBase):
    id: int
    
    class Config:
        from_attributes = True


# Schemas para Ciudad
class CiudadBase(BaseModel):
    nombre: str
    id_departamento: int

class CiudadResponse(CiudadBase):
    id: int
    
    class Config:
        from_attributes = True


# Schemas para IPS
class IPSBase(BaseModel):
    nombre: str
    tipo: str
    num_consultorios: int
    num_equipos: int
    id_ciudad: int

class IPSCreate(IPSBase):
    pass

class IPSResponse(IPSBase):
    id: int
    
    class Config:
        from_attributes = True


# Schemas para Consumo
class ConsumoBase(BaseModel):
    mes: str
    año: int
    consumo_kwh: Decimal

class ConsumoResponse(ConsumoBase):
    id: int
    id_ips: int
    fecha_registro: datetime
    
    class Config:
        from_attributes = True


# Schema para Registro Completo
class RegistroCompletoRequest(BaseModel):
    nombre_ips: str
    tipo_ips: str
    num_consultorios: int
    num_equipos: int
    id_ciudad: int
    mes_consumo: str
    año_consumo: int
    consumo_kwh: Decimal

class ResultadosFinancierosData(BaseModel):
    capex: Decimal
    opex: Decimal
    vpn: Decimal
    tir: Decimal
    inversion: Decimal
    ahorro_anual: Decimal
    periodo_retorno: Decimal
    num_paneles: int
    potencia_instalada_kw: Decimal
    area_utilizada_m2: Decimal
    irradiacion_utilizada: Decimal

class RegistroCompletoResponse(BaseModel):
    success: bool
    id_ips: Optional[int] = None
    ips_registrada: Optional[IPSResponse] = None
    consumo_registrado: Optional[ConsumoResponse] = None
    irradiacion_kwh_m2: Optional[Decimal] = None
    energia_generada_kwh_mes: Optional[Decimal] = None
    resultados_financieros: Optional[ResultadosFinancierosData] = None
    es_viable: Optional[bool] = None
    error: Optional[str] = None