import streamlit as st

pages = (
    st.Page("pages/app.py", title="Home", icon=":material/home:"),
    st.Page("pages/run_app.py", title="Execução", icon=":material/chat:"),
    st.Page("pages/tools_log.py", title="Log de Tools", icon=":material/build_circle:")
)
    
pg = st.navigation(pages)
pg.run()
