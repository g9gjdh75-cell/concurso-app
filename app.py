import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import json
import re

# Configuração da Página
st.set_page_config(page_title="ConcursoMaster AI - Tríade", layout="wide")

st.markdown("""
<style>
    .stButton { width: 100%; }
    .flashcard { border: 1px solid #ddd; padding: 20px; margin: 10px 0; border-radius: 10px; background-color: #f9f9f9; }
    .consensus-box { background-color: #e6ffe6; border-left: 5px solid #28a745; padding: 15px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- Configuração das 3 IAs ---
def init_apis():
    keys = ['gemini_key', 'openai_key', 'qwen_key']
    if not all(k in st.session_state for k in keys):
        st.sidebar.header("⚙️ Configuração das APIs")
        st.session_state['gemini_key'] = st.sidebar.text_input("Chave Google Gemini", type="password")
        st.session_state['openai_key'] = st.sidebar.text_input("Chave OpenAI (GPT)", type="password")
        st.session_state['qwen_key'] = st.sidebar.text_input("Chave Alibaba Qwen (DashScope)", type="password")
        
        if all(st.session_state[k] for k in keys):
            # Inicializar Gemini
            genai.configure(api_key=st.session_state['gemini_key'])
            st.session_state['gemini_model'] = genai.GenerativeModel('gemini-1.5-flash')
            
            # Inicializar OpenAI (GPT)
            st.session_state['gpt_client'] = OpenAI(api_key=st.session_state['openai_key'])
            
            # Inicializar Qwen (via OpenAI compatible endpoint da Alibaba/DashScope)
            st.session_state['qwen_client'] = OpenAI(
                api_key=st.session_state['qwen_key'],
                base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
            )
            st.success("✅ Tríade de IAs Conectada!")
        else:
            st.warning("Preencha as 3 chaves de API na barra lateral.")
            return False
    return True

# --- Lógica de Geração e Validação Cruzada ---

def gerar_questao_base(banca, cargo, nivel, edital_texto):
    """Gera a questão inicial usando o Gemini."""
    prompt = f"""
    Crie 1 questão de concurso para a banca {banca}, cargo {cargo} ({nivel}).
    Use o seguinte contexto do edital: {edital_texto[:1000]}...
    
    Formato JSON estrito:
    {{
      "enunciado": "...",
      "alternativas": ["A) ...", "B) ..."],
      "tipo": "multipla_escolha",
      "gabarito_sugerido": "A",
      "justificativa_inicial": "..."
    }}
    """
    try:
        response = st.session_state['gemini_model'].generate_content(prompt)
        text = response.text
        json_str = re.search(r'\{.*\}', text, re.DOTALL).group()
        return json.loads(json_str)
    except Exception as e:
        return None

def validar_ia(model_name, client_or_model, questao_json, banca):
    """Função genérica para validar uma questão com qualquer IA."""
    prompt = f"""
    Você é um auditor da banca {banca}. Analise esta questão:
    {json.dumps(questao_json, ensure_ascii=False)}
    
    O gabarito '{questao_json['gabarito_sugerido']}' está correto?
    Responda APENAS com JSON: {{"valido": true/false, "gabarito_correto": "Letra", "comentario": "..."}}
    """
    
    try:
        if model_name == "gemini":
            response = client_or_model.generate_content(prompt)
            text = response.text
        else: # OpenAI ou Qwen
            response = client_or_model.chat.completions.create(
                model="gpt-4o-mini" if model_name == "gpt" else "qwen-plus",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            text = response.choices[0].message.content
            
        json_str = re.search(r'\{.*\}', text, re.DOTALL).group()
        return json.loads(json_str)
    except:
        return {"valido": False, "comentario": "Erro de conexão"}

def tribunal_de_ias(questao_base, banca, edital_texto):
    """Realiza a validação cruzada entre as 3 IAs."""
    resultados = {}
    
    # 1. Validação do GPT-4o
    st.caption("🤖 GPT-4o analisando...")
    resultados['gpt'] = validar_ia("gpt", st.session_state['gpt_client'], questao_base, banca)
    
    # 2. Validação do Qwen
    st.caption("🤖 Qwen analisando...")
    resultados['qwen'] = validar_ia("qwen", st.session_state['qwen_client'], questao_base, banca)
    
    # 3. Validação do Gemini (Auditoria)
    st.caption("🤖 Gemini auditando...")
    resultados['gemini'] = validar_ia("gemini", st.session_state['gemini_model'], questao_base, banca)
    
    # Lógica de Consenso Total
    votos_corretos = sum(1 for r in resultados.values() if r.get('valido'))
    
    if votos_corretos == 3:
        questao_base['status'] = "✅ CONSENSO TOTAL (3/3)"
        questao_base['resolucao_final'] = "Validado por GPT-4o, Qwen e Gemini."
        return questao_base
    else:
        # Se não houver consenso total, tentamos ajustar com o gabarito majoritário ou descartamos
        questao_base['status'] = f"⚠️ SEM CONSENSO ({votos_corretos}/3)"
        questao_base['resolucao_final'] = "Questão descartada ou requer revisão humana."
        return None

# --- Interface Principal ---

def main():
    st.title("⚖️ ConcursoMaster AI - Tribunal de 3 IAs")
    
    if not init_apis():
        return

    tab1, tab2, tab3 = st.tabs(["📝 Gerar Simulado", "✅ Realizar Prova", "🃏 Flashcards"])

    with tab1:
        st.header("Configuração do Simulado")
        col1, col2 = st.columns(2)
        with col1:
            banca = st.selectbox("Banca", ["Cebraspe", "FGV", "Vunesp", "IBFC"])
            cargo = st.text_input("Cargo")
            nivel = st.selectbox("Nível", ["Médio", "Superior"])
        with col2:
            edital_file = st.file_uploader("Anexar Edital (TXT/PDF)", type=['txt', 'pdf'])
        
        if st.button("🚀 Iniciar Tribunal de IAs"):
            if not cargo:
                st.error("Informe o cargo.")
                return
            
            edital_texto = str(edital_file.read(), "utf-8") if edital_file else ""
            questoes_finais = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i in range(5): # Exemplo com 5 questões para teste rápido
                status_text.text(f"Gerando e validando questão {i+1}/5...")
                
                # Passo 1: Geração
                q_base = gerar_questao_base(banca, cargo, nivel, edital_texto)
                
                if q_base:
                    # Passo 2: Tribunal
                    q_validada = tribunal_de_ias(q_base, banca, edital_texto)
                    if q_validada:
                        q_validada['id'] = i + 1
                        questoes_finais.append(q_validada)
                
                progress_bar.progress((i + 1) / 5)
            
            if questoes_finais:
                st.session_state['simulado'] = questoes_finais
                st.session_state['respostas'] = {}
                st.success(f"{len(questoes_finais)} questões validadas pelo consenso das 3 IAs!")
                st.switch_tab("✅ Realizar Prova")
            else:
                st.error("Nenhuma questão atingiu consenso total. Tente novamente.")

    with tab2:
        if 'simulado' not in st.session_state:
            st.info("Gere o simulado primeiro.")
        else:
            form = st.form("prova_form")
            for q in st.session_state['simulado']:
                form.subheader(f"Q{q['id']} - {q['status']}")
                form.write(q['enunciado'])
                form.radio("Resposta:", q['alternativas'], key=f"resp_{q['id']}")
            
            if form.form_submit_button("Finalizar"):
                erros = []
                for q in st.session_state['simulado']:
                    resp_user = st.session_state[f"resp_{q['id']}"]
                    if resp_user.split(')')[0] != q['gabarito_sugerido']:
                        erros.append(q)
                
                st.session_state['erros'] = erros
                st.metric("Resultado", f"Erros: {len(erros)}")
                if erros:
                    st.switch_tab("🃏 Flashcards")

    with tab3:
        st.header("Flashcards de Erros")
        if 'erros' in st.session_state:
            for e in st.session_state['erros']:
                with st.expander(f"Questão {e['id']} - Ver Resolução"):
                    st.write(e['enunciado'])
                    st.success(f"Gabarito: {e['gabarito_sugerido']}")
                    st.info(e['resolucao_final'])

if __name__ == "__main__":
    main()
