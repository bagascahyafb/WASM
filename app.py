import folium
import pandas as pd
import streamlit as st
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# Membaca dataset
df = pd.read_csv('C:/Users/ibuba/Kuliah/Semester 5/SainsData/WorkshopAnalisaMediaSosial/data')
df.drop(columns=["Unnamed: 0"], inplace=True)
df.dropna(inplace=True)

# Deskripsi singkat di tampilan awal
st.title("Pencarian Lowongan Pekerjaan di Indonesia")
st.write("""
    Aplikasi ini membantu Anda mencari lowongan pekerjaan di berbagai kota di Indonesia.
    Anda dapat memfilter lowongan berdasarkan kota, tipe pekerjaan, dan jam kerja, serta
    melihat persebaran lowongan tersebut pada peta interaktif.
""")

# Filter di bagian atas laman
st.subheader("Filter Lowongan")
selected_city = st.multiselect("Pilih Kota", options=df["Kota"].unique(), default=[])
selected_job_type = st.multiselect("Pilih Tipe Pekerjaan", options=df["Type"].unique(), default=[])
selected_work_hours = st.multiselect("Pilih Jam Kerja", options=df["Work Hours"].unique(), default=[])

# Jika filter tidak diisi, maka tampilkan semua data
if not selected_city:
    selected_city = df["Kota"].unique()

if not selected_job_type:
    selected_job_type = df["Type"].unique()

if not selected_work_hours:
    selected_work_hours = df["Work Hours"].unique()

# Fungsi untuk membuat URL menjadi clickable
def make_clickable(url):
    return f'<a href="{url}" target="_blank">{url}</a>'

# Filter data berdasarkan pilihan user
filtered_data = df[
    (df["Kota"].isin(selected_city)) &
    (df["Type"].isin(selected_job_type)) &
    (df["Work Hours"].isin(selected_work_hours))
]

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

# Menampilkan peta dengan data yang difilter
st.write("### Peta Lowongan Pekerjaan")
m = generate_map(filtered_data)
st_folium(m, width=700, height=500)

# Pagination setup
st.write("### Lowongan Pekerjaan")

# Pengaturan pagination
items_per_page = 10
total_items = filtered_data.shape[0]
total_pages = (total_items // items_per_page) + (1 if total_items % items_per_page > 0 else 0)

# Membuat CSS untuk memastikan tabel tidak berada di tengah dan memperbesar tombol pagination
st.write("""
    <style>
    table {
        width: 100%;
        table-layout: auto;
        margin-left: 0;
    }
    .pagination-button {
        padding: 10px 20px;
        font-size: 16px;
        margin: 5px;
        display: inline-block;
    }
    .pagination-container {
        text-align: left;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Fungsi untuk menampilkan nomor halaman dengan 3 awal dan 3 akhir
def display_page_numbers(total_pages, current_page):
    page_numbers = []
    cols = st.columns(min(total_pages, 10))  # Membatasi maksimal 10 kolom

    # Menentukan nomor halaman yang akan ditampilkan
    if total_pages <= 6:
        page_numbers = list(range(1, total_pages + 1))  # Jika halaman kurang dari 6, tampilkan semua
    else:
        # Menampilkan 3 halaman awal, 3 halaman akhir, dan halaman di sekitar current_page
        if current_page <= 3:
            page_numbers = [1, 2, 3, '...', total_pages - 2, total_pages - 1, total_pages]
        elif current_page > total_pages - 3:
            page_numbers = [1, 2, 3, '...', total_pages - 2, total_pages - 1, total_pages]
        else:
            page_numbers = [1, 2, 3, '...', current_page - 1, current_page, current_page + 1, '...', total_pages - 2, total_pages - 1, total_pages]

    # Menampilkan tombol
    pagination_container = st.container()
    with pagination_container:
        for page_num in page_numbers:
            if page_num == '...':
                st.write("...")
            else:
                if st.button(f"{page_num}", key=page_num):
                    return page_num

    return current_page

# Awal halaman (1)
if 'page_number' not in st.session_state:
    st.session_state.page_number = 1

# Pilihan halaman menggunakan tombol angka
current_page = display_page_numbers(total_pages, st.session_state.page_number)

# Update session state jika halaman berubah
st.session_state.page_number = current_page

# Menentukan batas data yang ditampilkan
start_idx = (st.session_state.page_number - 1) * items_per_page
end_idx = start_idx + items_per_page

# Membatasi data sesuai dengan halaman yang dipilih
paginated_data = filtered_data.iloc[start_idx:end_idx]

# Menampilkan tabel dengan data terfilter dan paginated
selected_columns = ["Kota", "Company Name", "Job Title", "URL", "Type", "Work Hours"]

st.write(paginated_data[selected_columns].to_html(escape=False), unsafe_allow_html=True)

# Informasi halaman
st.write(f"Menampilkan halaman {st.session_state.page_number} dari {total_pages} halaman.")
