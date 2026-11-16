import streamlit as st
import database_agent
import whisper

app = database_agent.create_graph()

st.title(":material/chat: Sistema Multiagente - Chat")

prompt = st.chat_input("O que você gostaria de pedir hoje?", accept_audio=True)

with st.chat_message("assistant"):
        st.write("Olá! Eu sou um sistema multiagente de recomendação de refeições. Por favor, me diga o que você deseja pedir hoje.")

if prompt:
    if prompt.audio:
        model = whisper.load_model("small")
        prompt.text = model.transcribe(prompt.audio)
        
    with st.chat_message("user"):
        st.write(prompt.text)

    with st.chat_message("assistant"):
        # Container expansível que mostra o "pensamento" em tempo real
        with st.status("Analisando pedido...", expanded=True) as status:
            
            resultado_final = {}
            
            # O app.stream() entrega cada nó assim que ele termina de rodar
            for evento in app.stream({"prompt_user": prompt.text}, stream_mode="updates"):
                # 1. Quando o nó verificador terminar
                if "verificador" in evento:
                    verif = evento["verificador"]["verifier_result"]
                    if verif.alarme == 0:
                        st.write("🛡️ **Segurança:** Prompt aprovado (Alarme: 0)")
                    else:
                        st.error(f"🚨 **Bloqueado:** {verif.justificativa_alarme}")
                        status.update(label="Requisição bloqueada", state="error")
                
                # 2. Quando o nó recomendador terminar
                if "recomendador" in evento:
                    st.write("🔍 **Banco de Dados:** Consulta SQL concluída.")
                    resultado_final = evento["recomendador"]["recommender_result"]
                    status.update(label="Recomendações prontas!", state="complete", expanded=False)

        # 3. Exibição visual dos pratos recomendados fora do st.status
        if resultado_final and resultado_final.recomendacoes:
            for item in resultado_final.recomendacoes:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    col1.subheader(f"{item.nome_item} — {item.nome_estabelecimento}")
                    col1.write(item.justificativa)
                    col2.metric("Preço", f"R$ {item.preco:.2f}")
                    col2.write(f"⭐ {item.avaliacao_est:.1f}")