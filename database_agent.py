from langchain.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from dotenv import load_dotenv
import agents

load_dotenv()

agent_verifier, agent_recommender = agents.criar_agentes()

# Estado do grafo do LangGraph
class StatesFlow(TypedDict):
    prompt_user: str
    verifier_result: agents.RespostaVerificador | None
    recommender_result: agents.Recomendacao | None

# Nós do grafo
def no_verificador(state: StatesFlow):
    response = agent_verifier.invoke({"messages": HumanMessage(content=state["prompt_user"])}, config={"recursion_limit": 15})

    if isinstance(response, dict) and isinstance(response["structured_response"], agents.RespostaVerificador):
        result = response.get("structured_response")

    print(f'\nRESULTADO VERIFICADOR:{result}')
    print(f'\nTIPO: {type(result)}\n\n')

    return {"verifier_result": result}

def no_recomendacao(state: StatesFlow):
    response = agent_recommender.invoke({"messages": HumanMessage(content=state["prompt_user"])}, config={"recursion_limit": 25})

    for event in response["messages"]:
        event.pretty_print()

    if isinstance(response, dict) and isinstance(response["structured_response"], agents.Recomendacao):
        result = response.get("structured_response")

    print(f'\n\n\nRESULTADO RECOMENDADOR:{result}')
    print(f'\nTIPO: {type(result)}\n\n\n\n')
    
    return {"recommender_result": result}

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