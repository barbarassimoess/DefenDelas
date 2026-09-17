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
        color: {BRAND_PURPLE_DARK};
    }}

    /* Fundo geral do app com leve tom pêssego */
    .stApp {{
        background-color: {BRAND_OFFWHITE};
        color: {BRAND_PURPLE_DARK};
    }}

    /* Textos gerais e parágrafos */
    p, span, div {{
        color: {BRAND_PURPLE_DARK};
    }}

    /* Subtítulos e legendas do Streamlit sempre em roxo escuro bem legível */
    .stCaption, [data-testid="stCaptionContainer"], .stMarkdown small, small {{
        color: {BRAND_PURPLE_DARK} !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
        opacity: 0.95 !important;
        line-height: 1.4 !important;
    }}

    /* Rótulos de campos, seletores e filtros */
    label, [data-testid="stWidgetLabel"] label, [data-testid="stWidgetLabel"] p, .stWidgetLabel p {{
        color: {BRAND_PURPLE_DARK} !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
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

    .main-header h1, [data-testid="stHeader"] h1, .stMarkdown .main-header h1 {{
        font-family: 'Baloo 2', 'Plus Jakarta Sans', sans-serif !important;
        color: {BRAND_GREEN} !important;
        -webkit-text-fill-color: {BRAND_GREEN} !important;
        font-size: 2.1rem !important;
        font-weight: 800 !important;
        margin: 0 !important;
        letter-spacing: -0.02em !important;
        text-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
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
        font-size: 0.85rem;
        font-weight: 700;
        color: {BRAND_PURPLE_DARK} !important;
        text-transform: none;
        letter-spacing: 0.01em;
        margin-bottom: 0.4rem;
        opacity: 1 !important;
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

    /* =================================================================
       Abas (Tabs) - Compatibilidade 100% com Streamlit 1.62+ (React Aria)
       e versões anteriores (BaseWeb). Garante visibilidade total sem precisar do hover!
       ================================================================= */
    [data-testid="stTabs"] [role="tablist"],
    .stTabs [role="tablist"],
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px !important;
        border-bottom: 2px solid #E8E2F2 !important;
        padding-bottom: 2px !important;
        background-color: transparent !important;
    }}

    /* Botão de CADA aba */
    [data-testid="stTab"],
    [data-testid="stTabs"] button,
    [data-testid="stTabs"] [role="tab"],
    .stTabs [role="tab"],
    .stTabs [data-baseweb="tab"] {{
        height: auto !important;
        padding: 8px 16px !important;
        background-color: transparent !important;
        border: none !important;
        border-radius: 8px 8px 0 0 !important;
        transition: all 0.2s ease-in-out !important;
        opacity: 1 !important;
        visibility: visible !important;
    }}

    /* TEXTO DE TODAS AS ABAS (inativas e ativas) - SEMPRE VISÍVEL E ESCURO */
    [data-testid="stTab"],
    [data-testid="stTab"] *,
    [data-testid="stTab"] p,
    [data-testid="stTab"] span,
    [data-testid="stTab"] div,
    [data-testid="stTabs"] button *,
    [data-testid="stTabs"] [role="tab"] *,
    .stTabs [role="tab"] *,
    .stTabs [data-baseweb="tab"] * {{
        color: {BRAND_PURPLE_DARK} !important;
        -webkit-text-fill-color: {BRAND_PURPLE_DARK} !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        opacity: 0.92 !important;
        visibility: visible !important;
    }}

    /* Efeito de passar o mouse (Hover) em qualquer aba */
    [data-testid="stTab"]:hover,
    [data-testid="stTab"][data-hovered],
    [data-testid="stTabs"] button:hover,
    [data-testid="stTabs"] [role="tab"]:hover {{
        background-color: rgba(101, 77, 157, 0.08) !important;
    }}

    [data-testid="stTab"]:hover *,
    [data-testid="stTab"][data-hovered] *,
    [data-testid="stTabs"] button:hover *,
    [data-testid="stTabs"] [role="tab"]:hover * {{
        color: {BRAND_PURPLE} !important;
        -webkit-text-fill-color: {BRAND_PURPLE} !important;
        opacity: 1 !important;
    }}

    /* Aba selecionada / ativa */
    [data-testid="stTab"][data-selected],
    [data-testid="stTab"][aria-selected="true"],
    [data-testid="stTabs"] button[aria-selected="true"],
    [data-testid="stTabs"] [role="tab"][aria-selected="true"],
    .stTabs [aria-selected="true"] {{
        background-color: rgba(101, 77, 157, 0.12) !important;
        border-bottom: 3px solid {BRAND_PURPLE} !important;
    }}

    [data-testid="stTab"][data-selected] *,
    [data-testid="stTab"][aria-selected="true"] *,
    [data-testid="stTabs"] button[aria-selected="true"] *,
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] *,
    .stTabs [aria-selected="true"] * {{
        color: {BRAND_PURPLE} !important;
        -webkit-text-fill-color: {BRAND_PURPLE} !important;
        font-weight: 800 !important;
        opacity: 1 !important;
    }}

    /* Indicador de linha inferior da aba ativa no React-Aria (Streamlit 1.62+) */
    [data-testid="stTabs"] .react-aria-SelectionIndicator {{
        background-color: {BRAND_PURPLE} !important;
        height: 3px !important;
        border-radius: 3px !important;
    }}

    /* Indicador antigo BaseWeb highlight */
    .stTabs [data-baseweb="tab-highlight"] {{
        background-color: {BRAND_PURPLE} !important;
    }}

    /* Botões de rolagem das abas (elimina o bloco preto no tema escuro) */
    [data-testid="stTabsScrollLeft"],
    [data-testid="stTabsScrollRight"] {{
        background: {BRAND_OFFWHITE} !important;
        background-image: none !important;
        color: {BRAND_PURPLE_DARK} !important;
        border-radius: 6px !important;
        box-shadow: none !important;
    }}

    [data-testid="stTabsScrollLeft"] svg,
    [data-testid="stTabsScrollRight"] svg {{
        fill: {BRAND_PURPLE_DARK} !important;
        color: {BRAND_PURPLE_DARK} !important;
    }}

    /* Toggle / slider de privacidade no verde da marca */
    [data-testid="stToggle"] [role="checkbox"][aria-checked="true"] {{
        background-color: {BRAND_GREEN} !important;
    }}

    /* =================================================================
       Gráficos Plotly: Garante que TODOS os textos (eixos, ticks,
       rótulos, títulos e legendas) fiquem em roxo escuro legível.
       ================================================================= */
    .js-plotly-plot .plotly text,
    .js-plotly-plot .g-title text,
    .js-plotly-plot .xtitle text,
    .js-plotly-plot .ytitle text,
    .js-plotly-plot .xtick text,
    .js-plotly-plot .ytick text,
    .js-plotly-plot .legendtext,
    .js-plotly-plot .legendtitletext,
    .js-plotly-plot .pielabel text,
    .js-plotly-plot .annotation-text {{
        fill: {BRAND_PURPLE_DARK} !important;
        color: {BRAND_PURPLE_DARK} !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 600 !important;
    }}
</style>
"""

# ------------------------------------------------------------------
# Paleta de Cores para Gráficos Plotly — Tons escuros, nítidos e contrastados
# ------------------------------------------------------------------
COLOR_PALETTE = [
    BRAND_PURPLE,        # #654D9D
    BRAND_GREEN,         # #9EC44D
    BRAND_PEACH_DEEP,    # #E8A87C
    BRAND_PURPLE_DARK,   # #4A3873
    "#7CA33A",           # verde escuro
    "#B45309",           # âmbar / caramelo contrastado
    "#3B82F6",           # azul vibrante
    "#C026D3",           # magenta contrastado
    "#0D9488",           # teal profundo
    "#4338CA",           # índigo
]

# Escalas contínuas customizadas com alto contraste de texto e valores
PURPLE_SCALE = [
    [0.0, "#D3C7EE"],
    [0.5, BRAND_PURPLE],
    [1.0, BRAND_PURPLE_DARK],
]

GREEN_SCALE = [
    [0.0, "#D9EBB5"],
    [0.5, BRAND_GREEN],
    [1.0, BRAND_GREEN_DARK],
]

# Configuração de Layout Padrão para todos os gráficos Plotly (sem chaves que possam colidir com update_layout)
PLOTLY_LAYOUT = {
    'font': {
        'family': 'Plus Jakarta Sans, Segoe UI, sans-serif',
        'color': BRAND_PURPLE_DARK,
        'size': 12
    },
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'margin': {'l': 70, 'r': 40, 't': 50, 'b': 60},
    'hovermode': 'closest',
    'colorway': COLOR_PALETTE,
}

def apply_chart_theme(fig, left_margin=None, bottom_margin=None, top_margin=None, right_margin=None):
    """
    Aplica estilo institucional, fontes em roxo escuro legível, margens seguras e impede corte de rótulos externos nos gráficos.
    """
    # Atualiza fontes de eixos e legendas sem conflito de argumentos
    fig.update_xaxes(
        automargin=True,
        tickfont=dict(family='Plus Jakarta Sans, Segoe UI, sans-serif', color=BRAND_PURPLE_DARK, size=11),
        title_font=dict(family='Plus Jakarta Sans, Segoe UI, sans-serif', color=BRAND_PURPLE_DARK, size=12),
        gridcolor='#E8E2F2',
        linecolor='#E8E2F2'
    )
    fig.update_yaxes(
        automargin=True,
        tickfont=dict(family='Plus Jakarta Sans, Segoe UI, sans-serif', color=BRAND_PURPLE_DARK, size=11),
        title_font=dict(family='Plus Jakarta Sans, Segoe UI, sans-serif', color=BRAND_PURPLE_DARK, size=12),
        gridcolor='#E8E2F2',
        linecolor='#E8E2F2'
    )
    fig.update_layout(
        font=dict(family='Plus Jakarta Sans, Segoe UI, sans-serif', color=BRAND_PURPLE_DARK, size=12),
        legend=dict(
            font=dict(family='Plus Jakarta Sans, Segoe UI, sans-serif', color=BRAND_PURPLE_DARK, size=12)
        )
    )

    # Aplicação de margens específicas
    margins = {'l': 70, 'r': 40, 't': 50, 'b': 60}
    if left_margin is not None:
        margins['l'] = left_margin
    if bottom_margin is not None:
        margins['b'] = bottom_margin
    if top_margin is not None:
        margins['t'] = top_margin
    if right_margin is not None:
        margins['r'] = right_margin
    fig.update_layout(margin=margins)

    try:
        fig.update_traces(selector=dict(type='bar'), cliponaxis=False)
        fig.update_traces(selector=dict(type='scatter'), cliponaxis=False)
    except Exception:
        pass
    return fig
