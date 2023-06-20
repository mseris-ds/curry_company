import streamlit as st
from PIL import Image

st.set_page_config( 
    page_title = 'Home',
    page_icon = "🎲"
)    

#image_path = 'logo.png'
image = Image.open( 'logo.png' )
st.sidebar.image( image, width = 120 )

st.sidebar.markdown(' # Cury Company')
st.sidebar.markdown(' ## Fastest Delivery in Town')
st.sidebar.markdown(""" ---""")

st.write( '# Curry Company Growth Dashboard' )

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos entregadores e restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão empresa:
        - Visão gerencial: Métricas gerais de comportamento.
        - Visão tática: Indicadores semanais de crescimento.
        - Visão geográfica: Insights de geolocalização.
    - Visão entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão restaurantes:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for help
        Matheus Serafim
        https://www.linkedin.com/in/mseris/
    """
)
