import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode

# Configuration de la page
st.set_page_config(page_title="Configuration", page_icon="⚙️", layout="wide")
st.image("logo_safran.png", width=100)
st.markdown("## ⚙️ Analyse Charge / Capacité - Configuration")

# Paramètres
col1, col2 = st.columns(2)
with col1:
    efficience = st.number_input("Efficacité (%)", value=60, min_value=50, max_value=100, step=1)
with col2:
    heures_semaine = st.number_input("Heures de travail par semaine", value=35, min_value=1)

# Données d'entrée
data = {
    "Poste de charge": [
        "343AH0", "343CAS", "343MPT", "343PLT", "343TOS", "343AS0",
        "343SCA", "343TCA", "343CTR", "343CTO", "343PT0"
    ],
    "Désignation": [
        "HELICO", "CAS", "MULTI PRODUIT", "PILOTE", "TOS", "SOUS ENSEMBLE TOS",
        "SOUS ENSEMBLE CAS", "SOUS ENSEMBLE CAS", "CONTRÔLE", "HABILLAGE", "PROTOS"
    ],
    "CDI": [1.5, 5.2, 1.4, 6.7, 1, 3.7, 0, 0, 5, 2, 1],
    "Intérim": [2, 2, 0.5, 0.5, 2, 1, 0, 0, 1, 1, 0],
}

df = pd.DataFrame(data)

# JS pour calcul dynamique côté client
js_capacite = JsCode("""
function(params) {
    let cdi = parseFloat(params.data.CDI || 0);
    let inter = parseFloat(params.data["Intérim"] || 0);
    let eff = %EFFICIENCE%;
    let hrs = %HEURES%;
    let cap = (cdi + inter) * eff / 100 * hrs;
    return cap.toFixed(1);
}
""".replace("%EFFICIENCE%", str(efficience)).replace("%HEURES%", str(heures_semaine)))

# Configuration AgGrid
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_columns(["CDI", "Intérim"], editable=True)
gb.configure_column("Capacité hebdo", valueGetter=js_capacite, type=["numericColumn", "numberColumnFilter", "customNumericFormat"], precision=1, editable=False)
gb.configure_grid_options(domLayout='normal')
grid_options = gb.build()

# Affichage tableau unique
st.markdown("### 🔧 Modifier CDI / Intérim et voir la capacité recalculée automatiquement :")
AgGrid(
    df,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.VALUE_CHANGED,
    allow_unsafe_jscode=True,
    fit_columns_on_grid_load=True,
    height=600,
    reload_data=False
)


st.markdown("---")
st.markdown("### 📥 Importer un fichier Excel pour l'analyse Charge / Capacité")

uploaded_file = st.file_uploader("Choisir un fichier Excel", type=["xlsx"])

if uploaded_file is not None:
    try:
        df_import = pd.read_excel(uploaded_file)
        st.success("✅ Fichier importé avec succès ! Aperçu ci-dessous :")
        AgGrid(df_import, height=400, fit_columns_on_grid_load=True)
    except Exception as e:
        st.error(f"❌ Erreur lors de la lecture du fichier : {e}")
