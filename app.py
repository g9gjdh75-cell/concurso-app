import streamlit as st
import random

# --- Configuração da Página ---
st.set_page_config(page_title="Flashcards Roláveis", layout="centered")

# --- CSS Personalizado para Rolagem Interna ---
# Isso força a caixa do flashcard a ter barra de rolagem se o texto for grande
custom_css = """
<style>
    .flashcard-container {
        background-color: #1e1e1e;
        border-radius: 15px;
        padding: 20px;
        min-height: 300px; /* Altura mínima do cartão */
        max-height: 70vh;  /* Altura máxima: 70% da tela */
        overflow-y: auto;  /* PERMITE ROLAR COM O DEDO AQUI DENTRO */
        border: 1px solid #333;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    
    /* Estiliza a barra de rolagem para ficar discreta no mobile */
    .flashcard-container::-webkit-scrollbar {
        width: 6px;
    }
    .flashcard-container::-webkit-scrollbar-thumb {
        background-color: #555;
        border-radius: 10px;
    }
    
    .card-text {
        font-size: 1.2rem;
        line-height: 1.6;
        color: #ffffff;
        white-space: pre-wrap; /* Mantém quebras de linha */
    }
    
    .label-tag {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-bottom: 10px;
        text-transform: uppercase;
    }
    .tag-front { background-color: #ff9f43; color: #000; }
    .tag-back { background-color: #0abde3; color: #000; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- Banco de Dados de Flashcards (Exemplo) ---
if 'flashcards' not in st.session_state:
    st.session_state.flashcards = [
        {
            "front": "O que é a Tríade CIA em Segurança da Informação?\n\nExplique detalhadamente cada um dos três pilares e dê um exemplo prático de violação de cada um.",
            "back": "A Tríade CIA é composta por:\n\n1. Confidencialidade: Garantir que apenas pessoas autorizadas acessem a informação.\n   *Ex: Vazamento de senhas.*\n\n2. Integridade: Garantir que a informação não foi alterada indevidamente.\n   *Ex: Alteração de notas em um sistema escolar.*\n\n3. Disponibilidade: Garantir que a informação esteja acessível quando needed.\n   *Ex: Ataque DDoS derrubando um site.*"
        },
        {
            "front": "Qual a diferença entre Criptografia Simétrica e Assimétrica?",
            "back": "Simétrica: Usa a MESMA chave para cifrar e decifrar. É mais rápida, mas tem problema de distribuição de chaves.\n\nAssimétrica: Usa um PAR de chaves (Pública e Privada). A pública cifra, a privada decifra. Resolve o problema de distribuição, mas é mais lenta computacionalmente."
        },
        {
            "front": "Descreva o funcionamento do protocolo TCP Handshake (Three-way handshake).",
            "back": "É o processo de estabelecimento de conexão TCP:\n\n1. SYN: O cliente envia um pacote SYN para o servidor.\n2. SYN-ACK: O servidor responde com SYN-ACK.\n3. ACK: O cliente envia ACK final.\n\nApós esses 3 passos, a conexão está estabelecida e a transferência de dados pode começar."
        }
    ]
    st.session_state.current_index = 0
    st.session_state.show_back = False

# --- Lógica do App ---
st.title("🧠 Flashcards Roláveis")
st.caption("Deslize o dedo DENTRO do cartão se o texto for longo!")

card = st.session_state.flashcards[st.session_state.current_index]

# Container principal do cartão com classe CSS personalizada
st.markdown('<div class="flashcard-container">', unsafe_allow_html=True)

if not st.session_state.show_back:
    # FRENTE DO CARTÃO
    st.markdown('<span class="label-tag tag-front">❓ Pergunta / Definição</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="card-text">{card["front"]}</div>', unsafe_allow_html=True)
else:
    # VERSO DO CARTÃO
    st.markdown('<span class="label-tag tag-back"> Resposta</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="card-text">{card["back"]}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True) # Fecha o container rolável

# --- Controles ---
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("⬅️ Anterior", use_container_width=True):
        st.session_state.show_back = False
        st.session_state.current_index = (st.session_state.current_index - 1) % len(st.session_state.flashcards)
        st.rerun()

with col2:
    btn_text = "👀 Ver Resposta" if not st.session_state.show_back else "🔄 Virar Carta"
    if st.button(btn_text, type="primary", use_container_width=True):
        st.session_state.show_back = not st.session_state.show_back
        st.rerun()

with col3:
    if st.button("Próximo ➡️", use_container_width=True):
        st.session_state.show_back = False
        st.session_state.current_index = (st.session_state.current_index + 1) % len(st.session_state.flashcards)
        st.rerun()

# Indicador de progresso
st.progress((st.session_state.current_index + 1) / len(st.session_state.flashcards))
st.caption(f"Cartão {st.session_state.current_index + 1} de {len(st.session_state.flashcards)}")
