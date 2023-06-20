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

st.set_page_config( page_title='Visão Empresa', page_icon='📈', layout = 'wide' )

# ======================================
# Funções
# ======================================
def country_maps( df ): 
    
    columns = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    
    columns_grouped = ['City', 'Road_traffic_density']
    
    data_plot = df.loc[:, columns].groupby(columns_grouped).median().reset_index()
    
    map = folium.Map( zoom_start = 11 )
    
    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'], 
                       location_info['Delivery_location_longitude']],
                       popup = location_info[['City', 'Road_traffic_density']] ).add_to( map )
        
    folium_static( map, width = 1024, height = 600)

def order_share_by_week( df ):
    
    df_aux1 = df.loc[:, ['ID', 'Week_of_year']].groupby(['Week_of_year']).count().reset_index()
    df_aux2 = df.loc[:, ['Week_of_year', 'Delivery_person_ID']].groupby(['Week_of_year']).nunique().reset_index()
    df_aux = pd.merge( df_aux1, df_aux2, how='inner')
    
    df_aux['Order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    
    fig = px.line(df_aux, x = 'Week_of_year', y = 'Order_by_delivery')

    return fig

def order_by_week( df ):
           
    df['Week_of_year'] = df['Order_Date'].dt.strftime('%U') 
    df_aux = df.loc[:, ['Week_of_year' , 'ID']].groupby(['Week_of_year']).count().reset_index()
    fig = px.line( df_aux, x = 'Week_of_year', y = 'ID' )

    return fig

def traffic_order_city( df ):
    df_aux = df.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
    
    fig = px.scatter( df_aux, x = 'City', y = 'Road_traffic_density', size = 'ID' , color = 'City')

    return fig

def traffic_order_share( df ):
    df_aux = df.loc[:, ['ID', 'Road_traffic_density']].groupby(['Road_traffic_density']).count().reset_index()
    df_aux['Perc_ID'] = (df_aux['ID'] / df_aux['ID'].sum()) * 100
    
    fig = px.pie(df_aux, values = 'Perc_ID', names = 'Road_traffic_density')

    return fig

def order_metric( df ):
    df_aux1 = df.loc[:, ['ID', 'Order_Date']].groupby(['Order_Date']).count().reset_index()
    fig = px.bar( df_aux1, x = 'Order_Date', y = 'ID')

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
st.header( 'Marketplace - Visão Empresa')

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
st.sidebar.markdown('### Powered by Matheus Serafim')

# Filtro de Data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[ linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df['Road_traffic_density'].isin( traffic_options )
df = df.loc[ linhas_selecionadas, :]

#========================================
# Layout no Streamlit
#========================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão tatica', 'Visão Geográfica'])

with tab1: 
    with st.container():
        # Order metric
        fig = order_metric( df )
        st.markdown( '# Orders by Day')
        st.plotly_chart(fig, use_container_width = True)

    with st.container():
        col1, col2 = st.columns( 2 )
        
        with col1:
            fig = traffic_order_share( df )
            st.header( "Traffic Order Share")  
            st.plotly_chart(fig, use_container_width = True)

        with col2:
            fig = traffic_order_city( df )
            st.header( "Traffic Order City")
            st.plotly_chart(fig, use_container_width = True)
            
with tab2:
    with st.container():
         st.header('Order by Week')
         fig = order_by_week( df )
         st.plotly_chart(fig, use_container_width = True)

    with st.container():
        st.header('Order Share by Week')
        fig = order_share_by_week( df )
        st.plotly_chart(fig, use_container_width = True)
        
with tab3:
    st.header('Country Maps')
    country_maps( df )
    
    
    
    

       




