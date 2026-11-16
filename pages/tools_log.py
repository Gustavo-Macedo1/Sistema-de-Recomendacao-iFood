import sqlite3
from pathlib import Path
from typing import Any

import streamlit as st


DB_PATH = Path(__file__).resolve().parents[1] / "ifood_dataset.db"


@st.cache_data(show_spinner=False)
def carregar_banco(db_path: str, ultima_modificacao: float) -> dict[str, Any]:
    """Carrega schema, contagem e amostra das tabelas sem permitir escrita."""
    del ultima_modificacao  # usado apenas para invalidar o cache quando o arquivo mudar
    tabelas: dict[str, Any] = {}
    uri = f"file:{Path(db_path).as_posix()}?mode=ro"

    with sqlite3.connect(uri, uri=True) as connection:
        nomes = connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()

        for (nome,) in nomes:
            nome_seguro = nome.replace('"', '""')
            colunas_raw = connection.execute(
                f'PRAGMA table_info("{nome_seguro}")'
            ).fetchall()
            colunas = [
                {
                    "coluna": coluna[1],
                    "tipo": coluna[2],
                    "obrigatória": bool(coluna[3]),
                    "chave primária": bool(coluna[5]),
                }
                for coluna in colunas_raw
            ]

            total = connection.execute(
                f'SELECT COUNT(*) FROM "{nome_seguro}"'
            ).fetchone()[0]
            cursor = connection.execute(
                f'SELECT * FROM "{nome_seguro}" LIMIT 10'
            )
            cabecalho = [item[0] for item in cursor.description]
            amostra = [dict(zip(cabecalho, linha)) for linha in cursor.fetchall()]
            tabelas[nome] = {"total": total, "colunas": colunas, "amostra": amostra}

    return tabelas


st.title(":material/manage_search: Observabilidade das Tools")
st.caption("Inspecione a base local e as chamadas realizadas na execução mais recente do agente.")

tab_banco, tab_chamadas = st.tabs(["Banco de dados", "Chamadas das funções"])

with tab_banco:
    if not DB_PATH.exists():
        st.error(f"Banco de dados não encontrado em `{DB_PATH}`.")
    else:
        tabelas = carregar_banco(str(DB_PATH), DB_PATH.stat().st_mtime)
        st.write(f"**Arquivo:** `{DB_PATH.name}` · **Modo de inspeção:** somente leitura")

        metricas = st.columns(len(tabelas)) if tabelas else []
        for coluna, (nome, dados) in zip(metricas, tabelas.items()):
            coluna.metric(nome, f"{dados['total']} registros")

        for nome, dados in tabelas.items():
            with st.expander(f"Tabela `{nome}` — schema e amostra"):
                st.markdown("**Schema**")
                st.dataframe(dados["colunas"], width="stretch", hide_index=True)
                st.markdown("**Primeiros 10 registros**")
                if dados["amostra"]:
                    st.dataframe(dados["amostra"], width="stretch", hide_index=True)
                else:
                    st.info("A tabela está vazia.")

with tab_chamadas:
    execucao = st.session_state.get("agent_execution_log")

    if not execucao:
        st.info("Nenhuma execução registrada nesta sessão.")
        st.caption("Acesse a página Execução para rodar o agente e gerar os logs.")
    else:
        topo_1, topo_2 = st.columns([3, 1])
        topo_1.markdown(f"**Prompt:** {execucao.get('prompt', '')}")
        topo_2.caption(f"Executado em {execucao.get('executado_em', '—')}")

        verificacao = execucao.get("verificacao") or {}
        if verificacao.get("alarme") == 0:
            st.success("Prompt aprovado pelo agente verificador.")
        elif verificacao:
            st.error(f"Prompt bloqueado: {verificacao.get('justificativa', '')}")

        tool_logs = execucao.get("tool_logs", [])
        if not tool_logs:
            st.warning("Esta execução não realizou chamadas de tools.")
        else:
            st.metric("Total de chamadas", len(tool_logs))
            for indice, log in enumerate(tool_logs, start=1):
                funcao = log.get("funcao", "Tool sem nome")
                with st.expander(f"{indice}. {funcao}", expanded=indice == 1):
                    st.markdown("**Argumentos enviados**")
                    argumentos = log.get("argumentos", {})
                    if argumentos:
                        st.json(argumentos)
                    else:
                        st.caption("A função não recebeu argumentos.")

                    st.markdown("**Resultado retornado**")
                    resultado = log.get("resultado")
                    if isinstance(resultado, str):
                        st.code(resultado or "(resultado vazio)", language="text")
                    else:
                        st.json(resultado)

        if st.button("Limpar histórico desta sessão", icon=":material/delete_sweep:"):
            del st.session_state["agent_execution_log"]
            st.rerun()
