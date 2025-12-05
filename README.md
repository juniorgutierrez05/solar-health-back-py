# Backend de Solar Health

Este proyecto ofrece un **backend en Python** para evaluar la viabilidad financiera de instalar sistemas de paneles solares en centros de salud. Incluye un modelo financiero completo que calcula:

- Área disponible del techo según el número de consultorios y equipos.
- Potencial de generación de energía usando datos de irradiación solar.
- Gastos de capital (CAPEX) y gastos operacionales (OPEX).
- Ahorro anual, Valor Presente Neto (VPN), Tasa Interna de Retorno (TIR) y período de retorno de la inversión.

La lógica principal se encuentra en `app/calculadora_financiera.py`, que expone métodos estáticos para realizar los cálculos. El backend puede integrarse con un servicio FastAPI (ver `main.py`) para ofrecer estos insights financieros a través de endpoints REST.

## Inicio rápido

1. Instale las dependencias (FastAPI, Uvicorn, etc.).
2. Ejecute la API con `uvicorn main:app --reload`.

El repositorio está estructurado para ser fácilmente extensible a nuevos modelos de energía o parámetros de costo.
