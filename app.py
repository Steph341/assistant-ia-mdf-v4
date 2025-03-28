import streamlit as st
import openai
import time

from config import OPENAI_API_KEY, AVAILABLE_MODELS
from db import (
    init_db, get_all_assistants, get_assistant_details,
    update_assistant, load_vector_store_map,
    get_vector_store_id_from_name, get_vector_store_name
)

# --- Initialisation
init_db()
st.set_page_config(page_title="Assistant IA MDF", page_icon="Favicon 48x48.png", layout="wide")

try:
    st.image("logo-png.webp", width=300)
except:
    st.warning("Logo non trouvé.")

st.title("🤖 Assistant IA - Mon Directeur Financier")

# --- Données de session
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "api_key" not in st.session_state:
    st.session_state.api_key = OPENAI_API_KEY

if "show_settings" not in st.session_state:
    st.session_state.show_settings = False

# --- Assistant sélectionné
assistant_list = get_all_assistants()
if not assistant_list:
    st.error("Aucun assistant disponible.")
    st.stop()

assistant_name = st.sidebar.selectbox("🧩 Assistant métier", assistant_list)
if "current_assistant" not in st.session_state or st.session_state.current_assistant != assistant_name:
    st.session_state.current_assistant = assistant_name
    st.session_state.chat_history = []
    st.session_state.details = get_assistant_details(assistant_name)

if not st.session_state.details:
    st.error("Assistant introuvable.")
    st.stop()

# --- Nouveau chat
if st.sidebar.button("🆕 Nouveau Chat MDF"):
    st.session_state.chat_history = []
    st.session_state.show_settings = False  # Masquer les paramètres
    st.success("💬 Nouveau chat démarré.")

# --- Paramètres avancés
st.session_state.show_settings = st.sidebar.checkbox("⚙️ Paramètres avancés", value=st.session_state.show_settings)

if st.session_state.show_settings:
    st.subheader("🔧 Paramétrage des assistants")

    # Clé API
    api_key = st.text_input("🔑 Clé API OpenAI", type="password", value=st.session_state.api_key)
    if api_key:
        st.session_state.api_key = api_key
        openai.api_key = api_key
    else:
        st.warning("Veuillez entrer votre clé API.")
        st.stop()

    # Modèle
    model = st.selectbox("🧠 Choisir un modèle LLM :", AVAILABLE_MODELS)
    st.session_state.model = model

    # Prompt + Vector store
    vector_map = load_vector_store_map()
    vector_choices = [f"{name} ({id})" for id, name in vector_map.items()]
    vector_id_to_name = {id: name for id, name in vector_map.items()}

    editable_details = st.session_state.details
    prompt_edit = st.text_area("📝 Prompt système", value=editable_details["prompt"], height=300)

    current_vector_id = editable_details["vector_store_id"]
    current_vector_display = f"{vector_id_to_name.get(current_vector_id, 'Inconnu')} ({current_vector_id})"
    selected_vector_display = st.selectbox(
        "🗃️ Choisir un vector store",
        vector_choices,
        index=vector_choices.index(current_vector_display) if current_vector_display in vector_choices else 0
    )

    if st.button("💾 Sauvegarder les modifications"):
        new_vector_id = selected_vector_display.split("(")[-1].replace(")", "")
        update_assistant(assistant_name, prompt_edit, new_vector_id)
        st.session_state.details = get_assistant_details(assistant_name)
        st.success(f"✅ Assistant « {assistant_name} » mis à jour.")
else:
    openai.api_key = st.session_state.api_key
    model = st.session_state.get("model", AVAILABLE_MODELS[0])

# --- Historique
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f"**🙋‍♂️ {message['content']}**")
    elif message["role"] == "assistant":
        st.markdown(f"🧠 {message['content']}")

# --- Saisie utilisateur
question = st.text_area("💬 Pose ta question ici :", height=150)

if st.button("🚀 Envoyer") and question.strip():
    try:
        st.session_state.chat_history.append({"role": "user", "content": question})

        # Création du thread
        thread = openai.beta.threads.create()
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question
        )

        # Requête sans le paramètre `tools`
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=st.session_state.details["id"],
            model=model,
            instructions=st.session_state.details["prompt"]
        )

        # Attente de complétion
        with st.spinner("🧠 L'assistant réfléchit..."):
            while True:
                status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                if status.status == "completed":
                    break
                elif status.status == "failed":
                    st.error("❌ L'exécution a échoué.")
                    st.stop()
                time.sleep(1)

        # Lecture de la réponse
        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                response = msg.content[0].text.value.strip()

                if any(phrase in response.lower() for phrase in [
                    "je ne sais pas", "je ne trouve pas", "aucune information"
                ]):
                    final_response = "⚠️ Cette demande dépasse mes compétences actuelles. Veuillez reformuler ou vérifier votre base documentaire."
                else:
                    final_response = response

                st.session_state.chat_history.append({"role": "assistant", "content": final_response})
                st.markdown("### ✅ Réponse générée :")
                st.markdown(final_response)
                st.caption(f"📌 Modèle utilisé : `{model}`")

    except Exception as e:
        st.error(f"❌ Erreur : {str(e)}")
