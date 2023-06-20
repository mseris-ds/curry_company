# Libraries
import pandas as pd
import plotly.express as px
import re
import folium
from haversine import haversine
import plotly.graph_objects as go
import jupyterlab_dash
import streamlit as st
import datetime as dt
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Entregadores', page_icon='🛵', layout = 'wide' )

# ======================================
# Funções
# ======================================
def top_delivers( df, top_asc ):
    df1 = ((df.loc[: , ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City', 'Delivery_person_ID'])
              .mean()
              .sort_values(['City' , 'Time_taken(min)'], ascending = top_asc)
              .reset_index()))
                
    df_aux01 = df1.loc[df1['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df1.loc[df1['City'] == 'Urban', :].head(10)
    df_aux03 = df1.loc[df1['City'] == 'Semi-Urban', :].head(10)
    
    df4 = pd.concat( [df_aux01, df_aux02, df_aux03]).reset_index( drop=True )

    return df4

def clean_code( df ):
    """ Esta funcao tem a responsabilidade de limpar o dataframe 
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tio da coluna de dados
        3. Remoção dos espaços das variaveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( remoção do texto da variarel numerica )

        Input: Dataframe
        Output: Dataframe
    """
    # 1.Removendo espaço da string
    df.loc[:, 'Delivery_person_ID'] = df.loc[:, 'Delivery_person_ID'].str.strip()
    df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
    df.loc[:, 'Type_of_order'] = df.loc[:, 'Type_of_order'].str.strip()
    df.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
    df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()
    df.loc[:, 'Festival'] = df.loc[:, 'Festival'].str.strip()
    
    # 2.Removendo espaços em branco
    linhas_vazias = df['Delivery_person_Age'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = (df['City'] != 'NaN')
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = (df['Road_traffic_density'] != 'NaN')
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = (df['Festival'] != 'NaN')
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = df['multiple_deliveries'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )
    
    # 3.Conversao de texto/categoria/string para numeros inteiros
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int )
    
    # 4.Conversao de texto/categoria/strings para numeros decimais
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )
    
    # 5.Conversao de texto para data
    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )
    
    # 6.Removendo o texto de numeros
    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split('(min)')[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

    return df


# ============================ Inicio da estrutura lógica do codigo =======================
# ==========================    
# Import Dataset
# ==========================    
df_raw = pd.read_csv('dataset/train.csv')
df = df_raw.copy()

# ==========================    
# Limpando os dados
# ==========================    
df = clean_code( df )

#========================================
# Barra lateral
#=========================================
st.header( 'Marketplace - Visão Entregadores')

#image_path = 'logo.png'
image = Image.open( 'logo.png' )
st.sidebar.image( image, width=120)

st.sidebar.markdown(' # Cury Company')
st.sidebar.markdown(' ## Fastest Delivery in Town')
st.sidebar.markdown(""" ---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual data deseja analisar?',
    value = dt.datetime(2022,4,13),
    min_value = dt.datetime(2022,2,11),
    max_value = dt.datetime(2022,4,6),
    format='DD-MM-YYYY')

st.header( date_slider)
st.sidebar.markdown(""" ---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do transito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown(""" ---""")

climate_conditions = st.sidebar.multiselect(
   'Quais as condições climáticas?',
   ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
                   'conditions Cloudy', 'conditions Fog', 'conditions Windy'],
   default=['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
                   'conditions Cloudy', 'conditions Fog', 'conditions Windy'],)

st.sidebar.markdown(""" ---""")
st.sidebar.markdown('### Powered by Matheus Serafim')


#========================================
# Layout no Streamlit
#=========================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title( 'Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap = 'large')
        with col1:
            # A maior idade entre os entregadores
            Delivery_person_Age_max = df.loc[: , 'Delivery_person_Age'].max()
            col1.metric( 'Maior de Idade', Delivery_person_Age_max )

        with col2:
            # A menor idade entre os entregadores
            Delivery_person_Age_min = df.loc[: , 'Delivery_person_Age'].min()
            col2.metric( 'Menor de Idade', Delivery_person_Age_min )

        with col3:
            # A Melhor condição de Veículos
            Vehicle_condition_best= df.loc[: , 'Vehicle_condition'].max()
            col3.metric( 'Melhor condição', Vehicle_condition_best )

        with col4:
            # Pior condição de Veículo
            Vehicle_condition_worst = df.loc[: , 'Vehicle_condition'].min()
            col4.metric( 'Pior condição', Vehicle_condition_worst )

    with st.container():
        st.markdown("""___""")
        st.title( 'Avaliações' )

        col1, col2 = st.columns( 2)
        with col1:
            st.markdown( '##### Avaliação média por entregador' )
            delivery_person_Ratings_avg = (df.loc[:, ['Delivery_person_ID','Delivery_person_Ratings']]
                                             .groupby(['Delivery_person_ID'])
                                             .mean()
                                             .reset_index())
            st.dataframe(delivery_person_Ratings_avg)


        with col2:
            st.markdown( '##### Avaliação média por trânsito' )
            df_avg_std_rating_by_traffic =( (df.loc[:, ['Delivery_person_Ratings','Road_traffic_density']]
                                               .groupby('Road_traffic_density')
                                               .agg( {'Delivery_person_Ratings' : ['mean', 'std']})))

            # Nome das colunas
            df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']


            # Reset do index
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
            st.dataframe(df_avg_std_rating_by_traffic)



            
            st.markdown( '##### Avaliação média por clima' )
            df_avg_std_rating_by_weatherconditions = ((df.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                                         .groupby('Weatherconditions')
                                                         .agg( {'Delivery_person_Ratings' : ['mean', 'std']})))

            # Nome das colunas
            df_avg_std_rating_by_weatherconditions.columns = ['delivery_mean', 'delivery_std']

            # Reset do index
            df_avg_std_rating_by_weatherconditions = df_avg_std_rating_by_weatherconditions.reset_index()
            st.dataframe(df_avg_std_rating_by_weatherconditions)

    with st.container():
        st.markdown("""___""")
        st.title( 'Velocidade de entrega' )

        col1, col2 = st.columns(2)

        with col1: 
            st.markdown( '##### Top Entregadores mais rápidos' )
            df3 = top_delivers( df, top_asc = True )
            st.dataframe(df3)

        with col2:
            st.markdown( '##### Top entregadores mais lentos' )
            df4 = top_delivers( df, top_asc = False )
            st.dataframe(df4)
          