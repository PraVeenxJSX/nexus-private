from typing import TypedDict


class AgentState(TypedDict):
    question: str
    user_id: int
    answer: str
    sources: list


def build_graph():
    from langgraph.graph import StateGraph, END
    from app.services.rag import answer_question

    def retrieve_and_answer(state: AgentState):
        answer, sources = answer_question(state["question"], state["user_id"])
        return {"answer": answer, "sources": sources}

    graph = StateGraph(AgentState)
    graph.add_node("knowledge_researcher", retrieve_and_answer)
    graph.set_entry_point("knowledge_researcher")
    graph.add_edge("knowledge_researcher", END)
    return graph.compile()


def run_agent(question: str, user_id: int):
    # Call retrieval directly so chat does not also load LangGraph on small hosts.
    from app.services.rag import answer_question

    answer, sources = answer_question(question, user_id)
    return {"answer": answer, "sources": sources, "question": question, "user_id": user_id}
