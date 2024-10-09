import folium
import pandas as pd
import streamlit as st
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# Membaca dataset
df = pd.read_csv('data clean')
df.dropna(inplace=True)

# Deskripsi singkat di tampilan awal
st.title("Pencarian Lowongan Kerja Pengolahan Data di Indonesia")
st.write("""
    Aplikasi ini membantu Anda mencari lowongan pekerjaan mengenai pengolahan data di berbagai kota di Indonesia.
    Anda dapat memfilter lowongan berdasarkan kota, tipe pekerjaan, dan jam kerja, serta
    melihat persebaran lowongan tersebut pada peta interaktif.
""")

# Filter di bagian atas laman
st.subheader("Filter Lowongan")
selected_city = st.multiselect("Pilih Daerah", options=df["Kota"].unique(), default=[])
selected_job_type = st.multiselect("Pilih Tipe Pekerjaan", options=df["Type"].unique(), default=[])
selected_work_hours = st.multiselect("Pilih Jam Kerja", options=df["Work Hours"].unique(), default=[])

# Jika filter tidak diisi, maka tampilkan semua data
if not selected_city:
    selected_city = df["Kota"].unique()

if not selected_job_type:
    selected_job_type = df["Type"].unique()

if not selected_work_hours:
    selected_work_hours = df["Work Hours"].unique()

# Filter data berdasarkan pilihan user
filtered_data = df[
    (df["Kota"].isin(selected_city)) &
    (df["Type"].isin(selected_job_type)) &
    (df["Work Hours"].isin(selected_work_hours))
]

# Fungsi untuk membuat nama perusahaan menjadi hyperlink
def make_clickable(name, url):
    return f'<a href="{url}" target="_blank">{name}</a>'

# Fungsi untuk menampilkan peta folium
def generate_map(filtered_data):
    # Membuat peta dengan posisi awal Indonesia
    m = folium.Map(location=[-0.789275, 113.921327], zoom_start=6)

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

# Membuat CSS untuk pagination horizontal
st.write("""
    <style>
    .pagination-button {
        padding: 10px 20px;
        font-size: 16px;
        margin: 5px;
        display: inline-block;
        text-align: center;
    }
    .pagination-container {
        display: flex;
        justify-content: left;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Fungsi untuk menampilkan nomor halaman secara horizontal dengan simbol navigasi
def display_page_numbers(total_pages, current_page):
    page_numbers = []

    # Tambahkan simbol '<' untuk pindah ke halaman pertama
    if current_page > 1:
        page_numbers.append('<')

    if total_pages <= 6:
        page_numbers.extend(list(range(1, total_pages + 1)))
    else:
        if current_page <= 3:
            page_numbers.extend(list(range(1, 6)) + ['...'] + [total_pages - 2, total_pages - 1, total_pages])
        elif current_page >= total_pages - 2:
            page_numbers.extend([1, 2, 3, '...'] + list(range(total_pages - 4, total_pages + 1)))
        else:
            page_numbers.extend([1, '...', current_page - 1, current_page, current_page + 1, '...'] + [total_pages - 2, total_pages - 1, total_pages])

    # Tambahkan simbol '>' untuk pindah ke halaman terakhir
    if current_page < total_pages:
        page_numbers.append('>')

    return page_numbers

# Awal halaman (1)
if 'page_number' not in st.session_state:
    st.session_state.page_number = 1

# Fungsi untuk memperbarui nomor halaman berdasarkan tombol yang diklik
def update_page_number(page_num, total_pages):
    if page_num == '<':
        st.session_state.page_number = 1
    elif page_num == '>':
        st.session_state.page_number = total_pages
    elif page_num != '...' and page_num != st.session_state.page_number:
        st.session_state.page_number = page_num

# Pilihan halaman menggunakan tombol angka
page_numbers = display_page_numbers(total_pages, st.session_state.page_number)

# Tampilkan pagination secara horizontal
pagination_container = st.container()
with pagination_container:
    cols = st.columns(len(page_numbers))
    for idx, page_num in enumerate(page_numbers):
        if page_num == '...':
            cols[idx].write("...")
        else:
            if cols[idx].button(f"{page_num}", key=page_num):
                update_page_number(page_num, total_pages)

# Menentukan batas data yang ditampilkan
start_idx = (st.session_state.page_number - 1) * items_per_page
end_idx = start_idx + items_per_page

# Membatasi data sesuai dengan halaman yang dipilih
paginated_data = filtered_data.iloc[start_idx:end_idx]

# Menggabungkan URL ke dalam kolom "Job Title"
paginated_data["Job Title"] = paginated_data.apply(lambda x: make_clickable(x["Job Title"], x["URL"]), axis=1)

# Menampilkan tabel dengan data terfilter dan paginated, pastikan kolom Company Name dapat diklik
selected_columns = ["Kota", "Company Name", "Job Title", "Type", "Work Hours"]
st.write(paginated_data[selected_columns].to_html(escape=False), unsafe_allow_html=True)

# Informasi halaman
st.write(f"Menampilkan halaman {st.session_state.page_number} dari {total_pages} halaman.")