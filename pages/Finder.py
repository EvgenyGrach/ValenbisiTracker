import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import streamlit as st
import folium
from folium import plugins
from streamlit_folium import folium_static
from shapely.geometry import LineString
from streamlit_js_eval import get_geolocation
import requests
import json
import osmnx as ox
from folium.plugins import HeatMap, MeasureControl
import networkx as nx
import geocoder
from polyline import decode
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import polyline
from streamlit_js_eval import streamlit_js_eval, copy_to_clipboard, create_share_link, get_geolocation




st.set_page_config(page_title="Valenbisi Tracker", page_icon="📈")
place_name = "Valencia, Spain"

c1, c2 = st.columns(2)
@st.cache_resource
def get_graph():
    graph = ox.graph_from_place(place_name, network_type="drive", simplify=True)
    street_geometries = ox.graph_to_gdfs(graph, nodes=False, edges=True)['geometry']
    return graph, street_geometries


request = requests.get('https://valencia.opendatasoft.com/api/records/1.0/search/?dataset=estat-transit-temps-real-estado-trafico-tiempo-real&q=&rows=376')


def df_respuesta(response):
    p = []
    if response.status_code == 200:
        data = response.json()
        st.write(data)
        records = data['records']
        for record in records:
            fields = record['fields']
            state = fields['estado']
            gid = fields['gid']
            denom = fields['denominacion']
            geo = fields['geo_shape']
            coord = geo['coordinates']
            
           
            
            p.append((gid, denom, state, coord))

        df = pd.DataFrame(p, columns = ('gid', 'denom', 'state', 'coord'))
        

    

        return df
    


    
trafico = df_respuesta(request)
trafico = trafico[~trafico['state'].isin([4, 9])]

recodificacion = {5: 0, 6: 1, 7: 2, 8: 3}
trafico['state'] = trafico['state'].replace(recodificacion)

st.write(trafico)

def show_secondary_page():
    trafico['geometry'] = trafico['coord'].apply(lambda x: LineString(x))
    gdf = gpd.GeoDataFrame(trafico, geometry='coord')

# Convertir las geometrías a objetos shapely
    gdf['geometry'] = gpd.GeoSeries.from_wkt(gdf['geometry'])

# Crear un mapa centrado en un punto medio de los tramos
    map_center = gdf.geometry.unary_union.centroid
    map2 = folium.Map(location=[map_center.y, map_center.x], zoom_start=12)

# Definir una función para asignar colores según el valor de 'state'
    def get_color(state):
        if state == 0:
            return 'green'
        elif state == 1:
            return 'yellow'
        elif state == 2:
            return 'orange'
        elif state == 3:
            return 'red'

# Añadir los tramos al mapa
    for _, row in gdf.iterrows():
        folium.GeoJson(
            row['geometry'],
            style_function=lambda x, state=row['state']: {'color': get_color(state)}
        ).add_to(map2)

# Añadir una leyenda al mapa
    legend_html = '''
       <div style="position: fixed; 
                 bottom: 50px; left: 50px; width: 200px; height: 150px; 
                 border:2px solid grey; z-index:9999; font-size:14px;
                 background-color:white;
                  ">
     &nbsp; <b>Legend</b> <br>
     &nbsp; 0: <i class="fa fa-circle" style="color:green"></i> Low <br>
     &nbsp; 1: <i class="fa fa-circle" style="color:yellow"></i> Medium <br>
     &nbsp; 2: <i class="fa fa-circle" style="color:orange"></i> High <br>
     &nbsp; 3: <i class="fa fa-circle" style="color:red"></i> Very High <br>
     </div>
     '''
    map2.get_root().html.add_child(folium.Element(legend_html))

# Mostrar el mapa en la aplicación Streamlit
    st.title("Heatmap de Tramos de Tráfico en Tiempo Real")
    folium_static(map2, width=700, height=500)
        
        

show_secondary_page()


