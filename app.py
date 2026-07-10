import streamlit as st
from streamlit_local_storage import LocalStorage
import json

# --- Configuração da Página ---
st.set_page_config(page_title="Flashcards AI Persistentes", layout="centered")

# --- CSS Personalizado para Rolagem Interna ---
custom_css = """
<style>
    .flashcard-container {
        background-color: #1e1e1e; border-radius: 15px; padding: 20px;
        min-height: 300px; max-height: 65vh; overflow-y: auto;
        border: 1px solid #333; box-shadow: 0 4px 6px rgba(0,0,0,0.3); margin-bottom: 20px;
    }
    .flashcard-container::-webkit-scrollbar { width: 6px; }
    .flashcard-container::-webkit-scrollbar-thumb { background-color: #555; border-radius: 10px; }
    .card-text { font-size: 1.2rem; line-height: 1.6; color: #ffffff; white-space: pre-wrap; }
    .label-tag { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; }
    .tag-front { background-color: #ff9f43; color: #000; }
    .tag-back { background-color: #0abde3; color: #000; }
    .set-card { 
        background-color: #2a2a2a; border-radius: 10px; padding: 15px; 
        margin-bottom: 10px; cursor: pointer; border: 1px solid #444; transition: all 0.2s;
    }
    .set-card:hover { border-color: #0abde3; background-color: #333; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- Inicialização com LocalStorage ---
local_store = LocalStorage()
STORAGE_KEY = "meus_flashcards_ai_v1"

if 'sets' not in st.session_state:
    saved_data = local_store.getItem(STORAGE_KEY)
    if saved_data:
        try:
            st.session_state.sets = json.loads(saved_data)
        except:
            st.session_state.sets = {}
    else:
        st.session_state.sets = {}

def save_to_local():
    local_store.setItem(STORAGE_KEY, json.dumps(st.session_state.sets))

# --- Estado de Navegação ---
if 'page' not in st.session_state: st.session_state.page = "home"
if 'current_set' not in st.session_state: st.session_state.current_set = None
if 'card_index' not in st.session_state: st.session_state.card_index = 0
if 'show_back' not in st.session_state: st.session_state.show_back = False

# --- PÁGINA INICIAL ---
if st.session_state.page == "home":
    st.title("📚 Meus Conjuntos de Flashcards")
    st.caption("Seus sets são salvos automaticamente neste dispositivo!")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button(" Criar Novo Set", use_container_width=True, type="primary"):
            st.session_state.page = "create"
            st.rerun()
    with col_btn2:
        if st.button("🗑️ Limpar Todos os Dados", use_container_width=True):
            local_store.removeItem(STORAGE_KEY)
            st.session_state.sets = {}
            st.success("Todos os dados foram apagados deste dispositivo.")
            st.rerun()

    st.divider()
    
    if not st.session_state.sets:
        st.info("Nenhum conjunto criado ainda. Clique em 'Criar Novo Set'.")
    else:
        for set_name, cards in st.session_state.sets.items():
            cols = st.columns([4, 1])
            with cols[0]:
                st.markdown(f'<div class="set-card"><b>{set_name}</b><br><small>{len(cards)} cartões</small></div>', unsafe_allow_html=True)
                if st.button(f"Estudar: {set_name}", key=f"study_{set_name}"):
                    st.session_state.current_set = set_name
                    st.session_state.card_index = 0
                    st.session_state.show_back = False
                    st.session_state.page = "study"
                    st.rerun()
            with cols[1]:
                if st.button("🗑️", key=f"del_{set_name}"):
                    del st.session_state.sets[set_name]
                    save_to_local()
                    st.rerun()

# --- PÁGINA DE CRIAÇÃO ---
elif st.session_state.page == "create":
    st.title("✏️ Criar Novo Conjunto")
    
    set_name = st.text_input("Nome do Conjunto:", placeholder="Ex: Direito Constitucional - Aula 1")
    front = st.text_area("Frente (Pergunta/Definição):", height=100, placeholder="Cole aqui o texto da IA...")
    back = st.text_area("Verso (Resposta):", height=150, placeholder="Cole aqui a resposta detalhada...")
    
    col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
    with col_c1:
        if st.button("⬅️ Voltar", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
    with col_c2:
        if st.button(" Adicionar Cartão", type="primary", use_container_width=True):
            if set_name and front and back:
                if set_name not in st.session_state.sets:
                    st.session_state.sets[set_name] = []
                st.session_state.sets[set_name].append({"front": front, "back": back})
                save_to_local() # SALVA AUTOMATICAMENTE
                st.success("Cartão adicionado e salvo!")
                st.rerun()
            else:
                st.warning("Preencha todos os campos!")
    with col_c3:
        if st.button("✅ Finalizar Set", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

# --- PÁGINA DE ESTUDO ---
elif st.session_state.page == "study":
    set_name = st.session_state.current_set
    cards = st.session_state.sets.get(set_name, [])
    
    if not cards:
        st.warning("Este conjunto está vazio.")
        if st.button("Voltar"):
            st.session_state.page = "home"
            st.rerun()
    else:
        st.header(f"🧠 Estudando: {set_name}")
        
        card = cards[st.session_state.card_index]
        
        st.markdown('<div class="flashcard-container">', unsafe_allow_html=True)
        if not st.session_state.show_back:
            st.markdown('<span class="label-tag tag-front">❓ Pergunta / Definição</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="card-text">{card["front"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="label-tag tag-back">✅ Resposta</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="card-text">{card["back"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("️ Anterior", use_container_width=True):
                st.session_state.show_back = False
                st.session_state.card_index = (st.session_state.card_index - 1) % len(cards)
                st.rerun()
        with col2:
            btn_text = "👀 Ver Resposta" if not st.session_state.show_back else "🔄 Virar Carta"
            if st.button(btn_text, type="primary", use_container_width=True):
                st.session_state.show_back = not st.session_state.show_back
                st.rerun()
        with col3:
            if st.button("Próximo ➡️", use_container_width=True):
                st.session_state.show_back = False
                st.session_state.card_index = (st.session_state.card_index + 1) % len(cards)
                st.rerun()
                
        st.progress((st.session_state.card_index + 1) / len(cards))
        
        if st.button("🏠 Sair do Estudo", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
