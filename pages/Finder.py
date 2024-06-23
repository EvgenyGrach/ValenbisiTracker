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
st.write(trafico)
trafico = trafico[~trafico['state'].isin([4, 9])]

recodificacion = {5: 0, 6: 1, 7: 2, 8: 3}
trafico['state'] = trafico['state'].replace(recodificacion)



def show_secondary_page():
    
    st.title("Finder")
    y = st.checkbox("Find me")
    # Display the map
    sub = st.text_input('Search for a Valenbisi Station ', key = 'user_search')
    st.subheader("Least occupied stations")
    bicis_full = bicis.loc[(bicis['available'] >= 15), ('address', 'open', 'ticket', 'total', 'available')]
    bicis_full = bicis_full.sort_values('available', ascending = False).reset_index(drop = True)
    st.dataframe(bicis_full)
    if not sub:
        x, y = get_graph()
        map2 = folium.Map()
        map2.fit_bounds([oeste, este])
        plugins.LocateControl(strings={"title": "See your current location", "popup": "Your position"}).add_to(map2)

        folium.GeoJson(y).add_to(map2)

        for _, row in bicis.iterrows():
            tooltip_txt = f"""
            <span style="font-weight:bold;">Dirección:</span> {row['address']}<br>
            <span style="font-weight:bold;">Total:</span> {row['total']}<br>
            <span style="font-weight:bold;">Disponibles:</span> {row['available']}
            """
            icon_color = get_icon_color(row['available'])
            if row['available'] > 0:
               folium.Marker(
                   location=[row['geo_point_2d'][0], row['geo_point_2d'][1]],
                   tooltip=tooltip_txt,
                   fill_color = "red",
                   icon=folium.Icon(color=icon_color, icon_color='#FFFF00')
               ).add_to(map2)
            else: pass
        folium_static(map2)

    
    elif sub and y:

        x, y = get_graph()
        map = folium.Map()
        map.fit_bounds([oeste, este])
        plugins.LocateControl(strings={"title": "See your current location", "popup": "Your position"}).add_to(map)
        loc = get_geolocation()
        latc = loc['coords']['latitude']
        longc = loc['coords']['longitude']
        folium.GeoJson(y).add_to(map)
        z = reverse_geocode(latc, longc)
        st.write(f"You're close to:  {z}")
        if sub:
            nam = search_location(sub)
            nam = list(nam)
            z, g, h = nam
            if g and h != None:
                st.success("Location found!")
                st.write("Estacion: ", nam[0])
                map = folium.Map()
                lati = g
                longi = h
                map.fit_bounds([[latc, longc], [lati, longi]])

                folium.Marker(location=[latc, longc], tooltip = "We found you!", icon = folium.Icon(color = "black", icon_color = '#FFFFFFF')).add_to(map)
                folium.Marker(location=[lati, longi], tooltip = "Your Destination ", icon = folium.Icon(color = "black", icon_color = '#00FFFF')).add_to(map)

                route_geometry = get_route_geometry(latc, longc, lati, longi)
                gh = []
                for i,n in route_geometry:
                    gh.append([n,i])
                linea = folium.PolyLine([gh], color = 'red', weight = 3)
                linea.add_to(map)
            
            else:
                st.write("no hemos encontrado na")
                st.error("Location not found.")
        
        folium_static(map)
        map.fit_bounds([[latc, longc], [lati, longi]])
        
        

show_secondary_page()


