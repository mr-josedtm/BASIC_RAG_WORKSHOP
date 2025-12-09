import streamlit as st
from streamlit import session_state
from streamlit_lottie import st_lottie
import requests
import time
from typing import Callable

from prompt_templates import get_sys_prompt
from chat import load_document_to_llm, DOCUMENT_FORMATS

SECTIONS = ['Inicio', 'Idioma', 'Tipo de documento', 'Cargar documento' ]
LANGUAGES = ['Español', 'Balear', 'Catalán', 'Euskera', 'Gallego']
DOCUMENT_TYPES = ['Apuntes', 'Información']


def _go_to_init():
    st.session_state['current_step'] = 1

def _set_form_step(action,step=None):
    if action == 'Next':
        st.session_state['current_step'] = st.session_state['current_step'] + 1
    if action == 'Back':
        st.session_state['current_step'] = st.session_state['current_step'] - 1
    if action == 'Jump':
        st.session_state['current_step'] = step

def _render_animation():
    animation_response = requests.get('https://assets1.lottiefiles.com/packages/lf20_vykpwt8b.json')
    animation_json = dict()
    if animation_response.status_code == 200:
        animation_json = animation_response.json()
    else:
        print("Error in the URL")
    return st_lottie(animation_json,height=200,width=300)

def _wizard_form_header():
    # Renderiza el menú de migas de pan
    breadcrumbs = []
    for i in range(0, st.session_state['current_step']):
        if i < len(SECTIONS):
            if i+1 == st.session_state['current_step']:
                breadcrumbs.append(f"<b>{SECTIONS[i]}</b>")
            else:
                breadcrumbs.append(SECTIONS[i]) 
    separator = " → "
    st.markdown(separator.join(breadcrumbs), unsafe_allow_html=True)

def _wizard_form_body(next_page: str, go_to_page: Callable):
    ###### Step 1: Introduction ######
    if st.session_state['current_step'] == 1:
        st.write("""
                #### Hola! Soy UMUchi
            """)       
        st.write("""
                ###### Vas a tener que darme algo de información para que pueda ayudarte mejor 👾
            """)
        st.image('https://aulas.um.es/themes/assets/img/LogosimboloUMU-positivo.png')
    ###### Step 2: Language ######
    if st.session_state['current_step'] == 2:
        st.session_state['in_language'] = st.selectbox(label="Selecciona el idioma en que hablaremos",options=LANGUAGES,index=0)
    ###### Step 3: Document type ######
    if st.session_state['current_step'] == 3:
        st.session_state['in_doc_type'] = st.radio(label='¿Sobre qué tipo de documento quiere hablar?',options=DOCUMENT_TYPES,index=1,horizontal=True)
        st.session_state['in_doc_format'] = st.radio(label='¿En qué formato está el documento?',options=DOCUMENT_FORMATS,index=0,horizontal=True)
    ###### Step 4: Source Files ######
    if st.session_state['current_step'] == 4:            
        source_file_container = st.empty()
        with source_file_container.container():
            st.session_state['in_document'] = st.file_uploader('Busca el documento', accept_multiple_files=False)

    st.markdown('---')
    
    form_footer_container = st.empty()
    with form_footer_container.container():
        
        disable_back_button = True if st.session_state['current_step'] == 1 else False
        disable_next_button = True if st.session_state['current_step'] == 4 else False
        
        form_footer_cols = st.columns([5,1,1.5,1.75])
        
        form_footer_cols[0].button('Cancelar',on_click=_go_to_init)
        form_footer_cols[1].button('Atrás',on_click=_set_form_step,args=['Back'],disabled=disable_back_button)
        form_footer_cols[2].button('Siguiente',on_click=_set_form_step,args=['Next'],disabled=disable_next_button)
    
        
        file_ready = False if st.session_state['in_document'] is not None else True
        load_file = form_footer_cols[3].button('Cargar',disabled=file_ready)
         
    if load_file:
        source_file_container.empty()
        form_footer_container.empty()
        response_container = st.empty()
        success = True
        try:

            load_document_to_llm(document=session_state['in_document'],doc_format=st.session_state['in_doc_format'])

            with response_container.container():
                progress_bar_cols = st.columns([2,5,2])
                with progress_bar_cols[1]:
                    my_bar = st.progress(0, text='')
                    _render_animation()

                    text_change_count = 0
                    text_index = 0
                    messages = [
                        '**Felicitando a OpenAI por su trabajo...**',
                        '**Enviando CV a NTTData...**',
                        '**Hackeando servidores de la UMU...**',
                        '**Subrayando el documento...**',
                        '**Completando la vectorización...**',
                        '**Subiendo la potencia del ventilador...**',
                    ]
                    for percent_complete in range(100):
                        time.sleep(0.05)
                        text_change_count +=1

                        if text_change_count % 20 == 0:
                            text_index += 1
                        my_bar.progress(percent_complete + 1, text=messages[text_index])

        except Exception as exc:
            print(exc)
            success = False
            raise exc
        
        with response_container.container():
            file_name = st.session_state['in_document'].name
            if success:
                st.success(f'✅  {file_name} cargado!')
                language = st.session_state['in_language']
                doc_type = st.session_state['in_doc_type']
                st.session_state['init_prompt'] = get_sys_prompt(doc_type, language)
            else:
                st.error(f'❌ Error al cargar {file_name}')
                            
            ok_cols = st.columns(8)    
            ok_cols[0].button('Chat!',type='primary',on_click=go_to_page,args=[next_page],use_container_width=True)        


def render_wizard_view(next_page: str, go_to_page: Callable):
    _wizard_form_header()
    _wizard_form_body(next_page, go_to_page)
