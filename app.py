import streamlit as st
import requests
import json

# Load API credentials from Streamlit secrets
CLU_ENDPOINT = st.secrets["AZURE_CLU_ENDPOINT"]
CLU_KEY = st.secrets["AZURE_CLU_KEY"]
PROJECT_NAME = st.secrets["CLU_PROJECT_NAME"]
DEPLOYMENT_NAME = st.secrets["CLU_DEPLOYMENT_NAME"]

# 🎨 Configurar la apariencia de la app
st.set_page_config(page_title="Financial AI Assistant", page_icon="💰")

# 📌 Título y descripción
st.markdown("<h1 style='text-align: center;'>💰 Financial AI Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Ask questions about your finances and get smart answers.</p>", unsafe_allow_html=True)

# 📩 Input del usuario con diseño mejorado
user_input = st.text_input("📝 **Ask questions about your finances:**", placeholder="Ejemplo: How much did I earn last month?")

if user_input:
    with st.spinner("⏳ Pensando..."):
        # Azure CLU API request
        headers = {
            "Ocp-Apim-Subscription-Key": CLU_KEY,
            "Content-Type": "application/json"
        }
        body = {
            "kind": "Conversation",
            "analysisInput": {
                "conversationItem": {
                    "id": "1",
                    "participantId": "user",
                    "text": user_input
                }
            },
            "parameters": {
                "projectName": PROJECT_NAME,
                "deploymentName": DEPLOYMENT_NAME
            }
        }
        
        response = requests.post(CLU_ENDPOINT, json=body, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            prediction = result["result"]["prediction"]
            
            intents = prediction["intents"]
            entities = prediction.get("entities", [])

            # 📌 Filtrar intents con confianza alta y elegir el más relevante
            filtered_intents = [(intent["category"], intent["confidenceScore"]) for intent in intents if intent["confidenceScore"] > 0.3]

            # 📌 Ordenar por confianza y seleccionar solo el mejor intent
            if filtered_intents:
                best_intent, best_confidence = sorted(filtered_intents, key=lambda x: x[1], reverse=True)[0]

                # 🎯 Mostrar el intent detectado en un recuadro estilizado
                st.markdown(f"""
                    <div style="border-radius: 10px; padding: 15px; background-color: #1f1f1f; border-left: 6px solid #4CAF50;">
                        <h4>🔍 Detected Intent</h4>
                        <p><b>Intent:</b> {best_intent}</p>
                        <p><b>Confidence:</b> {best_confidence:.2f}</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("⚠ No clear intent detected. Please rephrase your message.")

            # 📌 Mostrar las entidades detectadas con mejor formato
            if entities:
                st.markdown("<h4>📌 Extracted Entities</h4>", unsafe_allow_html=True)
                for entity in entities:
                    st.markdown(f"""
                        <div style="border-radius: 10px; margin:8px; padding: 10px; background-color: #1f1f1f; border-left: 6px solid #2196F3;">
                            <b>Category:</b> {entity['category']} <br>
                            <b>Text:</b> {entity['text']} <br>
                            <b>Offset:</b> {entity['offset']}, <b>Length:</b> {entity['length']}
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("ℹ No entities detected.")
        else:
            st.error(f"❌ Error {response.status_code}: {response.text}")
