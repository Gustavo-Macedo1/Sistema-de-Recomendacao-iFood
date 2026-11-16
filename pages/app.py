
import streamlit as st

st.set_page_config(page_title="Sistema Multiagente - iFood", page_icon="assets/ifood-logo.png", layout="wide")

col1, col2 = st.columns([0.15, 0.85])

with col1:
    st.image("assets/ifood-logo-brandlogos.net_.png", width=150)
with col2:
    st.title("Recomendação de Refeições - iFood")
    st.subheader("Sistema Multiagente Completo")

st.markdown("""
\n\n
---

:violet-badge[:material/database: SQLite] :orange-badge[:material/robot_2: LangChain] :green-badge[:material/graph_4: LangGraph] :red-badge[:material/crown: Streamlit] :blue-badge[:material/text_fields: Pydantic]

Este projeto implementa um sistema multiagente para recomendar refeições a usuários de soluções de delivery. 
O sistema consiste de:

- Uma base de dados SQLite fictícia baseada na API do iFood;
- Um agente verificador de SQL/Prompt injection, que é apoiado por uma camada de segurança via _regex_;
- Um agente recomendador (realiza consultas SQL com base no prompt do usuário e retorna as opções mais adequadas para o pedido);
- A presente interface construída com Streamlit.

A saída do sistema é estruturada (com Pydantic) e representa uma lista de recomendações de itens com base no pedido do usuário. Essa saída é _plug-and-play_,
estando pronta para implementação em estruturas que esperam saídas estruturadas, como o FastAPI.

---
""")

if st.button(label="INICIAR TESTE", type="primary"):
    st.switch_page("pages/run_app.py")