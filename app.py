import streamlit as st
import openai
import time
import traceback

from config import OPENAI_API_KEY, AVAILABLE_MODELS
from db import (
    init_db, get_all_assistants, get_assistant_details,
    update_assistant, load_vector_store_map,
)

# --- Initialisation
init_db()
st.set_page_config(page_title="Assistant IA MDF", page_icon="Favicon 48x48.png", layout="wide")

try:
    st.image("logo-png.webp", width=300)
except:
    st.warning("Logo non trouvé.")

st.title("🤖 Assistant IA - Mon Directeur Financier")

# --- Init session
for key, default in {
    "chat_history": [],
    "api_key": "",
    "model": AVAILABLE_MODELS[0],
    "show_settings": False,
    "api_error": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- Page de connexion sécurisée
if not st.session_state.api_key:
    if st.session_state.api_error:
        st.error(f"❌ {st.session_state.api_error}")

    with st.form("connexion", clear_on_submit=True):
        api_key_input = st.text_input("🔑 Clé API OpenAI", type="password")
        submitted = st.form_submit_button("Se connecter")
        if submitted:
            if api_key_input.strip():
                st.session_state.api_key = api_key_input.strip()
                st.session_state.api_error = None
                st.rerun()
            else:
                st.warning("Veuillez entrer votre clé API.")
    st.stop()

# --- Configuration OpenAI
openai.api_key = st.session_state.api_key

# --- Déconnexion
with st.sidebar:
    if st.button("🔓 Se déconnecter"):
        st.session_state.api_key = ""
        st.session_state.api_error = None
        st.rerun()

# --- Chargement des assistants
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
    st.session_state.show_settings = False
    st.success("💬 Nouveau chat démarré.")

# --- Paramètres
st.session_state.show_settings = st.sidebar.checkbox("⚙️ Paramètres avancés", value=st.session_state.show_settings)

if st.session_state.show_settings:
    st.subheader("🔧 Paramétrage des assistants")
    st.success("✅ Clé API chargée.")
    st.markdown("Si besoin, cliquez sur 'Se déconnecter' à gauche.")

    model = st.selectbox("🧠 Choisir un modèle LLM :", AVAILABLE_MODELS, index=AVAILABLE_MODELS.index(st.session_state.model))
    st.session_state.model = model

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
    model = st.session_state.model

# --- Affichage de l’historique
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

        thread = openai.beta.threads.create()
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question
        )

        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=st.session_state.details["id"],
            model=model,
            instructions=st.session_state.details["prompt"]
        )

        with st.spinner("🧠 L'assistant réfléchit..."):
            while True:
                status = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                if status.status == "completed":
                    break
                elif status.status == "failed":
                    st.error("❌ L'exécution a échoué.")
                    st.stop()
                time.sleep(1)

        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                response = msg.content[0].text.value.strip()
                final_response = (
                    "⚠️ Cette demande dépasse mes compétences actuelles."
                    if any(p in response.lower() for p in ["je ne sais pas", "aucune information"])
                    else response
                )
                st.session_state.chat_history.append({"role": "assistant", "content": final_response})
                st.markdown("### ✅ Réponse générée :")
                st.markdown(final_response)
                st.caption(f"📌 Modèle utilisé : `{model}`")

    except openai.AuthenticationError:
        st.session_state.api_key = ""
        st.session_state.api_error = "Clé API invalide. Veuillez la corriger."
        st.rerun()

    except Exception as e:
        st.error("❌ Erreur inattendue")
        st.code(traceback.format_exc())
