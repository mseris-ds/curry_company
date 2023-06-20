# Libraries
import pandas as pd
import plotly.express as px
import re
import folium
from haversine import haversine
import plotly.graph_objects as go
import streamlit as st
import datetime as dt
from PIL import Image
from streamlit_folium import folium_static
import numpy as np

st.set_page_config( page_title='Visão Restaurantes', page_icon='🍴', layout = 'wide' )

# ======================================
# Funções
# ======================================
def avg_std_time_on_traffic( df ):
            
    df_aux = (df.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
                .groupby(['City', 'Road_traffic_density'])
                .agg({'Time_taken(min)' : ['mean', 'std']}))
    
    df_aux.columns = ['avg_time' , 'std_time']
    
    df_aux = df_aux.reset_index()
    
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values= 'avg_time', color='std_time', color_continuous_scale='RdBu',
                                                                                 color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig

def avg_st_time_graph( df ):
                
    df_aux = df.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)' : ['mean', 'std']})
    
    df_aux.columns = ['avg_time' , 'std_time']
    
    df_aux = df_aux.reset_index()
    
    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict( type='data', array=df_aux['std_time'] ) ) )
    fig.update_layout(barmode='group')
                
    return fig

def avg_std_time_delivery( df, festival, op ):
    """
    Esta função calcula o tempo médio e o desvio padrão do tempo de entrega
    Parâmetros:
        Input:
            - df: Dataframe com os dados necessários para o cálculo
            - op: Tipo de operação que precisa ser calculado
                'avg_time' : Calcula o tempo médio
                'std_time' : Calcula o desvio padrão do tempo
        Output:
            - df: Dataframe com duas colunas e uma linha.
                
    """
                
    df_aux = df.loc[:, ['Time_taken(min)', 'Festival']].groupby(['Festival']).agg({'Time_taken(min)' : ['mean', 'std']})
    
    df_aux.columns = ['avg_time' , 'std_time']
    df_aux = df_aux.reset_index()
    
    linhas_selecionadas = df_aux['Festival'] == festival
    df_aux = np.round( df_aux.loc[linhas_selecionadas, op], 2 )

    return df_aux

def distance( df, fig ):
    if fig == False:
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    
        df['distance'] = (df.loc[:, cols]
                            .apply( lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 ))
    
        avg_distance = np.round( df['distance'].mean(), 2)
        return avg_distance
        
    else:
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    
        df['distance'] = (df.loc[:, cols]
                            .apply( lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude']) ), axis=1 ))
    
        avg_distance = df.loc[:, ['City', 'distance']].groupby( 'City' ).mean().reset_index()

        fig = go.Figure( data=[ go.Pie( labels = avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])

        return fig

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
st.header( 'Marketplace - Visão Restaurantes')

#image_path = 'logo.png'
image = Image.open( 'logo.png' )
st.sidebar.image( image, width=120)

st.sidebar.markdown(' # Cury Company')
st.sidebar.markdown(' ## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual data deseja analisar?',
    value = dt.datetime(2022,4,13),
    min_value = dt.datetime(2022,2,11),
    max_value = dt.datetime(2022,4,6),
    format='DD-MM-YYYY')

st.header( date_slider)
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do transito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown("""---""")

climate_conditions = st.sidebar.multiselect(
   'Quais as condições climáticas?',
   ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
                   'conditions Cloudy', 'conditions Fog', 'conditions Windy'],
   default=['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
                   'conditions Cloudy', 'conditions Fog', 'conditions Windy'],)

st.sidebar.markdown(""" ---""")
st.sidebar.markdown('### Powered by Matheus Serafim')

# Filtro de Data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[ linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df['Road_traffic_density'].isin( traffic_options )
df = df.loc[ linhas_selecionadas, :]

# Filtro clima
linhas_filtradas = df['Weatherconditions'].isin( climate_conditions )
df = df.loc[ linhas_filtradas, :]


#========================================
# Layout no Streamlit
#=========================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title( 'Overall Metrics' )

        col1, col2, col3, col4, col5, col6 = st.columns( 6 )
        with col1:
            delivery_unique = len(df.loc[:, 'Delivery_person_ID'].unique())
            col1.metric( 'Entregadores', delivery_unique )
            
        with col2:
            avg_distance = distance( df, fig = False )
            col2.metric( 'A distancia média', avg_distance )
            
        with col3:    
            df_aux = avg_std_time_delivery( df, 'Yes', 'avg_time')     
            col3.metric( 'Tempo médio', df_aux )
             
        with col4:
            df_aux = avg_std_time_delivery( df, 'Yes', 'std_time') 
            col4.metric( 'STD Entrega', df_aux )
            
        with col5:
            df_aux = avg_std_time_delivery( df, 'No', 'avg_time') 
            col5.metric( 'Tempo médio', df_aux )
            
        with col6:
            df_aux = avg_std_time_delivery( df, 'No', 'std_time') 
            col6.metric( 'STD Entrega', df_aux )
            
    with st.container():   
        st.markdown( """___""")

        col1, col2 = st.columns( 2 )

        with col1:
            st.title( 'Tempo médio de entrega por cidade' )
            fig  = avg_st_time_graph( df )
            st.plotly_chart( fig, use_container_width=True )

        with col2:
             st.title( 'Distribuição da distância' )
             df_aux = df.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)' : ['mean', 'std']})

             df_aux.columns = ['avg_time' , 'std_time']

             df_aux = df_aux.reset_index()

             st.dataframe( df_aux )
   
    with st.container():
        st.markdown( """___""")
        st.title( 'Distribuição do tempo' )
        
        col1, col2 = st.columns( 2 )
        with col1:
            
             fig = distance (df, fig = True )
             st.plotly_chart( fig, use_container_width=True )

        with col2:
               
            fig = avg_std_time_on_traffic( df )    
            st.plotly_chart( fig, use_container_width=True )

        
    
        
        



















