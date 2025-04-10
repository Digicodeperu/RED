import streamlit as st
import pandas as pd
import requests
import base64
from io import BytesIO
from datetime import datetime

# --- CONFIGURACIÓN GITHUB PRIVADO ---
GITHUB_USER = "digicodeperu"
REPO = "raw"
RAMA = "main"
TOKEN = "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"

# Configuración visual
st.set_page_config(page_title="Proforma ServiComp", layout="wide")
st.markdown("<h1 style='text-align:center; color:#1e3d59;'>Proforma Digital - ServiComp</h1>", unsafe_allow_html=True)
st.markdown("---")

# Entrada del código
codigo = st.text_input("Ingrese el código de proforma (4 dígitos):", max_chars=4)

if codigo and len(codigo) == 4 and codigo.isdigit():
    nombre_archivo = f"{codigo}.xlsx"
    url_api = f"https://api.github.com/repos/{GITHUB_USER}/{REPO}/contents/{nombre_archivo}?ref={RAMA}"

    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    try:
        r = requests.get(url_api, headers=headers)
        r.raise_for_status()

        contenido = r.json().get("content", "")
        binario = base64.b64decode(contenido)
        df = pd.read_excel(BytesIO(binario))

        # Procesar columna FOTO como link
        if "FOTO" in df.columns:
            df["FOTO"] = df["FOTO"].apply(
                lambda url: f"<a href='{url}' target='_blank'>🔗 Ver Foto</a>" if pd.notna(url) else "")

        # Mostrar resultados
        st.markdown("### Resultado de la proforma:")
        st.write("📦 Ítems encontrados:", len(df))

        # Mostrar tabla como HTML
        st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)

        # Calcular total DISTRIB
        total = 0
        for v in df.get("DISTRIB", []):
            try:
                valor = str(v).replace("S/.", "").replace(",", "").strip()
                total += int(valor)
            except:
                continue

        st.markdown(f"### 💰 Total general: S/. {total:,}")
        st.markdown(f"🕒 Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        st.markdown("---")
        st.markdown("<p style='text-align: center; color: gray;'>Gracias por su preferencia – ServiComp ©</p>",
                    unsafe_allow_html=True)

    except requests.exceptions.HTTPError:
        st.error("No se encontró la proforma solicitada.")
    except Exception as e:
        st.error("Ocurrió un error inesperado al cargar la proforma.")
        st.exception(e)

else:
    st.info("Ingrese un código de 4 dígitos para cargar la proforma.")
