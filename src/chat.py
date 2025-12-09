from uuid import uuid4

import streamlit as st

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings

from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import HumanMessage, SystemMessage

from utils import _get_pdf_text, _csv_to_text

PDF_FORMAT = 'PDF'
CSV_FORMAT = 'CSV'
DOCUMENT_FORMATS = [PDF_FORMAT, CSV_FORMAT]

def _get_text_chunks(raw_text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    chunks = splitter.split_text(raw_text)
    print(f"INFO: Texto dividido en {len(chunks)} chunks")
    return chunks


def _get_vectorstore(text_chunks: list[str]) -> FAISS:
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings, docstore=InMemoryDocstore())
    return vectorstore


def _make_vector_search_tool(vectorstore):
    @tool("search_docs", return_direct=False)
    def search_docs(query: str) -> str:
        """Busca información relevante en el documento cargado."""
        docs = vectorstore.similarity_search(query, k=5)
        return "\n\n".join(d.page_content for d in docs)
    return search_docs


def _create_in_memory_checkpointer():
    return InMemorySaver()


def _create_agent_with_memory(tools):
    checkpointer = _create_in_memory_checkpointer()
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
    agent = create_agent(
        model=model,
        tools=tools,
        checkpointer=checkpointer
    )
    return agent

def load_document_to_llm(document, doc_format: str):
    if doc_format == PDF_FORMAT:
        raw_text = _get_pdf_text(document)
    elif doc_format == CSV_FORMAT:
        raw_text = _csv_to_text(document)
    else:
        raise ValueError(f"Formato de documento no soportado: {doc_format}")

    chunks = _get_text_chunks(raw_text)
    vectorstore = _get_vectorstore(chunks)
    search_tool = _make_vector_search_tool(vectorstore)

    agent = _create_agent_with_memory(tools=[search_tool])

    st.session_state.agent = agent
    st.session_state.thread_id = str(uuid4())
    st.session_state.messages = []

def chat_view(init_prompt: str):

    st.title("💬 Chat")
    st.caption("🚀 Developed by JDTorrano")

    agent = st.session_state.agent
    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    if not st.session_state.messages:
        init_sys_message = SystemMessage(content=init_prompt)
        input_dict = {"messages": [init_sys_message]}
        response = agent.invoke(input_dict, config)
        history = response.get("messages") or []

        last_content = ""
        if history:
            last = history[-1]
            last_content = getattr(last, "content", str(last))
        else:
            last_content = str(response)
        st.session_state.messages.append({"role": "assistant", "content": last_content})

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])


    if prompt := st.chat_input("Escribe tu pregunta aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        user_msg = HumanMessage(content=prompt)
        input_dict = {"messages": [user_msg]}
        response = agent.invoke(input_dict, config)

        history = response.get("messages") or []
        answer = ""
        if history:
            last = history[-1]
            answer = getattr(last, "content", str(last))
        else:
            answer = str(response)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.chat_message("assistant").write(answer)
