from typing import TypedDict
from langgraph.graph import StateGraph, END
from app.services.rag import answer_question

class AgentState(TypedDict): question: str; user_id: int; answer: str; sources: list

def build_graph():
    def retrieve_and_answer(state: AgentState):
        answer, sources = answer_question(state["question"], state["user_id"])
        return {"answer": answer, "sources": sources}
    graph = StateGraph(AgentState)
    graph.add_node("knowledge_researcher", retrieve_and_answer)
    graph.set_entry_point("knowledge_researcher")
    graph.add_edge("knowledge_researcher", END)
    return graph.compile()

def run_agent(question: str, user_id: int):
    app = build_graph()
    return app.invoke({"question": question, "user_id": user_id, "answer": "", "sources": []})
