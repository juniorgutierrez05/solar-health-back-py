from decimal import Decimal, ROUND_HALF_UP
from typing import Dict

# CONSTANTES PARA CÁLCULOS
COSTO_KWH = Decimal("0.18")
VIDA_UTIL_SISTEMA = 25
TASA_DESCUENTO = Decimal("0.08")
EFICIENCIA_SISTEMA = Decimal("0.85")
AREA_PANEL = Decimal("1.6")
POTENCIA_PANEL = Decimal("0.5")

class CalculadoraFinanciera:
    
    @staticmethod
    def calcular_area_disponible(num_consultorios: int, num_equipos: int) -> Decimal:
        """Calcula el área disponible para instalar paneles solares"""
        area_base = Decimal(str(num_consultorios)) * Decimal("20.0")
        area_equipos = Decimal(str(num_equipos)) * Decimal("5.0")
        area_total = area_base + area_equipos
        
        # Solo el 60% del área es usable para paneles
        return area_total * Decimal("0.6")
    
    @staticmethod
    def calcular_energia_generada(
        num_consultorios: int,
        num_equipos: int,
        irradiacion: Decimal
    ) -> Dict[str, any]:
        """Calcula la energía generada por el sistema fotovoltaico"""
        
        # 1. Calcular área disponible
        area_disponible = CalculadoraFinanciera.calcular_area_disponible(
            num_consultorios, num_equipos
        )
        
        # 2. Calcular número de paneles
        num_paneles = int(area_disponible / AREA_PANEL)
        
        # 3. Calcular potencia instalada
        potencia_instalada = POTENCIA_PANEL * Decimal(str(num_paneles))
        
        # 4. Calcular energía generada mensual
        energia_generada_mensual = (
            potencia_instalada * irradiacion * EFICIENCIA_SISTEMA
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        
        return {
            "energia_generada": energia_generada_mensual,
            "num_paneles": num_paneles,
            "potencia_instalada": potencia_instalada.quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
            "area_utilizada": area_disponible.quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        }
    
    @staticmethod
    def calcular_capex(num_paneles: int, potencia_instalada: Decimal) -> Decimal:
        """Calcula el CAPEX (inversión inicial)"""
        costo_paneles = Decimal(str(num_paneles)) * Decimal("300")
        costo_inversor = potencia_instalada * Decimal("800")
        costo_instalacion = (costo_paneles + costo_inversor) * Decimal("0.3")
        
        capex = costo_paneles + costo_inversor + costo_instalacion
        return capex.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calcular_opex(capex: Decimal) -> Decimal:
        """Calcula el OPEX (costos operacionales anuales)"""
        return (capex * Decimal("0.015")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    
    @staticmethod
    def calcular_ahorro_anual(consumo: Decimal, generacion: Decimal) -> Decimal:
        """Calcula el ahorro anual en costos de energía"""
        energia_autoconsumida = min(consumo, generacion)
        ahorro_anual = energia_autoconsumida * COSTO_KWH * Decimal("12")
        return ahorro_anual.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calcular_vpn(capex: Decimal, opex: Decimal, ahorro_anual: Decimal) -> Decimal:
        """Calcula el Valor Presente Neto"""
        vpn = -capex
        
        for año in range(1, VIDA_UTIL_SISTEMA + 1):
            flujo_anual = ahorro_anual - opex
            factor_descuento = (Decimal("1") + TASA_DESCUENTO) ** año
            flujo_descontado = flujo_anual / factor_descuento
            vpn += flujo_descontado
        
        return vpn.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calcular_tir(capex: Decimal, ahorro_anual: Decimal, opex: Decimal) -> Decimal:
        """Calcula la Tasa Interna de Retorno (simplificada)"""
        flujo_anual_neto = ahorro_anual - opex
        
        if capex == 0:
            return Decimal("0")
        
        tir = (flujo_anual_neto / capex) * Decimal("100")
        return tir.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calcular_periodo_retorno(
        capex: Decimal, 
        ahorro_anual: Decimal, 
        opex: Decimal
    ) -> Decimal:
        """Calcula el período de retorno de la inversión"""
        flujo_anual_neto = ahorro_anual - opex
        
        if flujo_anual_neto <= 0:
            return Decimal("999")
        
        periodo_retorno = capex / flujo_anual_neto
        return periodo_retorno.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    @staticmethod
    def calcular_resultados_completos(
        num_consultorios: int,
        num_equipos: int,
        consumo: Decimal,
        irradiacion: Decimal
    ) -> Dict[str, any]:
        """Calcula todos los resultados financieros"""
        
        # 1. Calcular energía generada
        datos_energia = CalculadoraFinanciera.calcular_energia_generada(
            num_consultorios, num_equipos, irradiacion
        )
        
        energia_generada = datos_energia["energia_generada"]
        num_paneles = datos_energia["num_paneles"]
        potencia_instalada = datos_energia["potencia_instalada"]
        area_utilizada = datos_energia["area_utilizada"]
        
        # 2. Calcular CAPEX y OPEX
        capex = CalculadoraFinanciera.calcular_capex(num_paneles, potencia_instalada)
        opex = CalculadoraFinanciera.calcular_opex(capex)
        
        # 3. Calcular ahorro anual
        ahorro_anual = CalculadoraFinanciera.calcular_ahorro_anual(
            consumo, energia_generada
        )
        
        # 4. Calcular indicadores financieros
        vpn = CalculadoraFinanciera.calcular_vpn(capex, opex, ahorro_anual)
        tir = CalculadoraFinanciera.calcular_tir(capex, ahorro_anual, opex)
        periodo_retorno = CalculadoraFinanciera.calcular_periodo_retorno(
            capex, ahorro_anual, opex
        )
        
        return {
            "capex": capex,
            "opex": opex,
            "vpn": vpn,
            "tir": tir,
            "inversion": capex,
            "ahorro_anual": ahorro_anual,
            "periodo_retorno": periodo_retorno,
            "num_paneles": num_paneles,
            "potencia_instalada_kw": potencia_instalada,
            "area_utilizada_m2": area_utilizada,
            "irradiacion_utilizada": irradiacion,
            "energia_generada": energia_generada
        }