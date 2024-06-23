import streamlit as st


st.set_page_config(
    page_title="FGV/Valenbisi Tracker",
    page_icon="👋"
)
st.title("FGV/Valenbisi Fast Tracker")
f = f"""
    <span style="font-weight:bold;">Real Time information on Metro Valencia and Valenbici Stations</span>
    """

st.write(f, unsafe_allow_html=True)
st.write("__________________________________________________________________________________")

f = f"""
    <span style="font-weight:bold;">Check info on Metro Valencia at</span><br>
    <span> FGV Tracker</span>
    """

c = f"""
    <span style="font-weight:bold;">Check info on Valenbici at</span><br>
    <span> Valenbisi Tracker</span>
    """
col1, col2 = st.columns(2)
with col1:
    st.write(f, unsafe_allow_html=True)

with col2:
    st.write(c, unsafe_allow_html=True)

g = f"""
    <span style="font-weight:bold;">Check real-time inormation on traffic density</span><br>
    <span> Just select Traffic</span>
    """
st.write(g, unsafe_allow_html=True)
st.write("____________________________________________________________________________________")


c1, c2 = st.columns(2)
evgeny = f"""
        <span style="font-weight:bold;"> Project by Evgeny Grachev</span><br>
        <span> Special mention to the Valencia Open Data Project</span>
        """
with c1:
    st.write(evgeny, unsafe_allow_html=True)


