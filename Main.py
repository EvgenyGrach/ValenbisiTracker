
from pages.Valenbisi_Tracker import mapita
import streamlit as st
from pages.Finder import show_secondary_page
from pages.FGV_Tracker import show_third_page

st.set_page_config(
    page_title="FGV/Valenbisi Tracker",
    page_icon="👋"
)
st.title("FGV/Valenbisi Fast Tracker")
f = f"""
    <span style="font-weight:bold;">Real Time information on FGV and Valenbisi Stations</span>
    """

st.write(f, unsafe_allow_html=True)
st.write("__________________________________________________________________________________")

f = f"""
    <span style="font-weight:bold;">Check info on FGV Stations at</span><br>
    <span> FGV Tracker</span>
    """

c = f"""
    <span style="font-weight:bold;">Check info on Valenbisi at</span><br>
    <span> Valenbisi Tracker</span>
    """
col1, col2 = st.columns(2)
with col1:
    st.write(f, unsafe_allow_html=True)

with col2:
    st.write(c, unsafe_allow_html=True)

g = f"""
    <span style="font-weight:bold;">You can also search for a station!</span><br>
    <span> Just selected Finder</span>
    """
st.write(g, unsafe_allow_html=True)

