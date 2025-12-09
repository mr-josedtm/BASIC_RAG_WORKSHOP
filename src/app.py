import streamlit as st
from dotenv import load_dotenv

from chat import chat_view

from wizard import render_wizard_view


LANGUAGES = ['Español', 'Balear', 'Catalán', 'Euskera', 'Gallego']
DOCUMENT_TYPES = ['Factura', 'Recibo', 'Nómina', 'Multa']
SECTIONS = ['Bienvenido!', 'Idioma', 'Tipo de documento', 'Leer documento' ]

PAGES = ["wizard", "chat"]

def _clean_state():
    print("CLEANING STATE!!!")
    ## VIEW STATE ##
    st.session_state['current_view'] = PAGES[0]
    ## WIZARD STATE ##
    st.session_state['in_language'] = LANGUAGES[0]
    st.session_state['in_doc_type'] = ""
    st.session_state['in_doc_format'] = ""
    st.session_state['in_document'] = None
    st.session_state['current_step'] = 1
    ## CHAT STATE ##
    st.session_state['thread_id'] = "1"
    st.session_state['messages'] = []
    st.session_state['agent'] = None
    st.session_state["messages"] = None

    st.session_state['init_prompt'] = None

def _go_to_page(page):
    if page == PAGES[0]:
        _clean_state()
    else:
        st.session_state['current_view'] = page


##### view rendering logic ####
if __name__ == '__main__':
    load_dotenv()
    ### APPLICATION STATE ###
    ## VIEW STATE ##
    if 'current_view' not in st.session_state:
        st.session_state['current_view'] = PAGES[0]
    ## WIZARD STATE ##
    if 'in_language' not in st.session_state:
        print("Reload language")
        st.session_state['in_language'] = LANGUAGES[0]
    if 'in_doc_type' not in st.session_state:
        st.session_state['in_doc_type'] = ""
    if 'in_doc_format' not in st.session_state:
        st.session_state['in_doc_format'] = ""
    if 'in_document' not in st.session_state:
        st.session_state['in_document'] = None
    if 'current_step' not in st.session_state:
        st.session_state['current_step'] = 1
    ## CHAT STATE ##
    if 'thread_id' not in st.session_state:
        st.session_state['thread_id'] = "1"
    if 'messages' not in st.session_state:
        st.session_state['messages'] = []
    if 'agent' not in st.session_state:
        st.session_state['agent'] = None
    if "messages" not in st.session_state:
        st.session_state["messages"] = None

    if 'init_prompt' not in st.session_state:
        st.session_state['init_prompt'] = None

    st.set_page_config(page_title="UMUchi", page_icon=":books:")

    if st.session_state['current_view'] == PAGES[0]:
        render_wizard_view(PAGES[1], _go_to_page)
    elif st.session_state['current_view'] == PAGES[1]:

        st.button('Cargar otro documento',type='primary',on_click=_go_to_page,args=[PAGES[0]],use_container_width=True)   
        chat_view(st.session_state['init_prompt'])
    else:
        st.write("""
            # ERROR PAGE
        """)

    # TODO use real routing with pages
