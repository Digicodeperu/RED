from flask import Flask, request, jsonify, send_file
import requests
import base64
import pandas as pd
from io import BytesIO
import os

# --- CONFIGURACIÓN ---
TOKEN = os.environ.get("GITHUB_TOKEN")  # Se lee desde el entorno seguro en Render
GITHUB_USER = "digicodeperu"
REPO = "raw"           # Nombre del repo donde están los .xlsx
BRANCH = "main"        # Rama del repo privado donde subís los archivos

app = Flask(__name__)

@app.route("/proforma/<codigo>", methods=["GET"])
def obtener_proforma(codigo):
    if not codigo.isdigit() or len(codigo) != 4:
        return jsonify({"error": "Código inválido. Debe tener 4 dígitos."}), 400

    nombre_archivo = f"{codigo}.xlsx"
    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO}/contents/{nombre_archivo}?ref={BRANCH}"

    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()

        contenido = r.json().get("content", "")
        binario = base64.b64decode(contenido)

        return send_file(BytesIO(binario),
                         download_name=nombre_archivo,
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    except requests.exceptions.HTTPError:
        return jsonify({"error": "Proforma no encontrada."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Render necesita que Flask escuche el puerto desde una variable de entorno
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
