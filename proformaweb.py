import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from datetime import datetime

# 🔗 API Flask desplegada en Render
API_URL = "https://raw-dbfc.onrender.com/proforma"

# 🎨 Configuración de la página
st.set_page_config(page_title="Proforma ServiComp", layout="wide")
st.markdown("<h1 style='text-align:center; color:#1e3d59;'>Proforma Digital - ServiComp</h1>", unsafe_allow_html=True)
st.markdown("---")

# 📥 Campo de entrada
codigo = st.text_input("Ingrese el código de proforma (4 dígitos):", max_chars=4)

# ✅ Si se ingresó un código válido
if codigo and len(codigo) == 4 and codigo.isdigit():
    try:
        response = requests.get(f"{API_URL}/{codigo}")
        if response.status_code == 404:
            st.error("❌ No se encontró la proforma solicitada.")
        else:
            # 📄 Cargar Excel desde API
            df = pd.read_excel(BytesIO(response.content))

            # 🔗 Convertir columna FOTO a link clickeable
            if "FOTO" in df.columns:
                df["FOTO"] = df["FOTO"].apply(
                    lambda url: f"<a href='{url}' target='_blank'>🔗 Ver Foto</a>" if pd.notna(url) else "")

            # 📊 Mostrar resultados
            st.markdown("### Resultado de la proforma:")
            st.write(f"📦 Ítems encontrados: {len(df)}")
            st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)

            # 💰 Calcular total
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

    except Exception as e:
        st.error("⚠️ Ocurrió un error al conectarse con el servidor.")
        st.exception(e)

# 🧾 Mensaje inicial
else:
    st.info("Ingrese un código de 4 dígitos para cargar la proforma.")
