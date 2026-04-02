import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ========================
# CONFIG
# ========================
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

sns.set_theme(style="whitegrid")
plt.rcParams['figure.dpi'] = 120

# ========================
# LOAD DATA
# ========================
@st.cache_data
def load_data():
    day_df = pd.read_csv("dashboard/main_data.csv")
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    return day_df

@st.cache_data
def load_hour_data():
    hour_df = pd.read_csv("data/hour.csv")
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

    season_map     = {1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'}
    weather_map    = {1:'Clear', 2:'Mist', 3:'Light Snow/Rain', 4:'Heavy Rain'}
    workingday_map = {0:'No', 1:'Yes'}
    month_map      = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
                      7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
    yr_map         = {0:'2011', 1:'2012'}

    hour_df['season']     = hour_df['season'].map(season_map)
    hour_df['weathersit'] = hour_df['weathersit'].map(weather_map)
    hour_df['workingday'] = hour_df['workingday'].map(workingday_map)
    hour_df['mnth']       = hour_df['mnth'].map(month_map)
    hour_df['yr']         = hour_df['yr'].map(yr_map)

    def categorize_hour(hr):
        if 0 <= hr <= 5:     return 'Dini Hari'
        elif 6 <= hr <= 9:   return 'Pagi'
        elif 10 <= hr <= 14: return 'Siang'
        elif 15 <= hr <= 18: return 'Sore'
        else:                return 'Malam'

    hour_df['time_category'] = hour_df['hr'].apply(categorize_hour)
    return hour_df

day_df  = load_data()
hour_df = load_hour_data()

# ========================
# SIDEBAR
# ========================
st.sidebar.image("https://img.icons8.com/emoji/96/bicycle-emoji.png", width=80)
st.sidebar.title("🚲 Bike Sharing")
st.sidebar.markdown("---")

year_options   = ['Semua'] + sorted(day_df['yr'].unique().tolist())
season_options = ['Semua'] + sorted(day_df['season'].unique().tolist())

selected_year   = st.sidebar.selectbox("Filter Tahun", year_options)
selected_season = st.sidebar.selectbox("Filter Musim", season_options)

st.sidebar.markdown("---")
st.sidebar.caption("Dashboard by: [Nama Kamu]")

# ========================
# APPLY FILTER — ke day_df DAN hour_df
# ========================
filtered_day  = day_df.copy()
filtered_hour = hour_df.copy()

if selected_year != 'Semua':
    filtered_day  = filtered_day[filtered_day['yr'] == selected_year]
    filtered_hour = filtered_hour[filtered_hour['yr'] == selected_year]

if selected_season != 'Semua':
    filtered_day  = filtered_day[filtered_day['season'] == selected_season]
    filtered_hour = filtered_hour[filtered_hour['season'] == selected_season]

# ========================
# HEADER
# ========================
st.title("🚲 Bike Sharing Dashboard")
st.markdown("Analisis pola peminjaman sepeda berdasarkan cuaca, musim, dan waktu.")

# Info filter aktif
filter_info = []
if selected_year != 'Semua':   filter_info.append(f"Tahun: **{selected_year}**")
if selected_season != 'Semua': filter_info.append(f"Musim: **{selected_season}**")
if filter_info:
    st.info("Filter aktif → " + " | ".join(filter_info))

st.markdown("---")

# ========================
# METRIC CARDS
# ========================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Peminjaman",    f"{filtered_day['cnt'].sum():,.0f}")
col2.metric("Rata-rata Harian",    f"{filtered_day['cnt'].mean():,.0f}")
col3.metric("Peminjaman Tertinggi",f"{filtered_day['cnt'].max():,.0f}")
col4.metric("Peminjaman Terendah", f"{filtered_day['cnt'].min():,.0f}")

st.markdown("---")

# ========================
# Q1: MUSIM & CUACA
# ========================
st.subheader("📊 Pengaruh Musim dan Cuaca terhadap Peminjaman Harian")
st.caption("Visualisasi ini menunjukkan bagaimana musim dan kondisi cuaca mempengaruhi jumlah peminjaman sepeda per hari.")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(7, 4))
    season_order = filtered_day.groupby('season')['cnt'].mean().sort_values(ascending=False).index
    sns.barplot(data=filtered_day, x='season', y='cnt',
                order=season_order, palette='Blues_d', ax=ax)
    ax.set_title('Rata-rata Peminjaman per Musim', fontsize=12)
    ax.set_xlabel('Musim')
    ax.set_ylabel('Rata-rata Peminjaman')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    for p in ax.patches:
        ax.annotate(f'{p.get_height():,.0f}',
                    (p.get_x() + p.get_width()/2., p.get_height()),
                    ha='center', va='bottom', fontsize=9)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(7, 4))
    weather_order = filtered_day.groupby('weathersit')['cnt'].mean().sort_values(ascending=False).index
    sns.barplot(data=filtered_day, x='weathersit', y='cnt',
                order=weather_order, palette='Oranges_d', ax=ax)
    ax.set_title('Rata-rata Peminjaman per Kondisi Cuaca', fontsize=12)
    ax.set_xlabel('Kondisi Cuaca')
    ax.set_ylabel('Rata-rata Peminjaman')
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
    ax.tick_params(axis='x', labelsize=8)
    for p in ax.patches:
        ax.annotate(f'{p.get_height():,.0f}',
                    (p.get_x() + p.get_width()/2., p.get_height()),
                    ha='center', va='bottom', fontsize=9)
    st.pyplot(fig)

# Penjelasan Q1
with st.expander("💡 Baca Penjelasan Insight"):
    top_season  = filtered_day.groupby('season')['cnt'].mean().idxmax()
    low_season  = filtered_day.groupby('season')['cnt'].mean().idxmin()
    top_weather = filtered_day.groupby('weathersit')['cnt'].mean().idxmax()
    low_weather = filtered_day.groupby('weathersit')['cnt'].mean().idxmin()
    top_season_val  = filtered_day.groupby('season')['cnt'].mean().max()
    low_season_val  = filtered_day.groupby('season')['cnt'].mean().min()
    top_weather_val = filtered_day.groupby('weathersit')['cnt'].mean().max()
    low_weather_val = filtered_day.groupby('weathersit')['cnt'].mean().min()

    st.markdown(f"""
    **Temuan Utama:**
    - Musim **{top_season}** mencatat rata-rata peminjaman tertinggi ({top_season_val:,.0f} peminjaman/hari),
      sementara musim **{low_season}** menjadi yang terendah ({low_season_val:,.0f} peminjaman/hari).
    - Cuaca **{top_weather}** mendukung peminjaman terbanyak ({top_weather_val:,.0f}/hari),
      sedangkan kondisi **{low_weather}** membuat jumlah peminjaman turun drastis ({low_weather_val:,.0f}/hari).
    - **Artinya:** Semakin hangat musim dan semakin cerah cuaca, semakin banyak orang meminjam sepeda.
      Operator dapat memanfaatkan informasi ini untuk mengatur ketersediaan armada sesuai musim.
    """)

st.markdown("---")

# ========================
# Q2: POLA PER JAM
# ========================
st.subheader("⏰ Pola Peminjaman per Jam: Hari Kerja vs Hari Libur")
st.caption("Visualisasi ini menunjukkan perbedaan pola peminjaman sepeda antara hari kerja dan hari libur berdasarkan jam.")

hourly_workday = filtered_hour.groupby(['hr', 'workingday'])['cnt'].mean().reset_index()
hourly_workday.columns = ['Hour', 'Workingday', 'Mean']

fig, ax = plt.subplots(figsize=(14, 5))
colors = {'Yes': '#2196F3', 'No': '#FF9800'}
for workingday, group in hourly_workday.groupby('Workingday'):
    label = 'Hari Kerja' if workingday == 'Yes' else 'Hari Libur'
    ax.plot(group['Hour'], group['Mean'],
            marker='o', markersize=4,
            label=label, color=colors[workingday], linewidth=2)
ax.set_title('Rata-rata Peminjaman per Jam', fontsize=13)
ax.set_xlabel('Jam')
ax.set_ylabel('Rata-rata Peminjaman')
ax.set_xticks(range(0, 24))
ax.legend()
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
st.pyplot(fig)

# Penjelasan Q2
with st.expander("💡 Baca Penjelasan Insight"):
    workday_data  = hourly_workday[hourly_workday['Workingday'] == 'Yes']
    holiday_data  = hourly_workday[hourly_workday['Workingday'] == 'No']

    if not workday_data.empty and not holiday_data.empty:
        peak_workday_hr  = int(workday_data.loc[workday_data['Mean'].idxmax(), 'Hour'])
        peak_workday_val = workday_data['Mean'].max()
        peak_holiday_hr  = int(holiday_data.loc[holiday_data['Mean'].idxmax(), 'Hour'])
        peak_holiday_val = holiday_data['Mean'].max()

        st.markdown(f"""
        **Temuan Utama:**
        - Pada **hari kerja**, puncak peminjaman terjadi di jam **{peak_workday_hr:02d}.00**
          ({peak_workday_val:,.0f} peminjaman rata-rata). Pola ini bersifat *bimodal* —
          ada dua lonjakan di pagi hari (berangkat kerja) dan sore hari (pulang kerja).
        - Pada **hari libur**, puncak terjadi di jam **{peak_holiday_hr:02d}.00**
          ({peak_holiday_val:,.0f} peminjaman rata-rata), mencerminkan aktivitas santai di siang hari.
        - **Artinya:** Sepeda lebih sering digunakan sebagai transportasi commuter di hari kerja,
          dan sebagai sarana rekreasi di hari libur.
        """)

st.markdown("---")

# ========================
# CLUSTERING
# ========================
st.subheader("🕐 Segmentasi Waktu Berdasarkan Volume Peminjaman")
st.caption("Jam dalam sehari dikelompokkan ke dalam 5 kategori waktu untuk melihat distribusi peminjaman sepeda.")

time_stats = filtered_hour.groupby('time_category')['cnt'].agg(['mean', 'sum']).reset_index()
time_stats.columns = ['Kategori Waktu', 'Rata-rata', 'Total']
time_stats['Rata-rata'] = time_stats['Rata-rata'].round(2)

palette = {
    'Dini Hari': '#1a237e', 'Pagi': '#42a5f5',
    'Siang': '#ffca28', 'Sore': '#ef6c00', 'Malam': '#4a148c'
}

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(7, 4))
    ax0_data = time_stats.sort_values('Rata-rata', ascending=False)
    bars = ax.bar(
        ax0_data['Kategori Waktu'].astype(str),
        ax0_data['Rata-rata'],
        color=[palette.get(k, '#cccccc') for k in ax0_data['Kategori Waktu'].astype(str)]
    )
    ax.set_title('Rata-rata Peminjaman per Kategori Waktu', fontsize=12)
    ax.set_xlabel('Kategori Waktu')
    ax.set_ylabel('Rata-rata Peminjaman')
    for bar in bars:
        ax.annotate(f'{bar.get_height():,.0f}',
                    (bar.get_x() + bar.get_width()/2., bar.get_height()),
                    ha='center', va='bottom', fontsize=9)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(7, 4))
    time_order = ['Dini Hari', 'Pagi', 'Siang', 'Sore', 'Malam']
    plot_data  = time_stats.set_index('Kategori Waktu').reindex(time_order).dropna()
    ax.pie(
        plot_data['Total'],
        labels=plot_data.index,
        colors=[palette.get(k, '#cccccc') for k in plot_data.index],
        autopct='%1.1f%%', startangle=90,
        textprops={'fontsize': 10}
    )
    ax.set_title('Proporsi Total Peminjaman per Kategori Waktu', fontsize=12)
    st.pyplot(fig)

# Penjelasan Clustering
with st.expander("💡 Baca Penjelasan Insight"):
    if not time_stats.empty:
        top_cat = time_stats.loc[time_stats['Rata-rata'].idxmax(), 'Kategori Waktu']
        low_cat = time_stats.loc[time_stats['Rata-rata'].idxmin(), 'Kategori Waktu']
        top_val = time_stats['Rata-rata'].max()
        low_val = time_stats['Rata-rata'].min()

        st.markdown(f"""
        **Temuan Utama:**
        - Kategori **{top_cat}** memiliki rata-rata peminjaman tertinggi ({top_val:,.0f} peminjaman/jam),
          menjadikannya periode tersibuk dalam sehari.
        - Kategori **{low_cat}** adalah periode paling sepi ({low_val:,.0f} peminjaman/jam).
        - **Artinya:** Operator dapat mengoptimalkan ketersediaan sepeda dengan memastikan
          stok penuh di jam **{top_cat}** dan mengurangi armada di jam **{low_cat}**
          untuk efisiensi operasional.
        """)