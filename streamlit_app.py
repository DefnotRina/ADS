import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np


def custom_title(text, size=30, is_bold=True, color="#FFFFFF", align="left"):
    """Renders text with specific size, weight, and alignment."""
    weight = "bold" if is_bold else "normal"
    
    html_code = f"""
    <p style="
        font-size: {size}px;
        font-weight: {weight};
        color: {color};
        text-align: {align};
        margin-bottom: 10px;
        font-family: sans-serif;
    ">
        {text}
    </p>
    """
    st.markdown(html_code, unsafe_allow_html=True)

# Set the title and icon for the browser tab
st.set_page_config(page_title="Meteorite Explorer", page_icon="☄️", layout="wide")

# --- DATA LOADING ---
@st.cache_data
def load_data():
    """Loads the pre-cleaned meteorite data."""
    file_path = "Meteorite_Landings_Cleaned.csv" 
    
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        st.error(f"Error: The cleaned data file '{file_path}' was not found.")
        st.error("Please run the `clean_data.py` script first to create it.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading cleaned data: {e}")
        return pd.DataFrame()
    
    if 'year_int' not in df.columns or 'mass_log' not in df.columns:
        st.error("Error: The cleaned file is missing required processed columns. Please re-run `clean_data.py`.")
        return pd.DataFrame()
        
    return df

# Load the data
df_meteorites = load_data()

if df_meteorites.empty:
    st.stop()

# --- Pre-calculate values for filters ---
min_log_mass = float(df_meteorites['mass_log'].min())
max_log_mass = float(df_meteorites['mass_log'].max())
min_year = int(df_meteorites['year_int'].min())
max_year = int(df_meteorites['year_int'].max())
slider_min_year = min_year
slider_max_year = max_year
if min_year == max_year:
    slider_min_year = min_year - 1
    slider_max_year = max_year + 1

unique_classes = sorted(df_meteorites['recclass'].unique())

PRESETS = {
    "All": (min_log_mass, max_log_mass),
    "0g - 1kg": (np.log10(0+1), np.log10(1000+1)),
    "1kg - 100kg": (np.log10(1001+1), np.log10(100000+1)),
    "100kg - 10 tonnes": (np.log10(100001+1), np.log10(10000000+1)),
    " > 10 tonnes": (np.log10(10000001+1), max_log_mass)
}

# --- MAIN PAGE LAYOUT ---
custom_title("☄️ NASA Meteorite Landings Explorer", size=60, is_bold=True)
st.markdown("This interactive app visualizes the [NASA Meteorite Landings dataset](https://data.nasa.gov/dataset/meteorite-landings).")
custom_title(
    "Made by: <span style='color:#FFBAE1'>Carla Katrina A. Leduna</span>", 
    size=14, 
    is_bold=False, 
    color="#AAAAAA", 
    align="left"
)

# --- Key Metrics (Uses FILTERED dataset) ---
st.header("Summary Statistics")

# CSS to create a card effect
st.markdown("""
<style>
.metric-card {
    background-color: #262730; 
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 10px;
    box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
    transition: 0.3s;
    text-align: center;
}
.metric-card:hover {
    box-shadow: 0 8px 16px 0 rgba(0,0,0,0.2);
}
.metric-title {
    font-size: 18px;
    color: #FAFAFA;
    margin-bottom: 10px;
}
.metric-value {
    font-size: 32px;
    color: #FF4B4B;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# --- PLACEHOLDER SECTION ---
metric_col1, metric_col2, metric_col3 = st.columns(3)
ph_metric1 = metric_col1.empty()
ph_metric2 = metric_col2.empty()
ph_metric3 = metric_col3.empty()

st.divider()

# --- NEW LAYOUT: Filters on Left, Map on Right ---
col_filter, col_map = st.columns([1, 5]) 

with col_filter:
    st.markdown("""
    <p style="
        font-size: 23px;
        font-weight: normal;
        color: #FFFFFF;
        text-align: left;
        margin-bottom: 10px;
        margin-top: 30px;
        font-family: sans-serif;
    ">
        Filters
    </p>
    """, unsafe_allow_html=True)
    custom_title("<i>Use these filters to explore the <b>Interactive World Map</b> and <b>Summary Statistics</b>.</i>", size = 12, is_bold=False)

    with st.expander("Mass", expanded=True):
        preset_choice = st.radio(
            "Select Mass Range:",
            PRESETS.keys()
        )
        selected_log_mass = PRESETS[preset_choice]

    with st.expander("Year", expanded=True):
        selected_year = st.slider(
            "Select year range:",
            min_value=slider_min_year,
            max_value=slider_max_year,
            value=(min_year, max_year)
        )
        if min_year == max_year:
            st.info(f"Note: All data is from the year {min_year}.")

    with st.expander("Fall Status", expanded=True):
        fall_status = st.radio(
            "Select fall status:",
            options=['All', 'Fell', 'Found'],
            index=0
        )
    
    with st.expander("Class", expanded=True):
        selected_classes = st.multiselect(
            "Select meteorite classes:",
            options=unique_classes,
            default=[] 
        )

# --- APPLY FILTERS ---
df_filtered = df_meteorites[
    (df_meteorites['mass_log'] >= selected_log_mass[0]) &
    (df_meteorites['mass_log'] <= selected_log_mass[1]) &
    (df_meteorites['year_int'] >= selected_year[0]) &
    (df_meteorites['year_int'] <= selected_year[1])
]

if fall_status != 'All':
    df_filtered = df_filtered[df_filtered['fall'] == fall_status]

if selected_classes:
    df_filtered = df_filtered[df_filtered['recclass'].isin(selected_classes)]


# --- POPULATE THE PLACEHOLDERS ---
total_count = df_filtered.shape[0]
total_mass_kg = df_filtered['mass (g)'].sum() / 1000
avg_mass_g = 0
if total_count > 0:
    avg_mass_g = df_filtered['mass (g)'].mean()

ph_metric1.markdown(f"""<div class="metric-card"><div class="metric-title">Meteorites</div><div class="metric-value">{total_count:,}</div></div>""", unsafe_allow_html=True)
ph_metric2.markdown(f"""<div class="metric-card"><div class="metric-title">Total Mass</div><div class="metric-value">{total_mass_kg:,.2f} kg</div></div>""", unsafe_allow_html=True)
ph_metric3.markdown(f"""<div class="metric-card"><div class="metric-title">Average Mass</div><div class="metric-value">{avg_mass_g:,.2f} g</div></div>""", unsafe_allow_html=True)


# --- Right Column (Map) ---
with col_map:
    st.header("Interactive World Map")

    if df_filtered.empty:
        st.warning("No meteorites found for the selected filters. Please expand your criteria.")
    else:
        fig = px.scatter_mapbox(
            df_filtered,
            lat="reclat", 
            lon="reclong", 
            color="mass_log",
            size="mass_log",   
            hover_name="name",
            custom_data=['mass (g)', 'year_int', 'recclass'],
            color_continuous_scale=px.colors.sequential.Reds,
            range_color=(min_log_mass, max_log_mass), 
            mapbox_style="carto-darkmatter",
            zoom=1,
            title="Meteorite Landings (Color & Size by Mass)",
            opacity=0.7
        )

        fig.update_traces(
            hovertemplate="""
            <b>%{hovertext}</b><br><br>
            Latitude = %{lat:.2f}<br>
            Longitude = %{lon:.2f}<br>
            Mass (g) = %{customdata[0]:,.0f}<br>
            Year = %{customdata[1]}<br>
            Class = %{customdata[2]}
            <extra></extra>
            """
        )

        fig.update_layout(
            margin={"r":0,"t":40,"l":0,"b":0},
            coloraxis_colorbar={
                'title':'Mass (g) - Log Scale'
            },
            # Removed modebar_remove to allow native zooming/panning
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )

        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True})
        
        st.markdown("""
        <p style="
            font-size: 12px; 
            font-style: italic; 
            color: #FFFFFF; 
            margin-left: 730px; 
            margin-top: 5px;
        ">
            This map is updated by the filters.
        </p>
        """, unsafe_allow_html=True)

st.divider()

# --- ADDITIONAL INSIGHTS (Use FULL dataset) ---
st.header("Global Overview")
st.markdown("Statistics representing the entire dataset")

col_insights1, col_insights2 = st.columns(2)

with col_insights1:
    # 1. Bar chart of Top 10 classifications
    st.subheader("Top 10 Meteorite Classes")
    class_counts = df_meteorites['recclass'].value_counts().nlargest(10).reset_index()
    class_counts.columns = ['Classification', 'Count']
    
    fig_class = px.bar(
        class_counts,
        x='Classification',
        y='Count',
        title="Most frequent classifications found.",
        color='Count',
        color_continuous_scale='Reds',
        template="plotly_dark"
    )
    
    fig_class.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        coloraxis_showscale=False,
        xaxis_title=None
    )
    
    fig_class.update_traces(
        hovertemplate="""
        Classification = %{x}<br>
        Count = %{y}
        <extra></extra>
        """
    )
    st.plotly_chart(fig_class, use_container_width=True)

with col_insights2:
    # 2. Histogram of Mass
    st.subheader("Mass Distribution")
    
    counts, bins = np.histogram(df_meteorites['mass_log'], bins=50)
    bin_centers = (bins[:-1] + bins[1:]) / 2
    
    hist_df = pd.DataFrame({
        'Mass (g) - Log Scale': bin_centers,
        'Count': counts
    })
    
    fig_mass_hist = px.bar(
        hist_df,
        x='Mass (g) - Log Scale',
        y='Count',
        color='Count',
        color_continuous_scale='Reds',
        title="Logarithmic scale showing the spread of meteorite weights.",
        template="plotly_dark"
    )
    
    fig_mass_hist.update_layout(
        xaxis_title="Mass (g) - Log Scale", 
        yaxis_title="Count",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        coloraxis_colorbar={
            'title':'Count'
        },
        bargap=0.01
    )
    
    fig_mass_hist.update_traces(
        hovertemplate="""
        Mass (g) - Log Scale = %{x:.2f}<br>
        Count = %{y}
        <extra></extra>
        """,
        width=bins[1] - bins[0]
    )
    st.plotly_chart(fig_mass_hist, use_container_width=True)

# --- NEW CHARTS (Use FULL dataset) ---

col_insights3, col_insights4 = st.columns(2)

with col_insights3:
    # 3. Line chart of discoveries over time
    st.subheader("Discovery Timeline")
    discoveries_by_year = df_meteorites['year_int'].value_counts().reset_index()
    discoveries_by_year.columns = ['Year', 'Count']
    discoveries_by_year = discoveries_by_year.sort_values('Year')
    
    # --- REPLACED px.line with go.Scatter for clean code and styling ---
    fig_line = go.Figure(go.Scatter(
        x=discoveries_by_year['Year'],
        y=discoveries_by_year['Count'],
        mode='lines',
        line=dict(color='#FFAB8F'),
        hovertemplate="Year = %{x}<br>Count = %{y}<extra></extra>"
    ))
    # -----------------------------------------------------------------
    
    fig_line.update_layout(
        title="Meteorite Discoveries per Year",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_line, use_container_width=True)

with col_insights4:
    # 4. Pie chart of Fell vs. Found
    st.subheader("Fell vs. Found")
    fall_counts = df_meteorites['fall'].value_counts().reset_index()
    fall_counts.columns = ['Status', 'Count']
    
    fig_pie = px.pie(
        fall_counts,
        names='Status',
        values='Count',
        color='Status',
        title="Proportion of observed falls vs. accidental finds.",
        template="plotly_dark",
        hole=0.3,
        color_discrete_map={'Found': "#F9413E", 'Fell': "#A20000"} 
    )
    fig_pie.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    fig_pie.update_traces(
        hovertemplate="""
        Status = %{label}<br>
        Count = %{value} (%{percent})
        <extra></extra>
        """
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# 5. Scatterplot of Year vs. Mass
st.subheader("Mass Trends Over Time")
fig_scatter = px.scatter(
    df_meteorites.sample(min(1000, len(df_meteorites))),
    x='year_int',
    y='mass_log',
    hover_name='name',
    custom_data=['mass (g)', 'year_int', 'recclass'],
    title="Correlation between year of discovery and meteorite mass.",
    template="plotly_dark",
    color='mass_log',
    color_continuous_scale=px.colors.sequential.Reds,
    opacity=0.6
)
fig_scatter.update_layout(
    xaxis_title="Year",
    yaxis_title="Mass (g) - Log Scale",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
fig_scatter.update_traces(
    hovertemplate="""
    <b>%{hovertext}</b><br><br>
    Year = %{x}<br>
    Mass (g) = %{customdata[0]:,.0f}<br>
    Class = %{customdata[2]}
    <extra></extra>
    """
)
st.plotly_chart(fig_scatter, use_container_width=True)


# --- Raw Data Table (Uses FULL dataset) ---
st.header("The Giants: Top 100 Largest Meteorites")
st.markdown("This table shows the largest meteorites in the **entire** dataset.")

df_top100 = df_meteorites.sort_values('mass (g)', ascending=False).head(100) 

# Select and rename columns for display
df_display = df_top100[['name', 'mass (g)', 'year_int', 'recclass', 'fall']].rename(
    columns={
        'name': 'Name',
        'mass (g)': 'Mass (g)',
        'year_int': 'Year',
        'recclass': 'Class',
        'fall': 'Fall'
    }
).reset_index(drop=True) 

# Show a sample of the data, sorted by mass
st.dataframe(
    df_display,
    use_container_width=True,
    hide_index=True 
)
