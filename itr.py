import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Climate Risk Dashboard - ITR", layout="wide")

st.title("Climate Transition Risk Dashboard : Implied Temperature Rise (ITR)")
st.markdown("""
Cet indicateur mesure l'augmentation estimée de la température mondiale impliquée par la trajectoire d'émissions de gaz à effet de serre du portefeuille.
""")

# -----------------------------------------------------------------------------
# 1. CHARGEMENT DES DONNÉES
# Note : Ces fichiers CSV devront être générés par ton moteur de calcul (Calculation Engine)
# en amont, tout comme l'a fait ta camarade pour le risque physique.
# -----------------------------------------------------------------------------
try:
    assets = pd.read_csv("itr_assets_data.csv", sep=";")
    sector = pd.read_csv("itr_sector_indicator.csv", sep=";")
    asset_class = pd.read_csv("itr_asset_class_indicator.csv", sep=";")
    coverage = pd.read_csv("itr_coverage_metrics.csv", sep=";")
    summary_raw = pd.read_csv("itr_summary.csv", sep=";")
    
    # Transformation du summary pour un accès facile
    summary = summary_raw.set_index("metric")["value"]
    
    portfolio_itr = summary.get("portfolio_itr", 0.0)
    baseline_temp = summary.get("scenario_baseline", 1.5)
    weighted_dqs = summary.get("weighted_dqs", 0.0)
    
except FileNotFoundError:
    st.warning("⚠️ Fichiers CSV introuvables. Assurez-vous que les fichiers de données ITR sont dans le même dossier.")
    st.stop()

# -----------------------------------------------------------------------------
# 2. PORTFOLIO SUMMARY (KPIs)
# -----------------------------------------------------------------------------
st.header("Portfolio Summary")

col1, col2, col3 = st.columns(3)

# Calcul du delta par rapport au scénario de base
delta_baseline = portfolio_itr - baseline_temp

# Affichage des KPIs
col1.metric(
    label="Portfolio ITR", 
    value=f"{portfolio_itr:.2f} °C", 
    delta=f"{delta_baseline:+.2f} °C vs Baseline", 
    delta_color="inverse" # Rouge si positif (mauvais pour le climat), vert si négatif
)
col2.metric(label="Scenario Baseline Temperature", value=f"{baseline_temp:.2f} °C")
col3.metric(label="Weighted Data Quality Score (DQS)", value=f"{weighted_dqs:.2f} / 5", help="1 = Best (Reported SBTi Target), 5 = Weakest (Default Assumption)")


# -----------------------------------------------------------------------------
# 3. VISUALISATIONS PAR SECTEUR ET CLASSE D'ACTIFS
# -----------------------------------------------------------------------------
st.header("ITR Breakdown")

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("ITR by Asset Class")
    fig_ac = px.bar(
        asset_class.sort_values("itr", ascending=False), 
        x="asset_class", 
        y="itr",
        color="itr",
        color_continuous_scale="Reds"
    )
    st.plotly_chart(fig_ac, use_container_width=True)

with col_chart2:
    st.subheader("Top 10 Sectors Contributing to ITR")
    # On isole les 10 secteurs les plus contributeurs
    top_sectors = sector.sort_values("itr", ascending=False).head(10)
    fig_sector = px.bar(
        top_sectors, 
        x="sector", 
        y="itr",
        color="itr",
        color_continuous_scale="Reds"
    )
    st.plotly_chart(fig_sector, use_container_width=True)


# -----------------------------------------------------------------------------
# 4. DISTRIBUTION ET QUALITÉ DES DONNÉES
# -----------------------------------------------------------------------------
st.header("ITR Distribution & Data Quality")

col_dist, col_cov = st.columns(2)

with col_dist:
    st.subheader("ITR Distribution Histogram")
    # Histogramme de la distribution des ITR des contreparties
    fig_hist = px.histogram(
        assets, 
        x="itr", 
        nbins=30,
        color_discrete_sequence=["#EF553B"]
    )
    fig_hist.add_vline(x=baseline_temp, line_dash="dash", line_color="green", annotation_text="Scenario Baseline")
    st.plotly_chart(fig_hist, use_container_width=True)

with col_cov:
    st.subheader("Coverage Metrics (Reduction Rate Source)")
    # Graphique circulaire (Donut) pour montrer % SBTi, Proxy sectoriel, Défaut
    fig_cov = px.pie(
        coverage, 
        values="percentage", 
        names="source", 
        hole=0.4,
        color="source",
        color_discrete_map={
            "SBTi Target": "#00CC96", 
            "Sector Proxy": "#FFA15A", 
            "Broad Default": "#EF553B"
        }
    )
    st.plotly_chart(fig_cov, use_container_width=True)


# -----------------------------------------------------------------------------
# 5. TABLEAU DÉTAILLÉ (DRILL-DOWN)
# -----------------------------------------------------------------------------
st.header("Counterparty-level Drill-down Data")

# Sélection des colonnes spécifiques requises par les spécifications
display_columns = [
    "counterparty_id", "sector", "exposure", "weight", 
    "current_intensity", "reduction_rate", "source", 
    "itr", "dqs", "outlier_flag"
]

# On filtre les colonnes existantes pour éviter les erreurs si le CSV est incomplet
existing_cols = [col for col in display_columns if col in assets.columns]

st.dataframe(assets[existing_cols].head(1000))