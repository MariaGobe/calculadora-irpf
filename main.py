from flask import Flask, request, jsonify
import os

app = Flask(__name__)

def calcular_irpf_2025(salario, estado_civil="soltero", hijos=0, pagas_extra=12, comunidad="nacional"):
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

    deduccion_hijos = hijos * 600
    retencion_total = max(retencion_total - deduccion_hijos, 0)

    if estado_civil.lower() == "casado":
        retencion_total *= 0.9

    seguridad_social = salario * 0.0635
    salario_neto = salario - retencion_total - seguridad_social
    salario_mensual = salario_neto / pagas_extra

    return {
        "salario_bruto": f"{salario:,.2f}€",
        "retencion_irpf": f"{retencion_total:,.2f}€",
        "seguridad_social": f"{seguridad_social:,.2f}€",
        "salario_neto_anual": f"{salario_neto:,.2f}€",
        "salario_neto_mensual": f"{salario_mensual:,.2f}€"
    }

@app.route('/calcular_irpf', methods=['POST'])
def calcular_irpf():
    data = request.json
    resultado = calcular_irpf_2025(
        data['salario'],
        data['estado_civil'],
        data['hijos'],
        data['pagas_extra'],
        data['comunidad']
    )
    return jsonify(resultado)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
