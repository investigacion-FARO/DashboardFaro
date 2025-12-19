import os
from pathlib import Path
import altair as alt
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuración de página PRIMERO
st.set_page_config(
    page_title="Herramienta de Seguimiento FARO", 
    layout="wide", 
    page_icon="📊",
    initial_sidebar_state="expanded"
)

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# --- CONSTANTES Y RUTAS ---
@st.cache_data(show_spinner=False)
def get_short_names(unique_indicators: list) -> dict:
    """
    Usa IA para acortar nombres de indicadores. 
    Si falla o no hay API Key, usa una limpieza simple por Regex.
    """
    # 1. Fallback simple (Limpieza manual por si no hay IA)
    cleaned_map = {}
    import re
    for ind in unique_indicators:
        # Quita "1.1.1 " del inicio y deja el resto
        simple = re.sub(r'^\d+(\.\d+)*\s*', '', ind)
        # Toma las primeras 5 palabras
        short = " ".join(simple.split()[:5])
        cleaned_map[ind] = short

    # 2. Intento con IA
    if OpenAI is None:
        return cleaned_map
        
    api_key = "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" # Tu API Key
    if not api_key:
        return cleaned_map

    try:
        client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
        
        # Preparamos el prompt en lote para ahorrar tokens
        prompt_text = "Genera un nombre muy corto (max 4 palabras) y descriptivo para cada indicador financiero/KPI. Elimina códigos numéricos. Responde SOLO en formato JSON {original: corto}."
        prompt_text += f"\nLista: {unique_indicators}"

        resp = client.chat.completions.create(
            model="nvidia/nemotron-3-nano-30b-a3b:free", # Modelo gratuito/barato
            messages=[
                {"role": "system", "content": "Eres un experto en dashboards. Resumes textos largos en etiquetas cortas."},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.1,
            response_format={"type": "json_object"} 
        )
        import json
        ai_map = json.loads(resp.choices[0].message.content)
        # Mezclamos con el fallback por si la IA alucina u olvida alguno
        cleaned_map.update(ai_map)
        return cleaned_map
    except Exception as e:
        return cleaned_map

# --- CONSTANTES Y RUTAS ---
# CAMBIO: Usamos la url raw para que pandas descargue el binario directamente
DATA_PATH = "https://github.com/Guallasamin/Dashboard_Faro/raw/main/Base%20de%20datos.xlsx"
SHEET_NAME = "Totales"
LOGO_PATH = "https://plataforma.grupofaro.org/pluginfile.php/1/theme_moove/logo/1759441070/logoFARO.png"

GROUPS = {
    "1": {"title": "Impacto de proyectos", "desc": "Beneficiarios y proyectos"},
    "2": {"title": "Alianzas y colaboración", "desc": "Articulación y redes"},
    "3": {"title": "Evidencia e influencia", "desc": "Productos y políticas"},
    "4": {"title": "Comunicación y reputación", "desc": "Posicionamiento y medios"},
    "5": {"title": "Sostenibilidad financiera", "desc": "Ingresos y diversificación"},
    "6": {"title": "Gestión y calidad", "desc": "Repositorio y aseguramiento"},
    "7": {"title": "Transformación digital", "desc": "Satisfacción tecnológica"},
    "8": {"title": "Talento y desarrollo", "desc": "Desempeño y capacitación"},
}

INDICATOR_META = {
    "1.1.1": {"tipo": "conteo", "unidad": "personas", "meta": None, "peso": 1},
    "1.1.2": {"tipo": "conteo", "unidad": "proyectos", "meta": None, "peso": 1},
    "1.1.3": {"tipo": "conteo", "unidad": "proyectos", "meta": None, "peso": 1},
    "2.1.1": {"tipo": "conteo", "unidad": "participaciones", "meta": None, "peso": 1},
    "2.1.2": {"tipo": "conteo", "unidad": "proyectos", "meta": None, "peso": 1},
    "2.2.1": {"tipo": "conteo", "unidad": "proyectos", "meta": None, "peso": 1},
    "2.2.2": {"tipo": "conteo", "unidad": "proyectos", "meta": None, "peso": 1},
    "2.2.3": {"tipo": "conteo", "unidad": "proyectos", "meta": None, "peso": 1},
    "2.3.1": {"tipo": "conteo", "unidad": "iniciativas", "meta": None, "peso": 1},
    "2.3.2": {"tipo": "conteo", "unidad": "iniciativas", "meta": None, "peso": 1},
    "3.1.1": {"tipo": "conteo", "unidad": "productos de evidencia", "meta": None, "peso": 1},
    "3.2.1": {"tipo": "conteo", "unidad": "políticas influenciadas", "meta": None, "peso": 1},
    "3.3.1": {"tipo": "conteo", "unidad": "programas escalables", "meta": None, "peso": 1},
    "4.1.1": {"tipo": "conteo", "unidad": "engagement digital", "meta": None, "peso": 1},
    "4.1.2": {"tipo": "conteo", "unidad": "visitas web/tiempo", "meta": 122000, "peso": 1},
    "4.2.1": {"tipo": "conteo", "unidad": "menciones/citas", "meta": None, "peso": 1},
    "4.2.2": {"tipo": "conteo", "unidad": "entrevistas/reportajes", "meta": None, "peso": 1},
    "4.2.3": {"tipo": "conteo", "unidad": "participaciones", "meta": None, "peso": 1},
    "4.2.4": {"tipo": "monto", "unidad": "free press", "meta": None, "peso": 1},
    "4.3.1": {"tipo": "porcentaje", "unidad": "% reconocimiento", "meta": None, "peso": 1},
    "4.3.2": {"tipo": "conteo", "unidad": "personas/organizaciones alcanzadas", "meta": None, "peso": 1},
    "5.1.1": {"tipo": "índice", "unidad": "índice sostenibilidad", "meta": None, "peso": 1},
    "6.1.1": {"tipo": "conteo", "unidad": "acciones en repositorio", "meta": None, "peso": 1},
    "6.2.1": {"tipo": "porcentaje", "unidad": "% aseguramiento calidad", "meta": None, "peso": 1},
    "7.1.1": {"tipo": "porcentaje", "unidad": "% satisfacción herramientas", "meta": None, "peso": 1},
    "8.1.1": {"tipo": "conteo", "unidad": "colaboradores con desempeño ≥ sat", "meta": None, "peso": 1},
    "8.1.2": {"tipo": "porcentaje", "unidad": "% colaboradores capacitados", "meta": None, "peso": 1},
}

COLORS = {
    "light_blue": "#46B6E6",
    "dark_blue": "#2F6EAC",
    "orange": "#EA692C",
    "amber": "#F19D38",
    "green": "#6EB54A",
    "lime": "#A9C846",
    "magenta": "#C12A7E",
    "pink": "#D96397",
    "grey": "#F0F2F6",
    "white": "#FFFFFF"
}

CATEGORICAL_PALETTE = [
    COLORS["light_blue"], COLORS["dark_blue"], COLORS["orange"],
    COLORS["amber"], COLORS["green"], COLORS["lime"],
    COLORS["magenta"], COLORS["pink"],
]
HEATMAP_SCALE = [COLORS["light_blue"], COLORS["lime"], COLORS["orange"]]

# --- ESTILOS CSS PERSONALIZADOS ---
def local_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');
        
        /* Fuente Global */
        html, body, [class*="css"]  {{
            font-family: 'Open Sans', sans-serif !important;
            color: #1F2937;
        }}

        /* Fondo general */
        .stApp {{
            background-color: #F8F9FA;
        }}

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {{
            background-color: #FFFFFF;
            border-right: 1px solid #E5E7EB;
        }}
        
        /* Títulos */
        h1, h2, h3 {{
            color: {COLORS['dark_blue']};
            font-weight: 700;
        }}
        
        /* Tarjetas (Containers) */
        div[data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"] {{
            # background-color: white; /* Precaución: esto puede afectar anidamientos */
        }}
        
        /* Métricas personalizadas */
        div[data-testid="stMetric"] {{
            background-color: #FFFFFF;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border: 1px solid #E5E7EB;
            text-align: center;
        }}
        div[data-testid="stMetricLabel"] {{
            font-size: 0.9rem;
            color: #6B7280;
        }}
        div[data-testid="stMetricValue"] {{
            font-size: 1.6rem;
            color: {COLORS['dark_blue']};
            font-weight: 700;
        }}

        /* Botones y Inputs */
        .stSelectbox label, .stRadio label {{
            font-weight: 600;
            color: {COLORS['dark_blue']};
        }}
        
        /* Expander */
        .streamlit-expanderHeader {{
            background-color: #FFFFFF;
            border-radius: 8px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

local_css()

# --- FUNCIONES DE CARGA Y PROCESAMIENTO ---

@st.cache_data(show_spinner=False)
def load_data(path: str, sheet: str) -> pd.DataFrame:  # <--- CAMBIO: path ahora es str
    # Pandas lee URLs directamente
    df_raw = pd.read_excel(path, sheet_name=sheet)
    header_row = df_raw.iloc[0]    
    df = df_raw.iloc[1:].copy()
    df.rename(columns={"Unnamed: 1": "Desagregacion"}, inplace=True)
    df["Indicador"] = df["Indicador"].ffill()
    df["Desagregacion"] = df["Desagregacion"].fillna("Total").astype(str).str.strip()
    df["Indicador"] = df["Indicador"].astype(str).str.strip()

    tidy_frames = []
    cols = list(df_raw.columns)
    for year in range(2024, 2029):
        prefix = f"Resultado del indicador {year}"
        if prefix not in cols:
            continue
        start = cols.index(prefix)
        year_cols = cols[start : start + 7]
        comp_names = header_row.iloc[start : start + 7].tolist()
        rename_map = {col: comp for col, comp in zip(year_cols, comp_names)}
        temp = df[["Indicador", "Desagregacion"] + year_cols].rename(columns=rename_map)
        temp["Año"] = year
        tidy = temp.melt(
            id_vars=["Indicador", "Desagregacion", "Año"],
            var_name="Componente",
            value_name="Valor",
        )
        tidy = tidy.drop_duplicates(subset=["Indicador", "Desagregacion", "Año", "Componente", "Valor"])
        tidy_frames.append(tidy)

    tidy_df = pd.concat(tidy_frames, ignore_index=True)
    tidy_df["Valor"] = pd.to_numeric(tidy_df["Valor"], errors="coerce")
    tidy_df = tidy_df.dropna(subset=["Valor"])
    tidy_df = tidy_df.sort_values("Valor", ascending=False).drop_duplicates(
        subset=["Indicador", "Desagregacion", "Año", "Componente"],
        keep="first",
    )
    tidy_df["Eje"] = tidy_df["Indicador"].str.extract(r"^(\d)").fillna("Otros")
    tidy_df["NombreEje"] = tidy_df["Eje"].map(lambda x: GROUPS.get(x, {}).get("title", "Otros"))
    tidy_df["Unidad"] = tidy_df["Indicador"].apply(lambda x: meta_for_indicator(x)["unidad"])
    if "Comentario" not in tidy_df.columns:
        tidy_df["Comentario"] = ""

    tidy_df["score_normalizado"] = compute_scores(tidy_df)
    return tidy_df

def meta_for_indicator(indicador: str):
    for prefix, meta in INDICATOR_META.items():
        if indicador.startswith(prefix):
            return meta
    return {"tipo": "conteo", "unidad": "unidades", "meta": None, "peso": 1}

def compute_scores(df: pd.DataFrame) -> pd.Series:
    scores = []
    for indicador, group in df.groupby("Indicador"):
        meta = meta_for_indicator(indicador)
        vals = group["Valor"].astype(float)
        if meta.get("meta") and meta["meta"] > 0:
            score = np.clip(vals / meta["meta"], 0, 1.2) * 100
        else:
            vals_adj = vals.copy()
            spread = vals_adj.max() - vals_adj.min()
            if meta.get("tipo") == "conteo" and spread > 20:
                vals_adj = np.log1p(vals_adj)
            p10, p90 = np.nanpercentile(vals_adj, [10, 90])
            denom = p90 - p10 if p90 - p10 != 0 else vals_adj.max() - vals_adj.min()
            if denom == 0:
                score = pd.Series(50, index=group.index)
            else:
                score = (vals_adj - p10) / denom * 100
                score = score.clip(0, 100)
        scores.append(score)
    return pd.concat(scores).sort_index()

def format_num(x: float) -> str:
    if pd.isna(x): return "N/D"
    if abs(x) >= 1_000_000: return f"{x/1_000_000:.1f}M"
    if abs(x) >= 1_000: return f"{x/1000:.1f}K"
    return f"{x:,.0f}"

# --- IA FUNCTIONALITY ---
def ai_answer(df: pd.DataFrame, question: str) -> str:
    if not question or question.strip() == "":
        return "Escribe una pregunta sobre los indicadores para poder responderte."
    if df.empty:
        return "No hay datos con los filtros actuales."
    if OpenAI is None:
        return "SDK OpenAI no instalado."

    api_key = "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"
    if not api_key:
        return "Falta API Key."

    try:
        client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    except Exception as exc:
        return f"Error cliente IA: {exc}"

    schema = ", ".join(df.columns)
    sample = df.to_dict(orient="records")
    resumen = {
        "n_indicadores": int(df["Indicador"].nunique()),
        "n_ejes": int(df["Eje"].nunique()),
        "anios": sorted(df["Año"].unique()),
        "componentes": sorted(df["Componente"].unique()),
    }
    contexto = {"schema": schema, "resumen": resumen, "sample": sample}
    
    user_prompt = f"""
    CONTEXT0: {contexto}
    PREGUNTA: {question}
    INSTRUCCIONES: Responde a detalle usando SOLO el contexto.
    Habla como analista de negocios, responde unicamente sobre el set de datos que te comparto, si no encuentras la respuesta responde que no la sabes. No hagas suposiciones. No inventes datos.
    RESPUESTA: quiero una respuesta clara y concisa, sin usar calificativos como extremo, mucho, poco basada en los datos proporcionados. Datos y Hechos.
    """

    try:
        resp = client.chat.completions.create(
            model="nvidia/nemotron-3-nano-30b-a3b:free",
            messages=[
                {"role": "system", "content": "Analista de FARO. Responde basado en datos estrictos."},
                {"role": "user", "content": user_prompt},
            ],
            stream=False,
            temperature=0.1,
        )
        return resp.choices[0].message.content
    except Exception as exc:
        return f"Error IA: {exc}"

# --- CARGA DATOS ---
try:
    data = load_data(DATA_PATH, SHEET_NAME)
except FileNotFoundError:
    st.error(f"❌ Archivo no encontrado: {DATA_PATH}")
    st.stop()
except Exception as exc:
    st.error(f"❌ Error al cargar datos: {exc}")
    st.stop()

# --- SIDEBAR & NAVEGACIÓN ---
current_year = int(data["Año"].max())
year_options = sorted(data["Año"].unique())
filtro_eje = []

with st.sidebar:
    if LOGO_PATH:
        st.image(LOGO_PATH, use_container_width=True)
    else:
        st.title("FARO")
    
    st.markdown("### 🧭 Navegación")
    page = st.radio(
        "",
        ["Nivel 1 – Resumen", "Nivel 2 – Comparativo", "Nivel 3 – Detalle"],
        index=0,
    )
    st.divider()
    st.caption("")
    # Filtros adicionales si se desean

filtered = data.copy()

# --- HEADER PRINCIPAL ---
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.title("Indicadores Estratégicos")
    st.markdown(f"**Vista:** {page}")
with col_head2:
    # Mini widget de IA
    with st.popover("🤖 Asistente IA", use_container_width=True):
        st.caption("¿En qué puedo ayudarte?")
        user_q = st.text_input("Tu pregunta...", key="ai_q")
        if user_q:
            with st.spinner("Analizando..."):
                st.info(ai_answer(data, user_q))

st.markdown("---")

if filtered.empty:
    st.warning("⚠️ No hay datos disponibles.")
    st.stop()

# --- UTILS GRÁFICOS ---
def apply_altair_theme(chart):
    return chart.configure_axis(
        grid=False, 
        domain=False,
        labelColor="#6B7280",
        titleColor="#374151"
    ).configure_view(
        strokeWidth=0
    ).configure_legend(
        labelLimit=0
    )

def color_rank(df: pd.DataFrame) -> pd.DataFrame:
    palette = CATEGORICAL_PALETTE
    df = df.copy().reset_index(drop=True)
    df["Color"] = [palette[min(i, len(palette) - 1)] for i in range(len(df))]
    return df

# --- VISTAS ---

## === NIVEL 1 ===
def render_level1(df: pd.DataFrame):
    st.markdown("### 📈 Resumen")
    
    # 1. Filtros y KPIs (Igual que antes)
    year_opts = sorted(df["Año"].unique())
    # Lógica para preseleccionar 2025
    idx_2025 = year_opts.index(2025) if 2025 in year_opts else len(year_opts)-1
    
    selected_year = st.selectbox("📅 Año Fiscal", year_opts, index=idx_2025)
    df_year = df[df["Año"] == selected_year].copy()
    
    avg_score = df_year["score_normalizado"].mean()
    c_kpi1, c_kpi2, c_kpi3, c_kpi4 = st.columns(4)
    c_kpi1.metric("Indicadores", df_year["Indicador"].nunique(), delta=f"Año {selected_year}", delta_color="off")
    c_kpi2.metric("Ejes", df_year["Eje"].nunique(), delta="Activos", delta_color="off")
    c_kpi3.metric("Desempeño Global", f"{avg_score:.1f}%", delta="Promedio Score", delta_color="normal")
    c_kpi4.metric("Última Act.", "Nov 2025", delta="Automático", delta_color="off")

    # 2. Treemap (Igual que antes)
    st.markdown(f"### 🏆 Performance por Eje ({selected_year})")
    c1, c2 = st.columns([3, 1])
    
    with c1:
        unique_inds = df_year["Indicador"].unique().tolist()
        short_names_map = get_short_names(unique_inds) # Usamos la función de caché IA
        df_year["Indicador_Corto"] = df_year["Indicador"].map(short_names_map).fillna(df_year["Indicador"])
        
        base_tree = (
            df_year.groupby(["Eje", "NombreEje", "Indicador", "Indicador_Corto", "Unidad"], as_index=False)
            .agg(score_mean=("score_normalizado", "mean"), valor_total=("Valor", "sum"))
        )
        base_tree = color_rank(base_tree)
        
        if not base_tree.empty:
            fig = px.treemap(
                base_tree,
                path=["NombreEje", "Indicador_Corto"],
                values="score_mean",
                color="NombreEje",
                color_discrete_sequence=CATEGORICAL_PALETTE,
                custom_data=["valor_total", "Unidad", "Indicador", "score_mean"]
            )
            fig.update_traces(
                texttemplate="<b>%{label}</b><br>%{customdata[0]:,.0f} %{customdata[1]}",
                hovertemplate="<b>%{customdata[2]}</b><br>Valor: %{customdata[0]:,.0f} %{customdata[1]}<br>Score: %{customdata[3]:.1f}",
                textinfo="label+text"
            )
            fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), height=450)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(f"No hay datos para {selected_year}")
    
    with c2:
        st.info("💡 **Guía:** El tamaño de la caja es el Score (cumplimiento). El número visible es el Valor de los Indicadores.")

    # --- SECCIÓN MODIFICADA: TENDENCIAS TEMPORALES ---
    st.markdown("### ⏳ Tendencias")
    eje_opts_lvl1 = list(GROUPS.keys())
    eje_sel_lvl1 = st.selectbox("Seleccionar Eje", eje_opts_lvl1, format_func=lambda x: f"{x}. {GROUPS[x]['title']}")
    
    # Filtramos la base para el gráfico de líneas
    evol_base = df[df["Eje"] == eje_sel_lvl1].copy()
    
    # 1. Aplicamos nombres cortos también aquí para que el tooltip no sea gigante
    # Nota: Usamos todos los indicadores del eje seleccionado, no solo los del año actual
    all_inds_trend = evol_base["Indicador"].unique().tolist()
    trend_short_map = get_short_names(all_inds_trend)
    evol_base["Ind_Corto"] = evol_base["Indicador"].map(trend_short_map).fillna(evol_base["Indicador"])

    # 2. Creamos una columna de texto formateado "Nombre: Valor"
    # Ejemplo: "Proyectos Realizados: 15"
    evol_base["Detalle_Texto"] = (
        "- " + evol_base["Ind_Corto"] + ": " + 
        evol_base["Valor"].apply(lambda x: f"{x:,.0f}")
    )
    
    # 3. Agrupamos concatenando el texto
    chart_base = evol_base[evol_base["Componente"] != "Total"].groupby(["Año", "Componente"], as_index=False).agg({
        "score_normalizado": "mean",
        "Valor": "sum",
        "Unidad": "first",
        # Aquí está la magia: unimos todas las filas de texto con un salto de línea
        "Detalle_Texto": lambda x: "\n".join(x) 
    })
    
    # 4. Graficamos
    chart_evol = alt.Chart(chart_base).mark_line(point=True, strokeWidth=3).encode(
        x=alt.X("Año:O", title=""),
        y=alt.Y("score_normalizado:Q", title="Score"),
        color=alt.Color("Componente:N", scale=alt.Scale(range=CATEGORICAL_PALETTE)),
        tooltip=[
            alt.Tooltip("Año", title="Año Fiscal"),
            alt.Tooltip("Componente", title="Área"),
            alt.Tooltip("Valor", title="Total Absoluto", format=",.0f"),
            # Mostramos la columna de texto concatenado
            alt.Tooltip("Detalle_Texto", title="Desglose de Indicadores")
        ]
    ).properties(height=350)
    
    st.altair_chart(apply_altair_theme(chart_evol), use_container_width=True)

# === NIVEL 2 ===
def render_level2(df: pd.DataFrame):
    st.markdown("### 📊 Comparativo de Áreas")
    
    # --- Barra de Herramientas (Filtros) ---
    with st.container():
        c_filt1, c_filt2, c_filt3 = st.columns([2, 1, 1])
        with c_filt1:
            l2_eje_opts = ["Todos"] + list(GROUPS.keys())
            l2_eje = st.selectbox("Eje Estratégico", l2_eje_opts, format_func=lambda x: "Todos los Ejes" if x == "Todos" else f"{x}. {GROUPS[x]['title']}")
        with c_filt2:
            l2_opts = sorted(df["Año"].unique(), reverse=True)
            # Lógica para preseleccionar 2025
            idx_2025 = l2_opts.index(2025) if 2025 in l2_opts else 0
            
            l2_year = st.selectbox("Año", l2_opts, index=idx_2025)
        with c_filt3:
            st.write("") # Espaciador

    # --- PREPARACIÓN DE DATOS ---
    
    # 1. BASE GLOBAL (Solo Año): Se usará para el MAPA DE CALOR
    # Esta base NO se ve afectada por el selectbox de Eje ni Indicadores
    l2_base_heatmap = df[df["Año"] == l2_year].copy()
    # Limpieza lógica estándar
    l2_base_heatmap = l2_base_heatmap[~((l2_base_heatmap["Indicador"].str.startswith("1.1.1")) & (l2_base_heatmap["Desagregacion"] != "Total"))]

    # 2. BASE ESPECÍFICA (Año + Filtros): Se usará para el RANKING
    l2_base_ranking = l2_base_heatmap.copy()

    # Aplicamos filtro de Eje SOLO a la base del Ranking
    if l2_eje != "Todos":
        l2_base_ranking = l2_base_ranking[l2_base_ranking["Eje"] == l2_eje]

    # Multiselect opcional (Solo afecta al Ranking)
    with st.expander("Filtrar por indicadores específicos", expanded=False):
        # Las opciones salen de la base filtrada por eje para ser consistentes
        l2_inds = sorted(l2_base_ranking["Indicador"].unique())
        l2_indicador = st.multiselect("Seleccionar Indicadores", l2_inds)
        if l2_indicador:
            l2_base_ranking = l2_base_ranking[l2_base_ranking["Indicador"].isin(l2_indicador)]

    if l2_base_heatmap.empty:
        st.warning("No hay datos disponibles para el año seleccionado.")
        return

    st.markdown("---")

    # ==========================================
    # GRÁFICO 1: MAPA DE CALOR (Heatmap)
    # ==========================================
    # USA: l2_base_heatmap (Sin filtros de eje/indicador)
    
    st.subheader("🔥 Intensidad por Eje y Área")

    base_heat = (
        l2_base_heatmap[(l2_base_heatmap["Componente"] != "Total")]
        .groupby(["Componente", "NombreEje", "Eje", "Unidad"], as_index=False)
        .agg({
            "score_normalizado": "mean",
            "Valor": "sum"
        })
    )
    
    chart_heat = (
        alt.Chart(base_heat)
        .mark_rect()
        .encode(
            x=alt.X("NombreEje:N", title="Eje Estratégico", axis=alt.Axis(labelAngle=-90)), 
            y=alt.Y("Componente:N", title="Área / Componente"),
            color=alt.Color("score_normalizado:Q", scale=alt.Scale(scheme="blues"), title="Score"),
            tooltip=[
                alt.Tooltip("NombreEje", title="Eje"),
                alt.Tooltip("Componente", title="Área"),
                alt.Tooltip("score_normalizado", title="Score Promedio", format=".1f"),
                alt.Tooltip("Valor", title="Valor Absoluto", format=",.0f"),
                alt.Tooltip("Unidad", title="Unidad")
            ]
        ).properties(height=500)
    )
    
    st.altair_chart(apply_altair_theme(chart_heat), use_container_width=True)

    st.write("")
    st.markdown("---")
    st.write("")

    # ==========================================
    # GRÁFICO 2: RANKING POR ÁREA (Barras)
    # ==========================================
    # USA: l2_base_ranking (Con todos los filtros aplicados)

    st.subheader(f"🏆 Ranking de Desempeño por Área ({l2_year})")
    
    if l2_eje == "Todos":
        st.info("👆 **Acción requerida:** Para ver el Ranking, por favor selecciona un **Eje Estratégico** específico en el filtro superior.")
    elif l2_base_ranking.empty:
        st.warning("No hay datos para los filtros específicos seleccionados.")
    else:
        # Agregación para Ranking usando la base filtrada
        base_rank = (
            l2_base_ranking[l2_base_ranking["Componente"] != "Total"]
            .groupby("Componente", as_index=False)
            .agg({
                "score_normalizado": "mean", 
                "Valor": "sum",
                "Unidad": "first"
            })
            .sort_values("score_normalizado", ascending=False)
        )
        
        # Colores condicionales
        base_rank["Color"] = np.where(
            base_rank["score_normalizado"] >= base_rank["score_normalizado"].mean(), 
            COLORS["dark_blue"], 
            COLORS["orange"]
        )
        
        # Construcción Gráfico Barras
        base_bar = alt.Chart(base_rank).encode(
            y=alt.Y("Componente:N", sort="-x", title=None)
        )

        bars = base_bar.mark_bar(cornerRadiusTopRight=3, cornerRadiusBottomRight=3).encode(
            x=alt.X("score_normalizado:Q", title="Índice de Desempeño (0-100)"),
            color=alt.Color("Color:N", scale=None),
            tooltip=[
                alt.Tooltip("Componente", title="Área"),
                alt.Tooltip("score_normalizado", title="Score", format=".1f"),
                alt.Tooltip("Valor", title="Valor Real", format=",.0f"),
                alt.Tooltip("Unidad", title="Unidad")
            ]
        )

        text_bar = base_bar.mark_text(align='left', baseline='middle', dx=3).encode(
            x=alt.X("score_normalizado:Q"),
            text=alt.Text("Valor", format=",.0f")
        )

        rule = alt.Chart(base_rank).mark_rule(color="black", strokeDash=[4, 4]).encode(x="mean(score_normalizado):Q")
        
        st.altair_chart(apply_altair_theme(bars + text_bar + rule).properties(height=400), use_container_width=True)

# === NIVEL 3 ===
def render_level3(df: pd.DataFrame):
    st.markdown("### 📝 Detalle de Indicadores")
    
    with st.expander("Configuración de Reporte", expanded=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            year_opts = sorted(df["Año"].unique())
            # Lógica para preseleccionar 2025
            idx_2025 = year_opts.index(2025) if 2025 in year_opts else len(year_opts)-1
            
            d_year = st.selectbox("Año Fiscal", year_opts, index=idx_2025)
        with c2:
            d_areas_opts = sorted(df["Componente"].unique())
            d_area = st.multiselect("Áreas", d_areas_opts, default=d_areas_opts)
        with c3:
            d_ejes_opts = list(GROUPS.keys())
            d_eje = st.multiselect("Ejes", d_ejes_opts, format_func=lambda x: f"Eje {x}")

    detail = df[df["Año"] == d_year].copy()
    if d_area: detail = detail[detail["Componente"].isin(d_area)]
    if d_eje: detail = detail[detail["Eje"].isin(d_eje)]
    
    # Limpieza de duplicados lógicos para tabla
    if detail["Indicador"].str.startswith("1.1.1").any():
        detail = detail[(~detail["Indicador"].str.startswith("1.1.1")) | (detail["Desagregacion"] == "Total")]

    if detail.empty:
        st.warning("No hay datos para mostrar.")
        return

    # Preparar tabla final
    display_df = detail[["Indicador", "Componente", "Unidad", "Valor", "score_normalizado"]].copy()
    display_df = display_df.rename(columns={
        "Componente": "Área", 
        "score_normalizado": "Desempeño (%)", 
        "Valor": "Resultado"
    })
    
    # Agregamos una columna de estado visual (opcional)
    display_df = display_df[["Indicador", "Área", "Resultado", "Unidad", "Desempeño (%)"]]

    st.markdown("#### Tabla de Resultados")
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Indicador": st.column_config.TextColumn("Indicador", width="large"),
            "Resultado": st.column_config.NumberColumn("Valor Real", format="%.0f"),
            "Desempeño (%)": st.column_config.ProgressColumn(
                "Score Normalizado",
                format="%.1f%%",
                min_value=0,
                max_value=100,
                width="medium"
            ),
        }
    )
    
    st.download_button(
        label="📥 Descargar Datos filtrados (CSV)",
        data=display_df.to_csv(index=False),
        file_name=f"reporte_faro_{d_year}.csv",
        mime="text/csv"
    )

# --- RENDERIZADO FINAL ---
if page == "Nivel 1 – Resumen":
    render_level1(filtered)
elif page == "Nivel 2 – Comparativo":
    render_level2(filtered)
else:
    render_level3(filtered)