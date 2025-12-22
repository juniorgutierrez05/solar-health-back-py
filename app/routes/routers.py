from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from datetime import datetime

from app.db_config.database import get_db
from app.models.models import Departamento, Ciudad, IPS, Consumo, Irradiacion, SistemaFV, ResultadosFinancieros
from app.schemas import (
    DepartamentoResponse, CiudadResponse, IPSResponse, IPSCreate,
    RegistroCompletoRequest, RegistroCompletoResponse, ResultadosFinancierosData,
    ConsumoResponse
)
from app.dashboard.calculadora_financiera import CalculadoraFinanciera

# Router para Departamentos
router_departamentos = APIRouter(prefix="/api/departamentos", tags=["departamentos"])

@router_departamentos.get("/", response_model=List[DepartamentoResponse])
def get_departamentos(db: Session = Depends(get_db)):
    """Obtener todos los departamentos"""
    departamentos = db.query(Departamento).all()
    return departamentos

@router_departamentos.get("/{id}", response_model=DepartamentoResponse)
def get_departamento_by_id(id: int, db: Session = Depends(get_db)):
    """Obtener un departamento por ID"""
    departamento = db.query(Departamento).filter(Departamento.id == id).first()
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    return departamento


# Router para Ciudades
router_ciudades = APIRouter(prefix="/api/ciudades", tags=["ciudades"])

@router_ciudades.get("/", response_model=List[CiudadResponse])
def get_ciudades(db: Session = Depends(get_db)):
    """Obtener todas las ciudades"""
    ciudades = db.query(Ciudad).all()
    return ciudades


# Router para IPS
router_ips = APIRouter(prefix="/api/ips", tags=["ips"])

@router_ips.get("/", response_model=List[IPSResponse])
def get_ips(db: Session = Depends(get_db)):
    """Obtener todas las IPS"""
    ips_list = db.query(IPS).all()
    return ips_list

@router_ips.get("/{id}", response_model=IPSResponse)
def get_ips_by_id(id: int, db: Session = Depends(get_db)):
    """Obtener una IPS por ID"""
    ips = db.query(IPS).filter(IPS.id == id).first()
    if not ips:
        raise HTTPException(status_code=404, detail="IPS no encontrada")
    return ips

@router_ips.post("/registrar", response_model=dict)
def registrar_ips(ips_data: IPSCreate, db: Session = Depends(get_db)):
    """Registrar una nueva IPS"""
    try:
        nueva_ips = IPS(**ips_data.model_dump())
        db.add(nueva_ips)
        db.commit()
        db.refresh(nueva_ips)
        return {
            "success": True,
            "message": f"IPS registrada exitosamente con ID: {nueva_ips.id}",
            "id": nueva_ips.id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al registrar IPS: {str(e)}")


# Router para Registro Completo
router_registro = APIRouter(prefix="/api/registro", tags=["registro"])

@router_registro.post("/completo", response_model=RegistroCompletoResponse)
def registro_completo(datos: RegistroCompletoRequest, db: Session = Depends(get_db)):
    """
    Endpoint principal: Registro completo de IPS con cálculos financieros
    """
    try:
        # 1. REGISTRAR IPS
        nueva_ips = IPS(
            nombre=datos.nombre_ips,
            tipo=datos.tipo_ips,
            num_consultorios=datos.num_consultorios,
            num_equipos=datos.num_equipos,
            id_ciudad=datos.id_ciudad
        )
        db.add(nueva_ips)
        db.flush()
        
        # 2. REGISTRAR CONSUMO
        nuevo_consumo = Consumo(
            id_ips=nueva_ips.id,
            mes=datos.mes_consumo,
            año=datos.año_consumo,
            consumo_kwh=datos.consumo_kwh,
            fecha_registro=datetime.utcnow()
        )
        db.add(nuevo_consumo)
        db.flush()
        
        # 3. OBTENER IRRADIACIÓN REAL DE LA BD
        irradiacion_obj = db.query(Irradiacion).filter(
            Irradiacion.id_ciudad == datos.id_ciudad,
            Irradiacion.mes == datos.mes_consumo
        ).first()
        
        irradiacion = irradiacion_obj.irradiacion_kwh_m2_mes if irradiacion_obj else Decimal("4.5")
        
        # 4. CALCULAR TODOS LOS RESULTADOS FINANCIEROS
        resultados = CalculadoraFinanciera.calcular_resultados_completos(
            num_consultorios=datos.num_consultorios,
            num_equipos=datos.num_equipos,
            consumo=datos.consumo_kwh,
            irradiacion=irradiacion
        )
        
        energia_generada = resultados["energia_generada"]
        
        # 5. REGISTRAR SISTEMA FV
        nuevo_sistema = SistemaFV(
            id_ips=nueva_ips.id,
            energia_generada_kwh_mes=energia_generada
        )
        db.add(nuevo_sistema)
        db.flush()
        
        # 6. REGISTRAR RESULTADOS FINANCIEROS
        nuevos_resultados = ResultadosFinancieros(
            id_sistema_fv=nuevo_sistema.id,
            capex=resultados["capex"],
            opex=resultados["opex"],
            vpn=resultados["vpn"],
            tir=resultados["tir"],
            inversion_inicial=resultados["inversion"]
        )
        db.add(nuevos_resultados)
        
        # 7. CONFIRMAR TRANSACCIÓN
        db.commit()
        
        # 8. PREPARAR RESPUESTA
        es_viable = energia_generada >= datos.consumo_kwh
        
        return RegistroCompletoResponse(
            success=True,
            id_ips=nueva_ips.id,
            ips_registrada=IPSResponse.model_validate(nueva_ips),
            consumo_registrado=ConsumoResponse.model_validate(nuevo_consumo),
            irradiacion_kwh_m2=irradiacion,
            energia_generada_kwh_mes=energia_generada,
            resultados_financieros=ResultadosFinancierosData(**resultados),
            es_viable=es_viable
        )
        
    except Exception as e:
        db.rollback()
        return RegistroCompletoResponse(
            success=False,
            error=f"Error en el registro: {str(e)}"
        )