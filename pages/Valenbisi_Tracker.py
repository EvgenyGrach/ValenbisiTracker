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
from streamlit_js_eval import streamlit_js_eval, copy_to_clipboard, create_share_link, get_geolocation
import branca.colormap as cm


place_name = "Valencia, Spain"


@st.cache_resource
def get_graph():
    graph = ox.graph_from_place(place_name, network_type="drive", simplify=True)
    street_geometries = ox.graph_to_gdfs(graph, nodes=False, edges=True)['geometry']
    return graph, street_geometries


request = requests.get('https://valencia.opendatasoft.com/api/records/1.0/search/?dataset=valenbisi-disponibilitat-valenbisi-dsiponibilidad&q=&rows=276')


def df_respuesta(response):
    p = []
    if response.status_code == 200:
        data = response.json()
        records = data['records']
        for record in records:
            record_id = record['recordid']
            fields = record['fields']
            geometry = record['geometry']
            ticket = fields['ticket']
            geo_point_2d = fields['geo_point_2d']
            open = fields['open']
            total = fields['total']
            number = fields['number']
            free = fields['free']
            available = fields['available']
            address = fields['address']
            geo_shape = fields['geo_shape']
            p.append((record_id, geometry, ticket, geo_point_2d, open, total, number, free, available, address, geo_shape))

        df = pd.DataFrame(p, columns = ('rocrd_id', 'geometry', 'ticket', 'geo_point_2d', 'open', 'total', 'number', 'free', 'available' , 'address', 'geo_shape'))
        df[['Latitude', 'Longitude']] = df['geo_point_2d'].apply(pd.Series)

    

        return df
    

def get_icon_color(value):
    if value < 5:
        return 'red'
    elif value > 15:
        return 'blue'
    else:
        return 'green'

    
bicis = df_respuesta(request)
oeste = bicis[['Latitude', 'Longitude']].min().values.tolist()
este = bicis[['Latitude', 'Longitude']].max().values.tolist()

    
def reverse_geocode(latitude, longitude):
    g = geocoder.osm([latitude, longitude], method='reverse')
    if g.ok:
        return g.address
    else:
        return None

@st.cache_data
def get_route_geometry(st_lat, st_lng, dest_lat, dest_lng):
    url = f"http://router.project-osrm.org/route/v1/driving/{st_lng},{st_lat};{dest_lng},{dest_lat}?overview=full&geometries=geojson"
    response = requests.get(url)
    data = response.json()
    if data["code"] == "Ok":
        geometry = list(data["routes"][0]["geometry"]['coordinates'])
        return geometry
    else:
        return []

def search_location(name):
    best_match = process.extractOne(name, bicis['address'], scorer=fuzz.ratio)
    if best_match is not None:
        closest_name = best_match[0]
        closest_row = bicis[bicis['address'] == closest_name].iloc[0]
        name, lat, long = closest_row['address'], closest_row['Latitude'], closest_row['Longitude']
        return name, lat, long
    else: 
        return None




def mapita():
    st.title("Valenbisi Fast tracker")
    st.write("Con esta herramienta puede visualizar un HeatMap que representa la disponibilidad de Valenbicis en distintas zonas")
    bicis_full = bicis.loc[(bicis['available'] >= 15), ('address', 'open', 'ticket', 'total', 'available', 'Latitude', 'Longitude')]
    bicis_full = bicis_full.sort_values('available', ascending = False).reset_index(drop = True)
    permit = st.checkbox("Buscar una estación")
    st.write("Si marca la casilla podra buscar estaciones de manera individual y consultar informacion mas detallada")
    map3 = folium.Map(location=[39.4699, -0.3763], zoom_start=12)
    if permit:
        selected_location = st.selectbox('Select a station', bicis_full['address'])
        show_map = True
        if show_map and selected_location:
            x, y = get_graph()
            localizacion = bicis.loc[bicis['address'] == selected_location, ('address', 'open', 'total', 'available', 'Latitude', 'Longitude')].reset_index(drop = True)
            localizacion1 = bicis.loc[bicis['address'] == selected_location, ('address', 'open', 'total', 'available')].reset_index(drop = True)
            selected_lat = localizacion.loc[localizacion['address'] == selected_location, ('Latitude', 'Longitude')]
            latdf = selected_lat.loc[0, 'Latitude']
            longdf = selected_lat.loc[0, 'Longitude']
            selected_long = localizacion.loc[localizacion['address'] == selected_location, 'Longitude']
            st.subheader("Estacion")
            st.dataframe(localizacion1)
            icon_color = get_icon_color(localizacion['available'].item())
            selected_lat = list(selected_lat)
            selected_lat = selected_lat
            selected_long = list(selected_long)
            selected_long = selected_long

            folium.Marker(
                location=[latdf, longdf],
                popup=selected_location,
                icon=folium.Icon(color=icon_color)
                ).add_to(map3)
            
            


        folium_static(map3)
    
    
    if not permit:
        x, y = get_graph()
        map2 = folium.Map(location=[39.4699, -0.3763], zoom_start=13)
        plugins.LocateControl(strings={"title": "See your current location", "popup": "Your position"}).add_to(map2)

        #folium.GeoJson(y).add_to(map2)

        heat_data = [[row['Latitude'], row['Longitude'], row['available']] for index, row in bicis.iterrows()]
        HeatMap(heat_data, min_opacity=0.2, max_val=max(bicis['available']), gradient={0: 'red', 0.33: 'orange', 0.66: 'yellow', 1: 'green'}).add_to(map2)
        st.subheader("Disponibilidad Valenbici mediante HeatMap")
        colormap = cm.LinearColormap(colors=['red', 'orange', 'yellow', 'green'], 
                             vmin=min(bicis['available']), 
                             vmax=max(bicis['available']),
                             caption='Disponibilidad de bicicletas')
        colormap.add_to(map2)
        folium_static(map2, width=700, height=500)


        #for _, row in bicis.iterrows():
         #  tooltip_txt = f"""
          #  <span style="font-weight:bold;">Dirección:</span> {row['address']}<br>
           # <span style="font-weight:bold;">Total:</span> {row['total']}<br>
            #<span style="font-weight:bold;">Disponibles:</span> {row['available']}
           # """
            #icon_color = get_icon_color(row['available'])
            #if row['available'] > 0:
             #  folium.Marker(
             #      location=[row['geo_point_2d'][0], row['geo_point_2d'][1]],
             #      tooltip=tooltip_txt,
             #      fill_color = "red",
              #     icon=folium.Icon(color=icon_color, icon_color='#FFFF00')
             #  ).add_to(map2)
          #  else: pass
       # folium_static(map2)


mapita()





