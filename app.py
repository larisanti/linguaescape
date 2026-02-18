import streamlit as st
import os
import time
from PIL import Image
from schemas import ExerciseRequest
from services import generate_exercises
from utils.pdf_generator import generate_pdf_bytes
from streamlit_extras.stylable_container import stylable_container

# Configurações da página
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(BASE_DIR, "images", "logotipos", "5.png")
try:
    page_logo = Image.open(icon_path)
except FileNotFoundError:
    page_logo = "📙"

st.set_page_config(
    page_title="Linguaescape | Exercise Generator",
    page_icon=page_logo,
    layout="centered"
)

st.markdown("""
    <style>
        /* Tenta desativar o preenchimento automático nos inputs */
        input {
            autocomplete: off;
        }
    </style>
""", unsafe_allow_html=True)

# CSS global
st.markdown("""
<style>
    /* Remove a borda padrão do formulário para o layout ficar limpo */
    [data-testid="stForm"] {
        border: none !important;
        padding-bottom: 0 !important;
    }
</style>
""", unsafe_allow_html=True)


# Header
logo_path = os.path.join(BASE_DIR, "images", "logotipos", "2.png")

col_vazia1, col_logo, col_vazia2 = st.columns([1, 2, 1])
with col_logo:
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        st.title("Linguaescape")

st.markdown("<p style='text-align: center; color: gray; font-size: 1.1em;'>Generate high-quality, CEFR-aligned English exercises in seconds.</p>", unsafe_allow_html=True)
st.divider()

# Input form
with st.form("exercise_generator_form"):
    
    st.subheader("1. General Context")
    
    col1, col2 = st.columns(2)
    with col1:
        theme = st.text_input(
            "Theme or Context", 
            placeholder="e.g., Technology, Job Interview, Travel"
        )
    with col2:
        topic = st.text_input(
            "Grammar or Target Vocabulary", 
            placeholder="e.g., Future with Will, Phrasal Verbs"
        )
        
    col3, col4 = st.columns(2)
    with col3:
        level = st.selectbox(
            "CEFR Level", 
            ["A1", "A2", "B1", "B2", "C1", "C2"],
            index=None,
            placeholder="Select a level..."
        )
    with col4:
        age_group = st.selectbox(
            "Target Audience", 
            ["Kids", "Teens", "Adults"],
            index=None,
            placeholder="Select age group..."
        )
        
    st.divider()
    
    st.subheader("2. Exercise Configuration")
    st.markdown("Choose how many exercise blocks you want and the number of questions per block.")
    
    col_gf1, col_gf2 = st.columns(2)
    with col_gf1:
        gf_count = st.number_input("Gap Fill", min_value=0, max_value=5, value=0)
    with col_gf2:
        gf_items = st.slider("Sentences per Gap Fill Block", min_value=0, max_value=10, value=0)
        
    col_sf1, col_sf2 = st.columns(2)
    with col_sf1:
        sf_count = st.number_input("Sentence Formation", min_value=0, max_value=5, value=0)
    with col_sf2:
        sf_items = st.slider("Items per Sentence Formation", min_value=0, max_value=10, value=0)
        
    col_mc1, col_mc2 = st.columns(2)
    with col_mc1:
        mc_count = st.number_input("Multiple Choice", min_value=0, max_value=5, value=0)
    with col_mc2:
        mc_items = st.slider("Questions per Multiple Choice", min_value=0, max_value=10, value=0)
        
    st.divider()
    
    st.subheader("3. Vocabulary Focus (Optional)")
    required_words_input = st.text_input(
        "Mandatory words to include (comma-separated)", 
        placeholder="e.g., algorithm, network, database, server"
    )
    
    # Botão: GENERATE EXERCISES
    col_btn_left, col_btn_center, col_btn_right = st.columns([1, 2, 1])
    
    with col_btn_center:
        with stylable_container(
            key="rainbow_button",
            css_styles="""
            button {
                color: #FFF !important;
                font-weight: bold;
                font-size: 1.2em;
                text-transform: uppercase;
                letter-spacing: 1px;
                /* Espessura reduzida para 2px */
                border: 2px solid transparent !important;
                border-radius: 5px;
                background: 
                    linear-gradient(#191919, #191919) padding-box,
                    linear-gradient(90deg, #ff0000, #ff7f00, #ffff00, #00ff00, #0000ff, #4b0082, #9400d3, #ff0000) border-box !important;
                background-size: 100% 100%, 200% 100% !important;
                background-position: 0% 0%, 0% 0%;
                transition: transform 0.1s ease, box-shadow 0.1s ease;
            }
            button:hover {
                animation: slidebg 2s linear infinite !important;
                transform: scale(1.02);
            }
            /* O brilho branco esfumaçado só aparece no clique */
            button:active {
                transform: scale(0.98);
                box-shadow: 0 0 20px rgba(255, 255, 255, 0.8) !important;
            }
            @keyframes slidebg {
                to {
                    background-position: 0% 0%, 200% 0%;
                }
            }
            """
        ):
            submitted = st.form_submit_button("✨ Generate Exercises ✨", use_container_width=True)

# Lógica de backend para processar a requisição e gerar o PDF
download_placeholder = st.empty()

if submitted:
    if not theme or not topic or not level or not age_group:
        st.error("⚠️ Please fill in Theme, Topic, Level, and Target Audience before generating.")
    elif (gf_count + sf_count + mc_count) == 0:
        st.error("⚠️ Please request at least one block of exercises.")
    elif (gf_count + sf_count + mc_count) > 10:
        st.error("⚠️ Too many exercise blocks! The maximum total is 10.")
    elif (gf_count > 0 and gf_items == 0) or (sf_count > 0 and sf_items == 0) or (mc_count > 0 and mc_items == 0):
        st.error("⚠️ You selected an exercise block but left the number of questions at 0. Please adjust the items per block using the slider.")
    else:
        time.sleep(1) 

        req_words_list = None
        if required_words_input.strip():
            req_words_list = [w.strip() for w in required_words_input.split(",") if w.strip()]
        
        request_data = ExerciseRequest(
            theme=theme,
            topic=topic,
            level=level,
            age_group=age_group,
            gap_fill_count=gf_count,
            gap_fill_items=gf_items,
            sentence_formation_count=sf_count,
            sentence_formation_items=sf_items,
            multiple_choice_count=mc_count,
            multiple_choice_items=mc_items,
            required_words=req_words_list
        )
        
        with st.spinner("Analyzing CEFR rules and generating exercises..."):
            try:
                ai_response = generate_exercises(request_data)
                pdf_bytes = generate_pdf_bytes(ai_response)
                
                st.session_state['pdf_bytes'] = pdf_bytes
                
                clean_title = ai_response.title.replace(" - ", "_").replace(" ", "_").lower()
                st.session_state['pdf_filename'] = f"linguaescape_{clean_title}.pdf"
                
            except Exception as e:
                st.error(f"❌ An error occurred during generation: {str(e)}")

# Botão: DOWNLOAD
if 'pdf_bytes' in st.session_state:
    with download_placeholder.container():
        
        # Espaçamento entre os botões
        st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
        
        col_dl_left, col_dl_center, col_dl_right = st.columns([1, 2, 1])
        
        with col_dl_center:
            with stylable_container(
                key="orange_download_button",
                css_styles="""
                button {
                    background-color: #f24405 !important;
                    color: white !important;
                    font-weight: 800; 
                    font-size: 1.2em; 
                    text-transform: uppercase; 
                    letter-spacing: 1px; 
                    border: none !important;
                    border-radius: 5px; 
                    transition: transform 0.1s ease, box-shadow 0.1s ease, filter 0.2s ease; 
                }
                button:hover {
                    transform: scale(1.02); 
                    filter: brightness(1.1);
                }
                /* O brilho branco esfumaçado só aparece no clique */
                button:active {
                    transform: scale(0.98);
                    box-shadow: 0 0 20px rgba(255, 255, 255, 0.8) !important;
                }
                """
            ):
                st.download_button(
                    label="Download",
                    data=st.session_state['pdf_bytes'],
                    file_name=st.session_state['pdf_filename'],
                    mime="application/pdf",
                    use_container_width=True
                )