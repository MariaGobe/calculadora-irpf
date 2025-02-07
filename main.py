from flask import Flask, request, jsonify
import os
import logging

app = Flask(__name__)

# Configuración básica del logger
logging.basicConfig(level=logging.INFO)

def calcular_irpf_2025(salario, estado_civil="soltero", hijos=0, pagas_extra=12, comunidad="nacional"):
    """
    Calcula el salario neto anual y mensual aplicando las retenciones de IRPF 2025 en España.
    
    Parámetros:
        salario (float): Salario bruto anual en euros.
        estado_civil (str): "soltero" o "casado".
        hijos (int): Número de hijos a cargo.
        pagas_extra (int): Número de pagas anuales (12 o 14).
        comunidad (str): Comunidad Autónoma de residencia.
        
    Retorna:
        dict: Desglose de la nómina que incluye:
              - salario_bruto
              - retencion_irpf
              - seguridad_social
              - salario_neto_anual
              - salario_neto_mensual
    """
    
    # Registro de parámetros recibidos
    logging.info(f"Calculando IRPF para: salario={salario}, estado_civil={estado_civil}, hijos={hijos}, pagas_extra={pagas_extra}, comunidad={comunidad}")
    
    # Validación de parámetros
    if pagas_extra not in [12, 14]:
        raise ValueError("El parámetro 'pagas_extra' debe ser 12 o 14.")
    if estado_civil.lower() not in ["soltero", "casado"]:
        raise ValueError("El parámetro 'estado_civil' debe ser 'soltero' o 'casado'.")
    
    # --- Cálculo de IRPF según tramos ---
    tramos = [
        (12450, 0.19),
        (20200, 0.24),
        (35200, 0.3),
        (60000, 0.37),
        (300000, 0.45),
        (float('inf'), 0.47)
    ]
    
    retencion_total = 0
    restante = salario
    for limite, tasa in tramos:
        if restante <= 0:
            break
        tramo = min(restante, limite)
        retencion_total += tramo * tasa
        restante -= tramo

    # Deducción por hijos: se deducen 600€ por cada hijo
    deduccion_hijos = hijos * 600
    retencion_total = max(retencion_total - deduccion_hijos, 0)

    # Ajuste por estado civil: si es casado, se reduce la retención en un 10%
    if estado_civil.lower() == "casado":
        retencion_total *= 0.9

    # Ajuste por comunidad autónoma (ejemplo)
    comunidad_lower = comunidad.lower()
    if comunidad_lower == "cataluña":
        retencion_total *= 0.98  # Reducción del 2%
    elif comunidad_lower == "andalucía":
        retencion_total *= 0.97  # Reducción del 3%
    # Se pueden agregar más ajustes según la normativa específica de cada comunidad

    # --- Cálculo de la Seguridad Social (aportación del trabajador) ---
    seguridad_social = salario * 0.0635

    # --- Cálculo del salario neto ---
    salario_neto = salario - retencion_total - seguridad_social
    salario_neto = max(salario_neto, 0)  # Se evita que el salario neto sea negativo

    # Salario neto mensual (según el número de pagas)
    salario_mensual = salario_neto / pagas_extra

    resultado = {
        "salario_bruto": f"{salario:,.2f}€",
        "retencion_irpf": f"{retencion_total:,.2f}€",
        "seguridad_social": f"{seguridad_social:,.2f}€",
        "salario_neto_anual": f"{salario_neto:,.2f}€",
        "salario_neto_mensual": f"{salario_mensual:,.2f}€"
    }
    
    logging.info(f"Resultado del cálculo: {resultado}")
    return resultado

@app.route('/calcular_irpf', methods=['POST'])
def calcular_irpf():
    try:
        data = request.json
        
        # Extraer parámetros con valores por defecto si no se indican
        salario = data.get('salario')
        estado_civil = data.get('estado_civil', "soltero")
        hijos = data.get('hijos', 0)
        pagas_extra = data.get('pagas_extra', 12)
        comunidad = data.get('comunidad', "nacional")
        
        # Validar que se haya proporcionado el salario
        if salario is None:
            return jsonify({"error": "El parámetro 'salario' es requerido."}), 400

        resultado = calcular_irpf_2025(salario, estado_civil, hijos, pagas_extra, comunidad)
        return jsonify(resultado)
    except Exception as e:
        logging.error(f"Error al calcular IRPF: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
