import streamlit as st
import json
from datetime import datetime

# --- Configuração da Página ---
st.set_page_config(page_title="Flashcards AI Roláveis", layout="centered")

# --- CSS Personalizado para Rolagem Interna ---
custom_css = """
<style>
    .flashcard-container {
        background-color: #1e1e1e;
        border-radius: 15px;
        padding: 20px;
        min-height: 300px;
        max-height: 65vh; /* Altura máxima para caber botões na tela */
        overflow-y: auto; /* ROLAGEM INTERNA ATIVADA */
        border: 1px solid #333;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    .flashcard-container::-webkit-scrollbar { width: 6px; }
    .flashcard-container::-webkit-scrollbar-thumb { background-color: #555; border-radius: 10px; }
    
    .card-text { font-size: 1.2rem; line-height: 1.6; color: #ffffff; white-space: pre-wrap; }
    
    .label-tag { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; margin-bottom: 10px; text-transform: uppercase; }
    .tag-front { background-color: #ff9f43; color: #000; }
    .tag-back { background-color: #0abde3; color: #000; }
    
    .set-card { 
        background-color: #2a2a2a; border-radius: 10px; padding: 15px; 
        margin-bottom: 10px; cursor: pointer; border: 1px solid #444;
        transition: all 0.2s;
    }
    .set-card:hover { border-color: #0abde3; background-color: #333; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- Inicialização do Estado ---
if 'sets' not in st.session_state:
    st.session_state.sets = {}
if 'current_set' not in st.session_state:
    st.session_state.current_set = None
if 'card_index' not in st.session_state:
    st.session_state.card_index = 0
if 'show_back' not in st.session_state:
    st.session_state.show_back = False
if 'page' not in st.session_state:
    st.session_state.page = "home" # home, create, study

# --- Funções Auxiliares ---
def save_sets_to_json():
    return json.dumps(st.session_state.sets, indent=2, ensure_ascii=False)

def load_sets_from_json(json_str):
    try:
        data = json.loads(json_str)
        st.session_state.sets.update(data)
        st.success("Sets carregados com sucesso!")
        st.rerun()
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {e}")

# --- PÁGINA INICIAL (GERENCIADOR DE SETS) ---
if st.session_state.page == "home":
    st.title("📚 Meus Conjuntos de Flashcards")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("➕ Criar Novo Set", use_container_width=True, type="primary"):
            st.session_state.page = "create"
            st.rerun()
    with col_btn2:
        uploaded_file = st.file_uploader(" Importar Sets (JSON)", type=["json"], label_visibility="collapsed")
        if uploaded_file is not None:
            load_sets_from_json(uploaded_file.read().decode("utf-8"))

    st.divider()
    
    if not st.session_state.sets:
        st.info("Nenhum conjunto criado ainda. Clique em 'Criar Novo Set' ou importe um arquivo JSON.")
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
                    st.rerun()

    # Botão de Exportar Geral
    if st.session_state.sets:
        st.download_button(
            label="💾 Baixar Todos os Sets (Backup)",
            data=save_sets_to_json(),
            file_name=f"meus_flashcards_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )

# --- PÁGINA DE CRIAÇÃO DE SET ---
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
                st.success("Cartão adicionado! Continue adicionando ou volte para estudar.")
                st.rerun()
            else:
                st.warning("Preencha todos os campos!")
    with col_c3:
        if st.button("✅ Finalizar Set", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

# --- PÁGINA DE ESTUDO (FLASHCARD COM ROLAGEM) ---
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
        
        # CONTAINER COM ROLAGEM INTERNA
        st.markdown('<div class="flashcard-container">', unsafe_allow_html=True)
        
        if not st.session_state.show_back:
            st.markdown('<span class="label-tag tag-front">❓ Pergunta / Definição</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="card-text">{card["front"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="label-tag tag-back"> Resposta</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="card-text">{card["back"]}</div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Controles de Navegação
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("⬅️ Anterior", use_container_width=True):
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
