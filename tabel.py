import streamlit as st
import pandas as pd

# Contoh data
data = [
    {
        "Kota": "Jakarta",
        "Nama Perusahaan": "PT. ABC",
        "Job Title": "Data Scientist",
        "URL": "https://example.com/job1",
        "Tipe Pekerjaan": "Full-time",
        "Work Hours": "8 hours/day"
    },
    {
        "Kota": "Surabaya",
        "Nama Perusahaan": "PT. XYZ",
        "Job Title": "Web Developer",
        "URL": "https://example.com/job2",
        "Tipe Pekerjaan": "Part-time",
        "Work Hours": "4 hours/day"
    },
    {
        "Kota": "Bandung",
        "Nama Perusahaan": "PT. DEF",
        "Job Title": "Software Engineer",
        "URL": "https://example.com/job3",
        "Tipe Pekerjaan": "Full-time",
        "Work Hours": "8 hours/day"
    }
]

# Konversi data ke DataFrame
df = pd.DataFrame(data)

# Sidebar filters
st.sidebar.header("Filter")
selected_city = st.sidebar.multiselect("Pilih Kota", options=df["Kota"].unique(), default=df["Kota"].unique())
selected_job_type = st.sidebar.multiselect("Pilih Tipe Pekerjaan", options=df["Tipe Pekerjaan"].unique(), default=df["Tipe Pekerjaan"].unique())
selected_work_hours = st.sidebar.multiselect("Pilih Jam Kerja", options=df["Work Hours"].unique(), default=df["Work Hours"].unique())

# Filter data berdasarkan pilihan user
filtered_data = df[
    (df["Kota"].isin(selected_city)) &
    (df["Tipe Pekerjaan"].isin(selected_job_type)) &
    (df["Work Hours"].isin(selected_work_hours))
]

# Menampilkan tabel hasil filter
st.write("### Lowongan Pekerjaan")
st.dataframe(filtered_data)

# Menambahkan hyperlink ke URL
def make_clickable(url):
    return f'<a href="{url}" target="_blank">Link</a>'

# Menerapkan hyperlink pada kolom 'URL' 
filtered_data['URL'] = filtered_data['URL'].apply(make_clickable)

# Menampilkan tabel dengan hyperlink
st.write("### Lowongan dengan URL")
st.write(filtered_data.to_html(escape=False), unsafe_allow_html=True)
