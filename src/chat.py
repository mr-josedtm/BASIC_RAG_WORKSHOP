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
    pass


def _get_vectorstore(text_chunks: list[str]) -> FAISS:
    pass


def _make_vector_search_tool(vectorstore):
    pass


def _create_in_memory_checkpointer():
    pass


def _create_agent_with_memory(tools):
    pass

def load_document_to_llm(document, doc_format: str):
    pass

def chat_view(init_prompt: str):
    pass
