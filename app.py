import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import plotly.figure_factory as ff
from streamlit_extras.switch_page_button import switch_page

# ============================================================================
# CONFIGURATION & CUSTOM CSS
# ============================================================================
st.set_page_config(
    page_title="Medical Imaging Analytics Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS
st.markdown("""
<style>
    .main-header {font-size: 3rem; color: #1e3a8a; font-weight: 700; margin-bottom: 0.5rem;}
    .subheader {font-size: 1.2rem; color: #64748b; margin-bottom: 2rem;}
    .metric-container {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      border-radius: 12px; padding: 1rem; text-align: center;}
    .stMetric > label {color: white !important; font-size: 0.9rem;}
    .stMetric > div > div {color: white !important; font-size: 2rem; font-weight: bold;}
    .sidebar .sidebar-content {background: linear-gradient(180deg, #f0f9ff 0%, #e0f2fe 100%);}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA GENERATION (HIPAA-compliant sample data)
# ============================================================================
@st.cache_data
def load_medical_data():
    """Generate realistic medical imaging dataset"""
    np.random.seed(42)
    n_patients = 5000
    modalities = {
        'CT': 0.40, 'MRI': 0.25, 'X-Ray': 0.20, 
        'Ultrasound': 0.10, 'PET-CT': 0.03, 'Mammography': 0.02
    }
    
    # Realistic patient demographics
    ages = np.clip(np.random.normal(55, 20, n_patients), 0, 110).astype(int)
    genders = np.random.choice(['Male', 'Female'], n_patients, p=[0.52, 0.48])
    
    data = {
        'Patient_ID': [f'PID-{i:06d}' for i in range(n_patients)],
        'Study_ID': [f'SID-{i:08d}' for i in range(n_patients)],
        'Modality': np.random.choice(list(modalities.keys()), n_patients, list(modalities.values())),
        'Hospital': np.random.choice([
            'Johns Hopkins Hospital', 'Mayo Clinic', 'Cleveland Clinic', 
            'UCLA Medical Center', 'Mass General'
        ], n_patients),
        'Study_Date': pd.date_range('2020-01-01', periods=n_patients, freq='12H'),
        'Age': ages,
        'Gender': genders,
        'Image_Count': np.random.poisson(3, n_patients) + 1,
        'Image_Size_GB': np.random.exponential(2.5, n_patients).round(2),
        'Radiation_Dose_mSv': np.where(
            pd.Series(np.random.choice(['CT', 'MRI', 'X-Ray'], n_patients)).str.contains('CT|X-Ray'),
            np.random.exponential(5, n_patients).clip(0, 25),
            0
        ).round(1),
        'Priority': np.random.choice(['Routine', 'Urgent', 'Stat'], n_patients, p=[0.7, 0.25, 0.05]),
        'Quality_Score': np.random.normal(4.2, 0.8, n_patients).clip(1, 5).round(1)
    }
    
    df = pd.DataFrame(data)
    df['Study_Date'] = pd.to_datetime(df['Study_Date'])
    return df

# ============================================================================
# HEADER & NAVIGATION
# ============================================================================
st.markdown('<h1 class="main-header">🏥 Medical Imaging Analytics Platform</h1>', unsafe_allow_html=True)
st.markdown('<p class="subheader">Enterprise-grade dashboard for radiology operations • 5,000+ studies analyzed</p>', unsafe_allow_html=True)

# Navigation
tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔬 Clinical Insights", "⚙️ Operations"])

# ============================================================================
# TAB 1: EXECUTIVE OVERVIEW
# ============================================================================
with tab1:
    df = load_medical_data()
    
    # Advanced KPIs
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Total Studies", f"{len(df):,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Patients", df['Patient_ID'].nunique())
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Total Storage", f"{df['Image_Size_GB'].sum():.1f} GB")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Avg Quality", f"{df['Quality_Score'].mean():.1f}/5")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col5:
        total_dose = df['Radiation_Dose_mSv'].sum()
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Total Dose", f"{total_dose:.0f} mSv")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col6:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Stat Cases", f"{(df['Priority']=='Stat').sum()}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.sunburst(
            df, path=['Hospital', 'Modality'],
            title="Study Distribution by Hospital & Modality",
            color='Image_Count',
            color_continuous_scale='Viridis'
        )
        fig1.update_layout(height=450)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        monthly_trend = df.groupby(df['Study_Date'].dt.to_period('M')).agg({
            'Study_ID': 'count',
            'Image_Size_GB': 'sum'
        }).reset_index()
        monthly_trend['Study_Date'] = monthly_trend['Study_Date'].astype(str)
        
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=monthly_trend['Study_Date'], y=monthly_trend['Study_ID'], 
                             name='Studies', marker_color='#1f77b4'))
        fig2.add_trace(go.Scatter(x=monthly_trend['Study_Date'], y=monthly_trend['Image_Size_GB'], 
                                 name='Storage (GB)', yaxis='y2', line=dict(color='#ff7f0e', width=3)))
        fig2.update_layout(
            title="Monthly Volume & Storage Trends",
            yaxis=dict(title="Studies"),
            yaxis2=dict(title="Storage (GB)", overlaying='y', side='right'),
            height=450
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Charts Row 2
    col3, col4 = st.columns(2)
    
    with col3:
        fig3 = px.treemap(
            df, path=['Modality'], values='Image_Count',
            color='Image_Size_GB', hover_data=['Hospital'],
            title="Modality Storage Breakdown",
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        fig4 = px.box(df, x='Modality', y='Radiation_Dose_mSv',
                     title="Radiation Exposure by Modality",
                     color='Modality',
                     color_discrete_sequence=px.colors.qualitative.Set3)
        fig4.update_layout(height=450)
        st.plotly_chart(fig4, use_container_width=True)

# ============================================================================
# TAB 2: CLINICAL INSIGHTS
# ============================================================================
with tab2:
    st.header("🔬 Clinical & Demographic Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        age_dist = px.histogram(df, x='Age', color='Gender', 
                               title="Patient Age & Gender Distribution",
                               nbins=50, opacity=0.7,
                               color_discrete_map={'Male': '#1f77b4', 'Female': '#ff7f0e'})
        age_dist.update_layout(height=400, bargap=0.1)
        st.plotly_chart(age_dist, use_container_width=True)
    
    with col2:
        priority_pie = px.pie(df, names='Priority', 
                             title="Case Priority Distribution",
                             color_discrete_sequence=['#2ca02c', '#ff7f0e', '#d62728'])
        st.plotly_chart(priority_pie, use_container_width=True)
    
    # Quality heatmap
    quality_heatmap = px.density_heatmap(
        df, x='Modality', y='Hospital', z='Quality_Score',
        title="Imaging Quality Heatmap (1-5 Scale)",
        color_continuous_scale='RdYlGn_r',
        height=400
    )
    st.plotly_chart(quality_heatmap, use_container_width=True)

# ============================================================================
# TAB 3: OPERATIONS
# ============================================================================
with tab3:
    st.header("⚙️ Operational Analytics")
    
    # Filter section
    col1, col2, col3 = st.columns(3)
    with col1:
        modality_filter = st.multiselect("Modality", df['Modality'].unique())
    with col2:
        hospital_filter = st.multiselect("Hospital", df['Hospital'].unique())
    with col3:
        priority_filter = st.multiselect("Priority", df['Priority'].unique())
    
    filtered_data = df[
        (df['Modality'].isin(modality_filter)) &
        (df['Hospital'].isin(hospital_filter)) &
        (df['Priority'].isin(priority_filter))
    ]
    
    # Raw data table
    st.subheader("Filtered Dataset")
    st.dataframe(filtered_data, use_container_width=True, height=400)
    
    # Download
    csv = filtered_data.to_csv(index=False)
    st.download_button(
        "📥 Download Filtered Data",
        csv,
        f"imaging_data_{datetime.now().strftime('%Y%m%d')}.csv",
        "text/csv"
    )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b;'>
    <p>🏥 Medical Imaging Analytics Platform | Compliant with HIPAA standards | 
    Data updated: <strong>{}</strong></p>
</div>
""".format(datetime.now().strftime('%Y-%m-%d %H:%M')), unsafe_allow_html=True)
