from langchain.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from typing import Any, TypedDict
from dotenv import load_dotenv
import agents

load_dotenv()

agent_verifier, agent_recommender = agents.criar_agentes()

# Estado do grafo do LangGraph
class StatesFlow(TypedDict):
    prompt_user: str
    verifier_result: agents.RespostaVerificador | None
    recommender_result: agents.Recomendacao | None
    tool_logs: list[dict[str, Any]]


def extrair_logs_tools(messages: list[Any]) -> list[dict[str, Any]]:
    """Relaciona cada chamada de tool à resposta gerada por ela."""
    logs: list[dict[str, Any]] = []
    logs_por_id: dict[str, dict[str, Any]] = {}

    for message in messages:
        for tool_call in getattr(message, "tool_calls", None) or []:
            call_id = tool_call.get("id", "")
            log = {
                "id": call_id,
                "funcao": tool_call.get("name", "Tool sem nome"),
                "argumentos": tool_call.get("args", {}),
                "resultado": None,
            }
            logs.append(log)
            if call_id:
                logs_por_id[call_id] = log

        tool_call_id = getattr(message, "tool_call_id", None)
        if not tool_call_id:
            continue

        log = logs_por_id.get(tool_call_id)
        if log is None:
            log = {
                "id": tool_call_id,
                "funcao": getattr(message, "name", None) or "Tool sem nome",
                "argumentos": {},
                "resultado": None,
            }
            logs.append(log)
            logs_por_id[tool_call_id] = log

        log["resultado"] = getattr(message, "content", "")

    return logs

# Nós do grafo
def no_verificador(state: StatesFlow):
    response = agent_verifier.invoke({"messages": HumanMessage(content=state["prompt_user"])}, config={"recursion_limit": 15})

    result = response.get("structured_response") if isinstance(response, dict) else None

    print(f'\nRESULTADO VERIFICADOR:{result}')
    print(f'\nTIPO: {type(result)}\n\n')

    return {"verifier_result": result}

def no_recomendacao(state: StatesFlow):
    response = agent_recommender.invoke({"messages": HumanMessage(content=state["prompt_user"])}, config={"recursion_limit": 25})

    messages = response.get("messages", []) if isinstance(response, dict) else []
    for event in messages:
        event.pretty_print()

    result = response.get("structured_response") if isinstance(response, dict) else None
    tool_logs = extrair_logs_tools(messages)

    print(f'\n\n\nRESULTADO RECOMENDADOR:{result}')
    print(f'\nTIPO: {type(result)}\n\n\n\n')
    
    return {"recommender_result": result, "tool_logs": tool_logs}

# Função de aresta condicional
def checa_seguranca(state: StatesFlow):
    verificacao = state["verifier_result"]

    if verificacao and verificacao.alarme == 0:
        return "recomendar"
    else:
        return "abortar"

def create_graph():
    # Criar grafo
    global StatesFlow
    graph = StateGraph(StatesFlow)

    # Definir nós
    graph.add_node("verificador", no_verificador)
    graph.add_node("recomendador", no_recomendacao)

    # Definir arestas
    graph.add_edge(START, "verificador")
    graph.add_conditional_edges("verificador", checa_seguranca, {"recomendar": "recomendador", "abortar": END})
    graph.add_edge("recomendador", END)

    app = graph.compile()
    return app

def search_recommendations(app, prompt):
    return app.invoke({"prompt_user": prompt})
