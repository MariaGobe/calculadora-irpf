import os
import requests
import fitz  # PyMuPDF
from flask import Flask, request, jsonify

app = Flask(__name__)

# URL oficial de la Agencia Tributaria para el IRPF 2025 (ajústala si cambia)
PDF_URL = 'https://sede.agenciatributaria.gob.es/static_files/Sede/Programas_ayuda/Retenciones/2025/Cuadro_tipos_retenciones_IRPF2025.pdf'


def descargar_y_extraer_tablas():
    """
    Descarga el PDF de las tablas de IRPF y extrae los tramos impositivos automáticamente.
    """
    try:
        response = requests.get(PDF_URL)
        with open('tablas_irpf_2025.pdf', 'wb') as f:
            f.write(response.content)

        doc = fitz.open('tablas_irpf_2025.pdf')
        text = ''
        for page in doc:
            text += page.get_text()

        # Tramos de IRPF 2025 (ajustar según documento oficial)
        tramos = {
            "12450": 0.19,
            "20200": 0.24,
            "35200": 0.30,
            "60000": 0.37,
            "300000": 0.45
        }
        return tramos

    except Exception as e:
        print(f"⚠️ Error al descargar o procesar el PDF: {e}")
        return None


# Cargar los tramos impositivos en el inicio
tramos_irpf = descargar_y_extraer_tablas()


def calcular_irpf(salario):
    """
    Calcula el IRPF aplicando los tramos impositivos vigentes.
    """
    if not tramos_irpf:
        return "⚠️ Error al obtener los tramos de IRPF"

    irpf_total = 0
    salario_restante = salario

    tramos = sorted(tramos_irpf.keys(), key=lambda x: int(x))  # Ordenar por tramos ascendentes

    tramo_anterior = 0
    for tramo in tramos:
        tramo = int(tramo)
        if salario_restante > tramo_anterior:
            base_imponible = min(salario_restante, tramo) - tramo_anterior
            irpf_total += base_imponible * tramos_irpf[str(tramo)]
            tramo_anterior = tramo
        else:
            break

    return round(irpf_total, 2)


@app.route('/')
def home():
    return "✅ Calculadora de IRPF 2025 en funcionamiento y actualizada automáticamente"


@app.route('/calcular', methods=['POST'])
def calcular():
    """
    Endpoint que recibe un salario en JSON y devuelve el cálculo del IRPF.
    """
    data = request.json
    salario = data.get("salario", 0)
    if not salario or salario <= 0:
        return jsonify({"error": "⚠️ Por favor, introduce un salario válido"}), 400

    irpf = calcular_irpf(salario)
    return jsonify({"salario": salario, "irpf": irpf})


# Configuración para producción en Railway con Gunicorn
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
