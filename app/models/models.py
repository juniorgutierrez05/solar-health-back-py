from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from decimal import Decimal
from app.db_config.database import Base

class Departamento(Base):
    __tablename__ = "departamento"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(50))
    
    # Relaciones
    ciudades = relationship("Ciudad", back_populates="departamento")


class Ciudad(Base):
    __tablename__ = "ciudad"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(50))
    id_departamento = Column(Integer, ForeignKey("departamento.id"))
    
    # Relaciones
    departamento = relationship("Departamento", back_populates="ciudades")
    ips_list = relationship("IPS", back_populates="ciudad")
    irradiaciones = relationship("Irradiacion", back_populates="ciudad")


class IPS(Base):
    __tablename__ = "ips"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100))
    tipo = Column(String(30))
    num_consultorios = Column(Integer)
    num_equipos = Column(Integer)
    id_ciudad = Column(Integer, ForeignKey("ciudad.id"))
    
    # Relaciones
    ciudad = relationship("Ciudad", back_populates="ips_list")
    consumos = relationship("Consumo", back_populates="ips")
    sistemas_fv = relationship("SistemaFV", back_populates="ips")


class Consumo(Base):
    __tablename__ = "consumo"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_ips = Column(Integer, ForeignKey("ips.id"))
    mes = Column(String(15))
    año = Column(Integer)
    consumo_kwh = Column(Numeric(10, 2))
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    ips = relationship("IPS", back_populates="consumos")


class Irradiacion(Base):
    __tablename__ = "irradiacion"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_ciudad = Column(Integer, ForeignKey("ciudad.id"))
    mes = Column(String(15))
    irradiacion_kwh_m2_mes = Column(Numeric(6, 2))
    
    # Relaciones
    ciudad = relationship("Ciudad", back_populates="irradiaciones")


class SistemaFV(Base):
    __tablename__ = "sistema_fv"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_ips = Column(Integer, ForeignKey("ips.id"))
    energia_generada_kwh_mes = Column(Numeric(10, 2))
    
    # Relaciones
    ips = relationship("IPS", back_populates="sistemas_fv")
    resultados_financieros = relationship("ResultadosFinancieros", back_populates="sistema_fv")


class ResultadosFinancieros(Base):
    __tablename__ = "resultados_financieros"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_sistema_fv = Column(Integer, ForeignKey("sistema_fv.id"))
    capex = Column(Numeric(12, 2))
    opex = Column(Numeric(12, 2))
    vpn = Column(Numeric(15, 2))
    tir = Column(Numeric(6, 2))
    inversion_inicial = Column(Numeric(12, 2))
    
    # Relaciones
    sistema_fv = relationship("SistemaFV", back_populates="resultados_financieros")