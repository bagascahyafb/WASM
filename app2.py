import folium 
import pandas as pd
import streamlit as st
from folium.plugins import MarkerCluster 
from streamlit_folium import st_folium

df = pd.read_csv("data")
df.drop(columns=["Unnamed: 0"], inplace=True)
df.dropna(inplace=True)

# Sidebar filters
st.sidebar.header("Filter")
selected_city = st.sidebar.multiselect("Pilih Kota", options=df["Kota"].unique(), default=df["Kota"].unique())
selected_job_type = st.sidebar.multiselect("Pilih Tipe Pekerjaan", options=df["Type"].unique(), default=df["Type"].unique())
selected_work_hours = st.sidebar.multiselect("Pilih Jam Kerja", options=df["Work Hours"].unique(), default=df["Work Hours"].unique())

# Filter data berdasarkan pilihan user
filtered_data = df[
    (df["Kota"].isin(selected_city)) &
    (df["Type"].isin(selected_job_type)) &
    (df["Work Hours"].isin(selected_work_hours))
]

def make_clickable(url):
    return f'<a href="{url}" target="_blank">{url}</a>'

filtered_data['URL'] = filtered_data['URL'].apply(make_clickable)

st.write("### Lowongan Pekerjaan")
selected_columns = ["Kota","Company Name","Job Title","URL","Type","Work Hours"]
st.write(filtered_data[selected_columns].to_html(escape=False), unsafe_allow_html=True)

# Fungsi untuk menampilkan peta folium
def generate_map(filtered_data):
    # Membuat peta dengan posisi awal Indonesia
    m = folium.Map(location=[-0.789275, 113.921327], zoom_start=5)

    # Membuat MarkerCluster
    marker_cluster = MarkerCluster().add_to(m)

    # Menambahkan marker dengan cluster
    for _, record in filtered_data.iterrows():
        # Membuat tabel pekerjaan untuk pop-up
        pekerjaan_table = f"""
            <table style='width:100%; table-layout:fixed;'>
                <tr><th style='white-space:nowrap;'>Pekerjaan</th></tr>
                <tr><td style='white-space:normal; word-wrap:break-word;'>{record['Job Title']}</td></tr>
            </table>
        """
        popup_content = f"<h3>{record['Kota']}</h3>{pekerjaan_table}"
        
        # Menambahkan marker ke cluster
        folium.Marker(
            [record["Latitude"], record["Longitude"]],
            popup=folium.Popup(popup_content, max_width=250),
            tooltip=f"Lowongan di {record['Kota']}",
            icon=folium.Icon(icon="info-sign", color="blue")
        ).add_to(marker_cluster)

    return m

# Generate peta dengan data yang difilter
m = generate_map(filtered_data)

# Menampilkan peta di Streamlit
st.write("### Peta Lowongan Pekerjaan")
st_folium(m, width=700, height=500)