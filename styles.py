# -*- coding: utf-8 -*-
"""
Estilos CSS e Temas para o Dashboard BI
Identidade Visual: DefenDelas — "Ao seu lado, quando você mais precisa."
"""

# ------------------------------------------------------------------
# Paleta oficial da marca DefenDelas (extraída do logo)
# ------------------------------------------------------------------
BRAND_PURPLE       = "#654D9D"   # Roxo principal
BRAND_PURPLE_DARK  = "#4A3873"   # Roxo escuro (gradientes/contraste)
BRAND_PURPLE_LIGHT = "#8B7BB8"   # Roxo claro / lavanda
BRAND_GREEN        = "#9EC44D"   # Verde principal
BRAND_GREEN_DARK    = "#7CA33A"  # Verde escuro
BRAND_PEACH         = "#FCE6DB"  # Pêssego / creme (fundo suave)
BRAND_PEACH_DEEP     = "#E8A87C" # Pêssego mais saturado (para gráficos)
BRAND_OFFWHITE       = "#FBFBFB"

CUSTOM_CSS = f"""
<style>
    /* Google Fonts — Baloo 2 para títulos (combina com o logo arredondado),
       Plus Jakarta Sans para o corpo do texto */
    @import url('https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }}

    /* Fundo geral do app com leve tom pêssego */
    .stApp {{
        background-color: {BRAND_OFFWHITE};
    }}

    /* Top banner / Header styling */
    .main-header {{
        background: linear-gradient(135deg, {BRAND_PURPLE_DARK} 0%, {BRAND_PURPLE} 55%, {BRAND_PURPLE_LIGHT} 100%);
        padding: 1.6rem 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(101, 77, 157, 0.4);
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 5px solid {BRAND_GREEN};
    }}

    .main-header h1 {{
        font-family: 'Baloo 2', 'Plus Jakarta Sans', sans-serif;
        color: white !important;
        font-size: 2rem !important;
        font-weight: 800 !important;
        margin: 0 !important;
        letter-spacing: -0.02em;
    }}

    .main-header p {{
        color: rgba(255, 255, 255, 0.9) !important;
        margin: 0.3rem 0 0 0 !important;
        font-size: 0.95rem;
    }}

    .badge-status {{
        background: {BRAND_GREEN};
        color: {BRAND_PURPLE_DARK};
        backdrop-filter: blur(8px);
        padding: 0.4rem 0.9rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        border: 1px solid rgba(255, 255, 255, 0.4);
    }}

    /* KPI Metric Cards */
    .kpi-container {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 1rem;
        margin-bottom: 1.5rem;
    }}

    .kpi-card {{
        background: #ffffff;
        border-radius: 14px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 4px 15px rgba(101, 77, 157, 0.08);
        border: 1px solid {BRAND_PEACH};
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }}

    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(101, 77, 157, 0.16);
    }}

    .kpi-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, {BRAND_PURPLE}, {BRAND_GREEN});
    }}

    .kpi-title {{
        font-size: 0.82rem;
        font-weight: 600;
        color: {BRAND_PURPLE_DARK};
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.4rem;
        opacity: 0.75;
    }}

    .kpi-value {{
        font-family: 'Baloo 2', 'Plus Jakarta Sans', sans-serif;
        font-size: 1.85rem;
        font-weight: 800;
        color: {BRAND_PURPLE_DARK};
        line-height: 1.1;
        margin-bottom: 0.2rem;
    }}

    .kpi-subtitle {{
        font-size: 0.8rem;
        color: {BRAND_GREEN_DARK};
        font-weight: 600;
    }}

    /* Section Cards */
    .section-card {{
        background: #ffffff;
        border-radius: 14px;
        padding: 1.4rem;
        box-shadow: 0 4px 15px rgba(101, 77, 157, 0.06);
        border: 1px solid {BRAND_PEACH};
        margin-bottom: 1.5rem;
    }}

    .section-title {{
        font-family: 'Baloo 2', 'Plus Jakarta Sans', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: {BRAND_PURPLE_DARK};
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}

    /* Cabeçalhos de markdown (####, ###) usam a fonte de marca */
    h2, h3, h4 {{
        color: {BRAND_PURPLE_DARK} !important;
        font-family: 'Baloo 2', 'Plus Jakarta Sans', sans-serif !important;
    }}

    /* LGPD Privacy Warning Banner */
    .privacy-active-banner {{
        background: #F1F8E4;
        border: 1px solid {BRAND_GREEN};
        border-radius: 10px;
        padding: 0.75rem 1rem;
        color: {BRAND_GREEN_DARK};
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}

    /* Sidebar tweaks */
    [data-testid="stSidebar"] {{
        background-color: {BRAND_PEACH};
        border-right: 1px solid #f0d5c4;
    }}

    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] .stMarkdown p {{
        color: {BRAND_PURPLE_DARK} !important;
    }}

    /* Botões primários no padrão da marca */
    .stButton > button {{
        background-color: {BRAND_PURPLE} !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
    }}
    .stButton > button:hover {{
        background-color: {BRAND_PURPLE_DARK} !important;
    }}

    /* Botões de download no verde da marca */
    .stDownloadButton > button {{
        background-color: {BRAND_GREEN} !important;
        color: {BRAND_PURPLE_DARK} !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
    }}
    .stDownloadButton > button:hover {{
        background-color: {BRAND_GREEN_DARK} !important;
        color: white !important;
    }}

    /* Abas (tabs) */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
    }}
    .stTabs [aria-selected="true"] {{
        color: {BRAND_PURPLE} !important;
        border-bottom-color: {BRAND_PURPLE} !important;
    }}

    /* Toggle / slider de privacidade no verde da marca */
    [data-testid="stToggle"] [role="checkbox"][aria-checked="true"] {{
        background-color: {BRAND_GREEN} !important;
    }}
</style>
"""

# ------------------------------------------------------------------
# Paleta de Cores para Gráficos Plotly — derivada da identidade DefenDelas
# ------------------------------------------------------------------
COLOR_PALETTE = [
    BRAND_PURPLE,        # #654D9D
    BRAND_GREEN,         # #9EC44D
    BRAND_PEACH_DEEP,    # #E8A87C
    BRAND_PURPLE_DARK,   # #4A3873
    "#B9DE85",           # verde claro
    "#D4A5C9",           # rosa empoeirado (harmoniza com o roxo)
    BRAND_PURPLE_LIGHT,  # #8B7BB8
    "#F2C879",           # dourado quente (derivado do pêssego)
    "#6FA8A0",           # teal neutro de apoio
    "#A8A0C4",           # cinza-roxo neutro
]

# Escalas contínuas customizadas (para gráficos de calor / barras com gradiente)
PURPLE_SCALE = [
    [0.0, "#F1EDFB"],
    [0.5, BRAND_PURPLE_LIGHT],
    [1.0, BRAND_PURPLE_DARK],
]

GREEN_SCALE = [
    [0.0, "#F4F9E9"],
    [0.5, BRAND_GREEN],
    [1.0, BRAND_GREEN_DARK],
]

PLOTLY_LAYOUT = {
    'font': {'family': 'Plus Jakarta Sans, Segoe UI, sans-serif', 'color': BRAND_PURPLE_DARK},
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'margin': {'l': 30, 'r': 30, 't': 40, 'b': 30},
    'hovermode': 'closest',
    'colorway': COLOR_PALETTE,
}
/* --- AJUSTES PARA CELULAR E TELAS PEQUENAS --- */
@media (max-width: 768px) {
    /* Força as colunas do Streamlit a empilharem na vertical */
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
        margin-bottom: 10px;
    }

    /* Garante que o cartão ocupe 100% da largura da tela do celular */
    .kpi-card {
        width: 100% !important;
        box-sizing: border-box !important;
        margin-bottom: 12px !important;
    }

    /* Reduz levemente o tamanho do texto do título do cartão no celular para não quebrar */
    .kpi-title {
        font-size: 13px !important;
    }

    /* Ajusta o valor numérico do cartão */
    .kpi-value {
        font-size: 24px !important;
    }
}
