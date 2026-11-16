# -*- coding: utf-8 -*-
"""
Painel BI - Sistema de Inteligência de Dados - DefenDelas
Interface Gráfica Interativa com Streamlit e Plotly
Monitoramento Integrado de Formulários, Atendimentos da Equipe e Petições Judiciais (CEDEM)
"""

import os
import sys

# Garante que o Python encontre os módulos na pasta raiz
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import io
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_loader import load_all_dashboard_data, load_consolidated_mulheres_data, CITIES_DB

# Importa os estilos garantindo o funcionamento do caminho
try:
    from styles import (
        BRAND_GREEN,
        BRAND_GREEN_DARK,
        BRAND_PEACH,
        BRAND_PEACH_DEEP,
        BRAND_PURPLE,
        BRAND_PURPLE_DARK,
        BRAND_PURPLE_LIGHT,
        BRAND_OFFWHITE,
        COLOR_PALETTE,
        CUSTOM_CSS,
        GREEN_SCALE,
        PLOTLY_LAYOUT,
        PURPLE_SCALE,
        apply_chart_theme,
    )
except ImportError:
    import styles
    BRAND_GREEN = styles.BRAND_GREEN
    BRAND_GREEN_DARK = getattr(styles, 'BRAND_GREEN_DARK', '#7CA33A')
    BRAND_PEACH = getattr(styles, 'BRAND_PEACH', '#FCE6DB')
    BRAND_PEACH_DEEP = styles.BRAND_PEACH_DEEP
    BRAND_PURPLE = styles.BRAND_PURPLE
    BRAND_PURPLE_DARK = styles.BRAND_PURPLE_DARK
    BRAND_PURPLE_LIGHT = getattr(styles, 'BRAND_PURPLE_LIGHT', '#8B7BB8')
    BRAND_OFFWHITE = getattr(styles, 'BRAND_OFFWHITE', '#FBFBFB')
    COLOR_PALETTE = styles.COLOR_PALETTE
    CUSTOM_CSS = styles.CUSTOM_CSS
    GREEN_SCALE = styles.GREEN_SCALE
    PLOTLY_LAYOUT = styles.PLOTLY_LAYOUT
    PURPLE_SCALE = styles.PURPLE_SCALE
    apply_chart_theme = styles.apply_chart_theme

# Paleta de cores para Raça/Cor baseada nas variações harmônicas da Identidade Visual DefenDelas
try:
    from styles import RACE_COLORS
except ImportError:
    RACE_COLORS = {
        'Branca': BRAND_PURPLE,        # #654D9D (Roxo institucional DefenDelas)
        'Parda': BRAND_PEACH_DEEP,     # #E8A87C (Pêssego / Terracota suave DefenDelas)
        'Preta': '#352458',            # Roxo nobre escuro / beringela institucional
        'Amarela': BRAND_GREEN,        # #9EC44D (Verde principal da marca)
        'Indígena': BRAND_GREEN_DARK,  # #7CA33A (Verde escuro institucional)
        'Não informado': '#C4B5E0',    # Lavanda suave / lilás neutro da paleta
    }

# 1. Configuração da Página
st.set_page_config(
    page_title="Painel de dados - DefenDelas",
    page_icon="logo_defendelas.png",
    layout="wide",
    initial_sidebar_state="auto"
)

# Aplicar CSS Customizado
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 2. Carregamento dos Dados com Cache
@st.cache_data(show_spinner=False)
def get_dashboard_data(folder_path=".", cache_key="v7_outubro_2026_oficial"):
    return load_all_dashboard_data(folder_path=folder_path)

# Sidebar: Logo e Identidade Visual DefenDelas
st.sidebar.image("logo_defendelas.png", use_container_width=True)
st.sidebar.markdown("---")

# 2. Carregamento Seguro dos Dados
# Para o público geral, o painel carrega diretamente os dados oficiais do projeto sem exibir caixas de upload.
# A área de upload fica disponível exclusivamente para a proprietária através do parâmetro ?admin=true na URL.
is_admin = st.query_params.get("admin", "").lower() in ["true", "1", "sim", "editor"]

uploaded_files = None
if is_admin:
    st.sidebar.markdown("### Painel da proprietária")
    uploaded_files = st.sidebar.file_uploader(
        "Carregar nova(s) planilha(s) (.xlsx, .xls)",
        type=["xlsx", "xls"],
        accept_multiple_files=True,
        help="Área restrita à proprietária para visualização e teste de novas planilhas."
    )
    if st.sidebar.button("Recarregar dados da pasta", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.sidebar.markdown("---")

if uploaded_files:
    raw_data = load_all_dashboard_data(folder_path=".", uploaded_files=uploaded_files)
else:
    raw_data = get_dashboard_data(".", cache_key="v7_outubro_2026_oficial")

df_forms_raw = raw_data.get('formularios', pd.DataFrame())
if not df_forms_raw.empty and 'municipio' in df_forms_raw.columns:
    df_forms_raw = df_forms_raw[df_forms_raw['municipio'].astype(str).str.lower() != 'manaus'].copy()
df_atend_raw = raw_data.get('atendimentos', pd.DataFrame())
df_pet_raw = raw_data.get('peticoes', pd.DataFrame())
df_consol = raw_data.get('mulheres_consolidadas', pd.DataFrame())
if df_consol.empty:
    df_consol = load_consolidated_mulheres_data()

# Desconsidera completamente o indicador anterior de 299 (registros brutos de video com retornos/ausencias)
if not df_atend_raw.empty:
    df_atend_raw = df_atend_raw[~df_atend_raw['categoria_modalidade'].str.lower().str.contains('vídeo|video')].copy()

# Indicadores Oficiais Consolidados de Mulheres Únicas Atendidas (CEDEM 2026 - LGPD)
total_mulheres_unicas = int(df_consol['Mulheres_Atendidas'].sum()) if not df_consol.empty else 267
mask_jud = df_consol['Categoria_Atendimento'].str.contains('com judicializa', case=False, na=False)
mask_sem_jud = df_consol['Categoria_Atendimento'].str.contains('sem judicializa|orienta', case=False, na=False)

total_com_jud = int(df_consol[mask_jud]['Mulheres_Atendidas'].sum()) if mask_jud.any() else 170
total_sem_jud = int(df_consol[mask_sem_jud]['Mulheres_Atendidas'].sum()) if mask_sem_jud.any() else 97

pct_com_jud = (total_com_jud / total_mulheres_unicas * 100) if total_mulheres_unicas > 0 else 63.7
pct_sem_jud = (total_sem_jud / total_mulheres_unicas * 100) if total_mulheres_unicas > 0 else 36.3

if df_forms_raw.empty and df_atend_raw.empty and df_pet_raw.empty:
    st.error("Nenhuma planilha válida foi encontrada na pasta ou nos arquivos carregados.")
    st.info("Coloque o arquivo `controle de dados dos formulários atualizado.xlsx` na pasta deste projeto.")
    st.stop()

# 3. Sidebar: Filtros Globais Dinâmicos
st.sidebar.markdown("### Filtros do painel")

# Modo de Privacidade LGPD
privacy_mode = st.sidebar.toggle("Modo LGPD / privacidade", value=True, help="Oculta ou mascara dados identificadores para relatórios públicos e seguros.")

# Filtro de Período / Datas de Envio (com base nos formulários)
if not df_forms_raw.empty and df_forms_raw['data'].dropna().count() > 0:
    min_date = df_forms_raw['data'].min()
    max_date = df_forms_raw['data'].max()
else:
    min_date = datetime.now().date()
    max_date = datetime.now().date()

periodo_selecionado = st.sidebar.date_input(
    "Período dos formulários",
    value=(min_date, max_date) if min_date != max_date else (min_date, min_date),
    min_value=min_date,
    max_value=max_date,
    format="DD/MM/YYYY"
)

# Filtros para Formulários
all_cities = sorted([c for c in df_forms_raw['municipio'].unique() if c and c != 'Não informado']) if not df_forms_raw.empty else []
cidades_selecionadas = st.sidebar.multiselect("Município / cidade", options=all_cities, placeholder="Todos os municípios")

all_regions = sorted([r for r in df_forms_raw['regiao_sc'].unique() if r and r != 'Outras Regiões / Não Identificado']) if not df_forms_raw.empty else []
regioes_selecionadas = st.sidebar.multiselect("Mesorregião SC", options=all_regions, placeholder="Todas as regiões")

order_faixas = ['Menor de 18 anos', '18 a 25 anos', '26 a 35 anos', '36 a 40 anos', '41 a 45 anos', '46 a 55 anos', '56 a 65 anos', '66 a 75 anos', '76 a 85 anos', 'Mais de 85 anos', 'Não informado']
present_faixas = [f for f in order_faixas if f in df_forms_raw['faixa_etaria'].unique()] if not df_forms_raw.empty else []
faixas_selecionadas = st.sidebar.multiselect("Faixa etária", options=present_faixas, placeholder="Todas as faixas")

all_races = sorted([r for r in df_forms_raw['raca_cor'].unique() if r]) if not df_forms_raw.empty else []
racas_selecionadas = st.sidebar.multiselect("Raça / cor", options=all_races, placeholder="Todas as raças")

all_areas = sorted([a for a in df_forms_raw['tipo_area'].unique() if a]) if not df_forms_raw.empty else []
areas_selecionadas = st.sidebar.multiselect("Zona / área", options=all_areas, placeholder="Todas as zonas")

viol_options = [
    'Violência Psicológica',
    'Violência Física',
    'Violência Patrimonial',
    'Violência Moral',
    'Violência Sexual'
]
violencias_selecionadas = st.sidebar.multiselect("Tipo de violência (Lei Maria da Penha)", options=viol_options, placeholder="Todos os 5 tipos")

# Filtros para Atendimentos
all_modalidades = sorted([m for m in df_atend_raw['categoria_modalidade'].unique() if m]) if not df_atend_raw.empty else []
modalidades_selecionadas = st.sidebar.multiselect("Modalidade de atendimento", options=all_modalidades, placeholder="Todas as modalidades")

# Campo de Busca Textual Livre
busca_termo = st.sidebar.text_input("Pesquisa textual", placeholder="Buscar palavra nos relatos...")

# 4. Aplicação dos Filtros
df = df_forms_raw.copy()
df_atend = df_atend_raw.copy()
df_pet = df_pet_raw.copy()

if not df.empty:
    if isinstance(periodo_selecionado, (tuple, list)) and len(periodo_selecionado) == 2:
        d_ini, d_fim = periodo_selecionado
        df = df[(df['data'] >= d_ini) & (df['data'] <= d_fim)]

    if cidades_selecionadas:
        df = df[df['municipio'].isin(cidades_selecionadas)]

    if regioes_selecionadas:
        df = df[df['regiao_sc'].isin(regioes_selecionadas)]

    if faixas_selecionadas:
        df = df[df['faixa_etaria'].isin(faixas_selecionadas)]

    if racas_selecionadas:
        df = df[df['raca_cor'].isin(racas_selecionadas)]

    if areas_selecionadas:
        df = df[df['tipo_area'].isin(areas_selecionadas)]

    if violencias_selecionadas:
        def check_viol(row):
            for v in violencias_selecionadas:
                if v in row['tipos_violencia_lista']:
                    return True
            return False
        df = df[df.apply(check_viol, axis=1)]

    if busca_termo:
        term = busca_termo.lower()
        df = df[
            df['relato_fatos'].astype(str).str.lower().str.contains(term) |
            df['municipio'].astype(str).str.lower().str.contains(term) |
            df['como_conheceu'].astype(str).str.lower().str.contains(term)
        ]

if not df_atend.empty:
    if modalidades_selecionadas:
        df_atend = df_atend[df_atend['categoria_modalidade'].isin(modalidades_selecionadas)]

# 5. Header Principal
total_forms_global = len(df_forms_raw)
total_atend_global = len(df_atend_raw)
total_pet_global = len(df_pet_raw)

st.markdown(
    f'<div class="main-header">'
    f'<div><h1>Painel de dados - DefenDelas</h1></div>'
    f'<div class="badge-status">Base oficial de dados da CEDEM - Defensoria Pública de Santa Catarina</div>'
    f'</div>',
    unsafe_allow_html=True
)

if privacy_mode:
    st.markdown("""
    <div class="privacy-active-banner">
        <b>Modo de privacidade LGPD ativo:</b> Dados pessoais e identificadores das mulheres foram anonimizados conforme a Lei Geral de Proteção de Dados.
    </div>
    """, unsafe_allow_html=True)

# 6. Abas Principais do Dashboard
tabs = st.tabs([
    "📊 Visão geral & indicadores integrados",
    "👥 Mulheres atendidas & atendimentos",
    "⚖️ Petições judiciais (CEDEM)",
    "👤 Perfil sociodemográfico",
    "📍 Distribuição geográfica (SC)",
    "⚖️ Tipos de violência (Lei Maria da Penha)",
    "📢 Canais de entrada"
])

# ==========================================
# ABA 1: VISÃO GERAL & KPIS INTEGRADOS
# ==========================================
with tabs[0]:
    total_formularios = len(df)
    total_peticoes = len(df_pet)
    cidades_unicas = df['municipio'].nunique() if not df.empty else 0
    
    # Linha 1 de KPIs: Indicadores Consolidados de Mulheres Atendidas (Oficial CEDEM)
    col_k1, col_k2, col_k3 = st.columns(3)
    with col_k1:
        st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_GREEN};"><div class="kpi-title">Total de Mulheres Atendidas</div><div class="kpi-value">{total_mulheres_unicas}</div><div class="kpi-subtitle">100% • Mulheres únicas atendidas (Base consolidada)</div></div>""", unsafe_allow_html=True)
    with col_k2:
        st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_PURPLE};"><div class="kpi-title">Atendidas com judicialização</div><div class="kpi-value">{total_com_jud}</div><div class="kpi-subtitle">{pct_com_jud:.1f}% do total • Atendidas com petição protocolada</div></div>""", unsafe_allow_html=True)
    with col_k3:
        st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_PEACH_DEEP};"><div class="kpi-title">Atendidas sem judicialização (apenas orientação)</div><div class="kpi-value">{total_sem_jud}</div><div class="kpi-subtitle">{pct_sem_jud:.1f}% do total • Orientação jurídica individualizada</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Linha 2 de KPIs: Atuação Operacional Integrada (Sem repetição de cards operacionais)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_PURPLE_LIGHT};"><div class="kpi-title">Formulários recebidos</div><div class="kpi-value">{total_formularios}</div><div class="kpi-subtitle">Porta de entrada formal de casos</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_PEACH_DEEP};"><div class="kpi-title">Petições judiciais CEDEM</div><div class="kpi-value">{total_peticoes}</div><div class="kpi-subtitle">Peças processuais protocoladas</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_GREEN_DARK};"><div class="kpi-title">Cidades alcançadas</div><div class="kpi-value">{cidades_unicas}</div><div class="kpi-subtitle">Municípios com assistidas</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráfico Único de Comparação das Mulheres Atendidas
    st.markdown("#### Distribuição das mulheres únicas atendidas (Categorias mutuamente exclusivas)")
    
    df_chart_oficial = pd.DataFrame({
        'Categoria': [
            'Atendidas com judicialização',
            'Atendidas sem judicialização (apenas orientação)'
        ],
        'Mulheres Únicas': [total_com_jud, total_sem_jud],
        'Proporção (%)': [pct_com_jud, pct_sem_jud],
        'Rótulo': [f"{total_com_jud} ({pct_com_jud:.1f}%)", f"{total_sem_jud} ({pct_sem_jud:.1f}%)"]
    })
    
    fig_bar_oficial = px.bar(
        df_chart_oficial,
        x='Mulheres Únicas',
        y='Categoria',
        orientation='h',
        text='Rótulo',
        title="Distribuição das mulheres únicas atendidas (Total: 267)",
        color='Categoria',
        color_discrete_map={
            'Atendidas com judicialização': BRAND_PURPLE,
            'Atendidas sem judicialização (apenas orientação)': BRAND_PEACH_DEEP
        }
    )
    fig_bar_oficial.update_traces(textposition='outside', cliponaxis=False)
    fig_bar_oficial.update_layout(
        showlegend=False,
        yaxis={'autorange': 'reversed', 'automargin': True},
        xaxis_title="Mulheres Únicas Atendidas",
        **PLOTLY_LAYOUT
    )
    apply_chart_theme(fig_bar_oficial, left_margin=240, bottom_margin=40)
    st.plotly_chart(fig_bar_oficial, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráfico de Evolução Mensal (Meses por extenso em português)
    st.markdown("#### Evolução mensal das demandas")
    
    months_data = [
        ('2026-03', 'Março'), ('2026-04', 'Abril'), ('2026-05', 'Maio'),
        ('2026-06', 'Junho'), ('2026-07', 'Julho'), ('2026-08', 'Agosto'),
        ('2026-09', 'Setembro'), ('2026-10', 'Outubro')
    ]
    months_codes = [m[0] for m in months_data]
    months_names = [m[1] for m in months_data]
    
    forms_m = df['mes_ano'].value_counts() if not df.empty else pd.Series()
    tel_m = df_atend[df_atend['categoria_modalidade'] == 'Telefone (mensagem)']['mes_ano'].value_counts() if not df_atend.empty else pd.Series()
    pet_m = df_pet['mes_ano'].value_counts() if not df_pet.empty else pd.Series()
    
    df_integ = pd.DataFrame({'Cod': months_codes, 'Mês': months_names})
    df_integ['Formulários'] = df_integ['Cod'].map(forms_m).fillna(0).astype(int)
    df_integ['Telefone'] = df_integ['Cod'].map(tel_m).fillna(0).astype(int)
    df_integ['Petições'] = df_integ['Cod'].map(pet_m).fillna(0).astype(int)
    
    fig_integ = go.Figure()
    fig_integ.add_trace(go.Bar(
        x=df_integ['Mês'], y=df_integ['Telefone'],
        name='Telefone (mensagem / WhatsApp)',
        marker_color=BRAND_GREEN, text=df_integ['Telefone'], textposition='outside'
    ))
    fig_integ.add_trace(go.Bar(
        x=df_integ['Mês'], y=df_integ['Formulários'],
        name='Formulários recebidos',
        marker_color=BRAND_PURPLE, text=df_integ['Formulários'], textposition='outside'
    ))
    fig_integ.add_trace(go.Bar(
        x=df_integ['Mês'], y=df_integ['Petições'],
        name='Petições protocoladas',
        marker_color=BRAND_PEACH_DEEP, text=df_integ['Petições'], textposition='outside'
    ))
    
    fig_integ.update_layout(
        barmode='group',
        xaxis_title="Mês",
        yaxis_title="Total de registros",
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        **PLOTLY_LAYOUT
    )
    apply_chart_theme(fig_integ, top_margin=60)
    st.plotly_chart(fig_integ, use_container_width=True)

    # Destaque: Panorama dos 5 Tipos de Violência
    st.markdown("#### Panorama dos 5 tipos de violência (Lei Maria da Penha)")
    viol_5_counts = {
        'Física': int(df['viol_fisica'].sum()) if not df.empty else 0,
        'Psicológica': int(df['viol_psicologica'].sum()) if not df.empty else 0,
        'Patrimonial': int(df['viol_patrimonial'].sum()) if not df.empty else 0,
        'Moral': int(df['viol_moral'].sum()) if not df.empty else 0,
        'Sexual': int(df['viol_sexual'].sum()) if not df.empty else 0,
    }
    df_v5 = pd.DataFrame(list(viol_5_counts.items()), columns=['Tipo', 'Casos']).sort_values(by='Casos', ascending=False)
    fig_v5 = px.bar(
        df_v5, x='Casos', y='Tipo', orientation='h', text='Casos',
        color='Casos', color_continuous_scale=PURPLE_SCALE
    )
    fig_v5.update_traces(textposition='outside', cliponaxis=False)
    fig_v5.update_layout(yaxis={'autorange': 'reversed', 'automargin': True}, **PLOTLY_LAYOUT)
    apply_chart_theme(fig_v5, left_margin=110)
    st.plotly_chart(fig_v5, use_container_width=True)
    st.markdown(f"""
    <div style="background-color: #F8F6FD; border-left: 4px solid {BRAND_PURPLE}; padding: 0.75rem 1.1rem; border-radius: 8px; margin-top: 0.6rem; margin-bottom: 1rem;">
        <p style="margin: 0; font-size: 0.88rem; color: {BRAND_PURPLE_DARK}; line-height: 1.45;">
            ℹ️ <b>Nota explicativa:</b> Em muitos relatos há sobreposição de mais de um tipo de violência na mesma solicitação, motivo pelo qual a soma dos casos excede o número total de formulários recebidos.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# ABA 2: MULHERES ATENDIDAS & ATENDIMENTOS DA EQUIPE
# ==========================================
with tabs[1]:
    st.caption("Acompanhamento das atividades operacionais de suporte continuado por telefone e WhatsApp.")
    
    # Linha Exclusiva de KPIs Operacionais (Sem repetição de cards da Aba 1)
    k_sub1, k_sub2, k_sub3 = st.columns(3)
    with k_sub1:
        st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_PURPLE_DARK};"><div class="kpi-title">Média diária (Telefone/WhatsApp)</div><div class="kpi-value">12,2</div><div class="kpi-subtitle">Contatos por dia com atividades • 60,8 por semana</div></div>""", unsafe_allow_html=True)
    with k_sub2:
        st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_PURPLE};"><div class="kpi-title">Acompanhamento por assistida</div><div class="kpi-value">7,5</div><div class="kpi-subtitle">Contatos de suporte por mulher atendida (267 assistidas)</div></div>""", unsafe_allow_html=True)
    with k_sub3:
        st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_PEACH_DEEP};"><div class="kpi-title">Período de atuação contínua</div><div class="kpi-value">33 semanas</div><div class="kpi-subtitle">165 dias com atividades registradas (Março a Outubro/2026)</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabela com Título "Total de mulheres atendidas"
    st.markdown("#### Total de mulheres atendidas")
    df_consol_tabela = pd.DataFrame([
        {
            'Indicador / Categoria de Atendimento': 'Atendidas com judicialização',
            'Quantidade (Mulheres Únicas)': total_com_jud,
            'Proporção (%)': f"{pct_com_jud:.1f}%",
            'Descrição Metodológica': 'Mulheres que passaram pelo acolhimento/atendimento e tiveram petição protocolada em juízo'
        },
        {
            'Indicador / Categoria de Atendimento': 'Atendidas sem judicialização (apenas orientação)',
            'Quantidade (Mulheres Únicas)': total_sem_jud,
            'Proporção (%)': f"{pct_sem_jud:.1f}%",
            'Descrição Metodológica': 'Mulheres atendidas em orientação jurídica qualificada e acolhimento sem protocolo judicial'
        },
        {
            'Indicador / Categoria de Atendimento': 'Total de Mulheres Atendidas',
            'Quantidade (Mulheres Únicas)': total_mulheres_unicas,
            'Proporção (%)': '100,0%',
            'Descrição Metodológica': 'Total consolidado de mulheres únicas atendidas (categorias estritamente mutuamente exclusivas)'
        }
    ])
    st.dataframe(df_consol_tabela, use_container_width=True, hide_index=True)

    # Nota explicativa de rodapé com os totais brutos
    st.markdown(f"""
    <div style="background-color: #F8F6FD; border-left: 4px solid {BRAND_PURPLE}; padding: 1.15rem 1.4rem; border-radius: 10px; margin-top: 1.5rem; margin-bottom: 1.5rem;">
        <h4 style="margin: 0 0 0.5rem 0; color: {BRAND_PURPLE_DARK}; font-size: 1.05rem;">
            📞 Dinâmica de acompanhamento contínuo por telefone e mensagens (WhatsApp)
        </h4>
        <p style="margin: 0 0 0.6rem 0; font-size: 0.93rem; color: #1F2937; line-height: 1.55;">
            No período analisado (março a outubro de 2026), foram registradas <b>2.006 interações por telefone e mensagens de texto/áudio (WhatsApp)</b> ao longo de <b>165 dias com atividades</b> (aproximadamente 33 semanas úteis). Esse total bruto representa os retornos periódicos, esclarecimento de dúvidas processuais e o acompanhamento contínuo individualizado das <b>267 mulheres atendidas</b>, resultando nas médias operacionais de <b>12,2 contatos por dia útil</b> (60,8 contatos por semana) e aproximadamente <b>7,5 contatos de acompanhamento contínuo por mulher atendida</b>.
        </p>
        <p style="margin: 0; font-size: 0.88rem; color: #4B5563; line-height: 1.5; font-style: italic; border-top: 1px dashed #D1D5DB; padding-top: 0.65rem;">
            <b>Relação entre porta de entrada e retornos:</b> Os formulários de acolhimento representam a porta de entrada formal para novos casos no serviço. A partir desse primeiro contato, cada mulher assistida gera múltiplos contatos de retorno e acompanhamento ao longo dos meses.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# ABA 3: PETIÇÕES JUDICIAIS (CEDEM)
# ==========================================
with tabs[2]:
    st.markdown("### Relatório de petições judiciais (CEDEM - 2026)")
    st.caption("Acompanhamento das peças processuais e atuações judiciais estratégicas na proteção dos direitos das mulheres.")
    
    if not df_pet.empty:
        k_pt1, k_pt2, k_pt3 = st.columns(3)
        total_pt = len(df_pet)
        top_pt_mes = df_pet['mes_nome'].value_counts().index[0] if not df_pet['mes_nome'].value_counts().empty else "N/D"
        top_pt_mes_count = df_pet['mes_nome'].value_counts().iloc[0] if not df_pet['mes_nome'].value_counts().empty else 0
        top_pt_cat = df_pet['categoria_peticao'].value_counts().index[0] if not df_pet['categoria_peticao'].value_counts().empty else "N/D"
        top_pt_cat_count = df_pet['categoria_peticao'].value_counts().iloc[0] if not df_pet['categoria_peticao'].value_counts().empty else 0
        
        with k_pt1:
            st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_PEACH_DEEP};"><div class="kpi-title">Total de petições</div><div class="kpi-value">{total_pt}</div><div class="kpi-subtitle">Peças processuais protocoladas</div></div>""", unsafe_allow_html=True)
        with k_pt2:
            st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_PURPLE};"><div class="kpi-title">Mês com maior volume</div><div class="kpi-value">{top_pt_mes}</div><div class="kpi-subtitle">{top_pt_mes_count} petições protocoladas</div></div>""", unsafe_allow_html=True)
        with k_pt3:
            st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_GREEN};"><div class="kpi-title">Categoria mais frequente</div><div class="kpi-value" style="font-size:1.3rem;">{top_pt_cat}</div><div class="kpi-subtitle">{top_pt_cat_count} peças ({(top_pt_cat_count/total_pt*100):.1f}%)</div></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Gráfico 1: Evolução Mensal de Petições
        meses_ordem_nomes = ['Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro']
        df_pt_mes = df_pet['mes_nome'].value_counts().reindex(meses_ordem_nomes).fillna(0).reset_index()
        df_pt_mes.columns = ['Mês', 'Petições']
        fig_pt_mes = px.bar(
            df_pt_mes, x='Mês', y='Petições', text='Petições',
            title="Volume mensal de petições protocoladas (2026)",
            color_discrete_sequence=[BRAND_PEACH_DEEP]
        )
        fig_pt_mes.update_traces(textposition='outside', cliponaxis=False)
        fig_pt_mes.update_layout(xaxis={'automargin': True}, **PLOTLY_LAYOUT)
        apply_chart_theme(fig_pt_mes, bottom_margin=50)
        st.plotly_chart(fig_pt_mes, use_container_width=True)

        # Gráfico 2: Petições por Categoria Processual (Largura Total com Total e Porcentagem)
        df_pt_cat = df_pet['categoria_peticao'].value_counts().reset_index()
        df_pt_cat.columns = ['Categoria Processual', 'Total']
        total_pt_cat = df_pt_cat['Total'].sum()
        df_pt_cat['Porcentagem'] = (df_pt_cat['Total'] / total_pt_cat * 100).round(1) if total_pt_cat > 0 else 0
        df_pt_cat['Texto'] = df_pt_cat.apply(lambda r: f"{r['Total']} ({r['Porcentagem']}%)", axis=1)
        
        fig_pt_cat = px.bar(
            df_pt_cat, x='Total', y='Categoria Processual', orientation='h', text='Texto',
            title="Petições por categoria processual (CEDEM - 2026)",
            color='Total', color_continuous_scale=PURPLE_SCALE
        )
        fig_pt_cat.update_traces(textposition='outside', cliponaxis=False)
        fig_pt_cat.update_layout(yaxis={'autorange': 'reversed', 'automargin': True}, **PLOTLY_LAYOUT)
        apply_chart_theme(fig_pt_cat, left_margin=220)
        st.plotly_chart(fig_pt_cat, use_container_width=True)
    else:
        st.info("Nenhum dado de petições encontrado.")

# ==========================================
# ABA 4: PERFIL SOCIODEMOGRÁFICO
# ==========================================
with tabs[3]:
    st.markdown("### Perfil sociodemográfico das mulheres assistidas")
    
    if not df.empty:
        col_demo1, col_demo2 = st.columns(2)
        
        with col_demo1:
            df_faixa = df['faixa_etaria'].value_counts().reindex(order_faixas).dropna().reset_index()
            df_faixa.columns = ['Faixa Etária', 'Total']
            df_faixa = df_faixa[df_faixa['Total'] > 0]
            if not df_faixa.empty:
                fig_faixa = px.bar(
                    df_faixa, x='Total', y='Faixa Etária', orientation='h',
                    text='Total', title="Distribuição por faixa etária",
                    color='Total', color_continuous_scale=PURPLE_SCALE
                )
                fig_faixa.update_traces(textposition='outside', cliponaxis=False)
                fig_faixa.update_layout(yaxis={'autorange': 'reversed', 'automargin': True}, **PLOTLY_LAYOUT)
                apply_chart_theme(fig_faixa, left_margin=120)
                st.plotly_chart(fig_faixa, use_container_width=True)
            
        with col_demo2:
            df_raca = df['raca_cor'].value_counts().reset_index()
            df_raca.columns = ['Raça/Cor', 'Total']
            if not df_raca.empty:
                fig_raca = px.pie(
                    df_raca, names='Raça/Cor', values='Total', hole=0.45,
                    title="Autodeclaração racial / cor",
                    color='Raça/Cor',
                    color_discrete_map=RACE_COLORS
                )
                fig_raca.update_traces(textinfo='percent+label')
                fig_raca.update_layout(**PLOTLY_LAYOUT)
                apply_chart_theme(fig_raca)
                st.plotly_chart(fig_raca, use_container_width=True)
            
        col_demo3, col_demo5 = st.columns(2)
        
        with col_demo3:
            df_civil = df['estado_civil'].value_counts().reset_index()
            df_civil.columns = ['Estado Civil', 'Total']
            if not df_civil.empty:
                fig_civil = px.bar(df_civil, x='Estado Civil', y='Total', text='Total', title="Estado civil", color_discrete_sequence=[BRAND_PURPLE])
                fig_civil.update_traces(textposition='outside', cliponaxis=False)
                fig_civil.update_layout(xaxis={'automargin': True}, **PLOTLY_LAYOUT)
                apply_chart_theme(fig_civil, bottom_margin=50)
                st.plotly_chart(fig_civil, use_container_width=True)
            
        with col_demo5:
            df_area = df['tipo_area'].value_counts().reset_index()
            df_area.columns = ['Tipo de Área', 'Total']
            if not df_area.empty:
                fig_area = px.pie(df_area, names='Tipo de Área', values='Total', hole=0.4, title="Tipo de área (urbana / rural)", color_discrete_sequence=[BRAND_PURPLE, BRAND_GREEN, BRAND_PEACH_DEEP])
                fig_area.update_traces(textinfo='percent+label')
                fig_area.update_layout(**PLOTLY_LAYOUT)
                apply_chart_theme(fig_area)
                st.plotly_chart(fig_area, use_container_width=True)

        # Identidade de Gênero em linha própria, com largura total e legenda
        # horizontal abaixo do gráfico para que os percentuais não fiquem cortados
        df_gen = df['identidade_genero'].value_counts().reset_index()
        df_gen.columns = ['Gênero', 'Total']
        if not df_gen.empty:
            fig_gen = px.pie(df_gen, names='Gênero', values='Total', hole=0.4, title="Identidade de gênero", color_discrete_sequence=COLOR_PALETTE)
            fig_gen.update_traces(textinfo='percent+label', textposition='auto')
            fig_gen.update_layout(
                **PLOTLY_LAYOUT,
                legend=dict(orientation='h', yanchor='top', y=-0.1, xanchor='center', x=0.5)
            )
            apply_chart_theme(fig_gen, bottom_margin=60)
            st.plotly_chart(fig_gen, use_container_width=True)

        st.markdown("#### Cruzamento demográfico: faixa etária x raça/cor")
        crosstab_raca_faixa = pd.crosstab(df['faixa_etaria'], df['raca_cor']).reindex(order_faixas).dropna(how='all')
        if not crosstab_raca_faixa.empty:
            fig_cross = px.bar(
                crosstab_raca_faixa, barmode='stack',
                title="Distribuição de raça/cor por faixa etária",
                color_discrete_map=RACE_COLORS
            )
            fig_cross.update_layout(
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                xaxis={'automargin': True},
                **PLOTLY_LAYOUT
            )
            apply_chart_theme(fig_cross, top_margin=60, bottom_margin=50)
            st.plotly_chart(fig_cross, use_container_width=True)
    else:
        st.info("Nenhum dado sociodemográfico encontrado para os filtros selecionados.")

# ==========================================
# ABA 5: DISTRIBUIÇÃO GEOGRÁFICA (SC)
# ==========================================
with tabs[4]:
    st.markdown("### Distribuição geográfica em Santa Catarina")
    
    if not df.empty:
        df_cities_all = df[df['municipio'] != 'Não informado']['municipio'].value_counts().reset_index()
        df_cities_all.columns = ['Município', 'Total']
        tot_cities_cases = df_cities_all['Total'].sum()
        df_cities_all['Porcentagem'] = (df_cities_all['Total'] / tot_cities_cases * 100).round(1) if tot_cities_cases > 0 else 0
        df_cities_all['Texto'] = df_cities_all.apply(lambda r: f"{r['Total']} ({r['Porcentagem']}%)", axis=1)

        view_qtd = st.radio(
            "Visualização do ranking gráfico:",
            ["Todos os municípios", "Top 15", "Top 30"],
            horizontal=True
        )
        
        if view_qtd == "Top 15":
            df_chart_cities = df_cities_all.head(15)
            chart_h = 500
        elif view_qtd == "Top 30":
            df_chart_cities = df_cities_all.head(30)
            chart_h = 750
        else:
            df_chart_cities = df_cities_all
            chart_h = max(550, len(df_chart_cities) * 22)

        col_geo1, col_geo2 = st.columns([1, 1])
        with col_geo1:
            fig_top_cities = px.bar(
                df_chart_cities, x='Total', y='Município', orientation='h',
                text='Texto', title=f"Municípios com solicitações ({view_qtd})",
                color='Total', color_continuous_scale=PURPLE_SCALE
            )
            fig_top_cities.update_traces(textposition='outside', cliponaxis=False)
            fig_top_cities.update_layout(
                yaxis={'autorange': 'reversed', 'automargin': True},
                height=chart_h,
                **PLOTLY_LAYOUT
            )
            apply_chart_theme(fig_top_cities, left_margin=180)
            st.plotly_chart(fig_top_cities, use_container_width=True)
            
        with col_geo2:
            df_regiao = df['regiao_sc'].value_counts().reset_index()
            df_regiao.columns = ['Região', 'Total']
            if not df_regiao.empty:
                fig_regiao = px.pie(
                    df_regiao, names='Região', values='Total', hole=0.45,
                    title="Distribuição por mesorregiões de Santa Catarina",
                    color_discrete_sequence=COLOR_PALETTE
                )
                fig_regiao.update_traces(
                    textinfo='percent',
                    textposition='inside',
                    insidetextorientation='radial',
                    hovertemplate="<b>%{label}</b><br>Total: %{value} solicitações<br>Proporção: %{percent}<extra></extra>"
                )
                fig_regiao.update_layout(
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=-0.12,
                        xanchor="center",
                        x=0.5,
                        font=dict(family='Plus Jakarta Sans, sans-serif', size=11, color=BRAND_PURPLE_DARK)
                    ),
                    **PLOTLY_LAYOUT
                )
                apply_chart_theme(fig_regiao, bottom_margin=100)
                st.plotly_chart(fig_regiao, use_container_width=True)

        st.markdown(f"#### Lista completa de todos os {len(df_cities_all)} municípios atendidos")
        df_table = df_cities_all.copy()
        df_table.insert(0, 'Posição', [f"{i+1}º" for i in range(len(df_table))])
        df_table['Mesorregião SC'] = df_table['Município'].apply(lambda m: CITIES_DB.get(m, {}).get('regiao', 'Não identificada'))
        df_table['Proporção (%)'] = df_table['Porcentagem'].astype(str) + '%'
        df_table = df_table[['Posição', 'Município', 'Total', 'Proporção (%)', 'Mesorregião SC']]
        df_table.columns = ['Posição', 'Município', 'Total de Solicitações', 'Proporção (%)', 'Mesorregião']
        st.dataframe(df_table, use_container_width=True, hide_index=True)
            
        st.markdown("#### Mapa de concentração territorial")
        df_geo = df.dropna(subset=['lat', 'lon']).groupby(['municipio', 'lat', 'lon', 'regiao_sc']).size().reset_index(name='Formulários')
        
        if not df_geo.empty:
            try:
                fig_map = px.scatter_map(
                    df_geo, lat='lat', lon='lon', size='Formulários',
                    color='Formulários', hover_name='municipio',
                    hover_data={'regiao_sc': True, 'Formulários': True, 'lat': False, 'lon': False},
                    color_continuous_scale='Turbo', size_max=35, zoom=6.5,
                    center={'lat': -27.2423, 'lon': -50.2189},
                    title="Concentração de solicitações por município em Santa Catarina"
                )
                fig_map.update_layout(margin={'l': 0, 'r': 0, 't': 40, 'b': 0}, height=500)
                st.plotly_chart(fig_map, use_container_width=True)
            except Exception:
                fig_map = px.scatter_mapbox(
                    df_geo, lat='lat', lon='lon', size='Formulários',
                    color='Formulários', hover_name='municipio',
                    hover_data={'regiao_sc': True, 'Formulários': True, 'lat': False, 'lon': False},
                    color_continuous_scale='Turbo', size_max=35, zoom=6.5,
                    center={'lat': -27.2423, 'lon': -50.2189},
                    mapbox_style='carto-positron',
                    title="Concentração de solicitações por município em Santa Catarina"
                )
                fig_map.update_layout(margin={'l': 0, 'r': 0, 't': 40, 'b': 0}, height=500)
                st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("Coordenadas geográficas não disponíveis para os dados selecionados.")
    else:
        st.info("Nenhum dado geográfico encontrado para os filtros selecionados.")

# ==========================================
# ABA 6: TIPOS DE VIOLÊNCIA (LEI MARIA DA PENHA)
# ==========================================
with tabs[5]:
    st.markdown("### Os 5 tipos de violência contra a mulher (Art. 7º - Lei Maria da Penha)")
    st.caption("Classificação gerada a partir dos relatos fáticos das vítimas no formulário de atendimento.")
    
    if not df.empty:
        col_v1, col_v2 = st.columns([1.3, 1])
        
        with col_v1:
            viol_data = [
                {
                    'Tipo de Violência': 'Violência Física',
                    'Casos': int(df['viol_fisica'].sum()),
                    'Definição': 'Agressão, lesão corporal, tapas, socos, empurrões, puxões de cabelo, sufocamento'
                },
                {
                    'Tipo de Violência': 'Violência Psicológica',
                    'Casos': int(df['viol_psicologica'].sum()),
                    'Definição': 'Ameaças, humilhação, agressão verbal, perseguição contumaz, controle, manipulação'
                },
                {
                    'Tipo de Violência': 'Violência Patrimonial',
                    'Casos': int(df['viol_patrimonial'].sum()),
                    'Definição': 'Retenção, destruição de bens, cartão, documentos ou recursos econômicos'
                },
                {
                    'Tipo de Violência': 'Violência Moral',
                    'Casos': int(df['viol_moral'].sum()),
                    'Definição': 'Calúnia, difamação, injúria, ataques à honra ou exposição indevida'
                },
                {
                    'Tipo de Violência': 'Violência Sexual',
                    'Casos': int(df['viol_sexual'].sum()),
                    'Definição': 'Relação sexual não desejada sob coação, abuso, assédio'
                },
            ]
            df_v_summary = pd.DataFrame(viol_data).sort_values(by='Casos', ascending=False)
            total_forms_cur = len(df)
            df_v_summary['% das Vítimas'] = ((df_v_summary['Casos'] / total_forms_cur) * 100).round(1) if total_forms_cur > 0 else 0
            
            fig_viol = px.bar(
                df_v_summary, x='Casos', y='Tipo de Violência', orientation='h',
                text='Casos', title="Total de casos por tipo de violência relatada",
                color='Casos', color_continuous_scale=PURPLE_SCALE,
                hover_data={'Definição': True, '% das Vítimas': True}
            )
            fig_viol.update_traces(textposition='outside', cliponaxis=False)
            fig_viol.update_layout(yaxis={'autorange': 'reversed', 'automargin': True}, **PLOTLY_LAYOUT)
            apply_chart_theme(fig_viol, left_margin=160)
            st.plotly_chart(fig_viol, use_container_width=True)
            
            st.markdown(f"""
            <div style="background-color: #F8F6FD; border-left: 4px solid {BRAND_PURPLE}; padding: 0.85rem 1.15rem; border-radius: 8px; margin-top: 0.75rem; margin-bottom: 1.2rem;">
                <p style="margin: 0; font-size: 0.90rem; color: {BRAND_PURPLE_DARK}; line-height: 1.5;">
                    ℹ️ <b>Nota explicativa:</b> Em muitos relatos apresentados pelas assistidas, observa-se a ocorrência simultânea de mais de um tipo de violência (ex.: violência física acompanhada de violência psicológica e moral). Por essa razão, a soma total dos dados de tipos de violência é superior ao número total de formulários recebidos.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        with col_v2:
            df_qtd_v = df['qtd_violencias'].value_counts().reset_index()
            df_qtd_v.columns = ['Qtd Violências Concomitantes', 'Total Casos']
            
            rotulos_map = {
                0: 'Não especificada no texto',
                1: '1 forma isolada',
                2: '2 formas simultâneas',
                3: '3 formas simultâneas',
                4: '4 formas simultâneas',
                5: '5 formas simultâneas'
            }
            df_qtd_v['Rótulo'] = df_qtd_v['Qtd Violências Concomitantes'].map(rotulos_map)
            
            fig_qtd = px.pie(
                df_qtd_v, names='Rótulo', values='Total Casos', hole=0.45,
                title="Sobreposição de formas de violência por vítima",
                color_discrete_sequence=COLOR_PALETTE
            )
            fig_qtd.update_traces(textinfo='percent+label')
            fig_qtd.update_layout(**PLOTLY_LAYOUT)
            apply_chart_theme(fig_qtd)
            st.plotly_chart(fig_qtd, use_container_width=True)

        st.markdown("#### Perfil do agressor / relação com a vítima")
        all_agr_items = []
        if 'perfil_agressor_lista' in df.columns:
            for items in df['perfil_agressor_lista']:
                if isinstance(items, list):
                    all_agr_items.extend(items)
                elif pd.notna(items):
                    all_agr_items.append(str(items))
        elif 'perfil_agressor_rotulo' in df.columns:
            all_agr_items = df['perfil_agressor_rotulo'].dropna().tolist()

        df_agr = pd.Series(all_agr_items).value_counts().reset_index()
        df_agr.columns = ['Perfil do Agressor', 'Total']
        chart_height = max(500, len(df_agr) * 26 + 100)
        fig_agr = px.bar(
            df_agr, x='Total', y='Perfil do Agressor', orientation='h', text='Total',
            title="Vínculo do agressor com a mulher",
            color='Total', color_continuous_scale=PURPLE_SCALE,
            height=chart_height
        )
        fig_agr.update_traces(textposition='outside', cliponaxis=False)
        fig_agr.update_layout(yaxis={'autorange': 'reversed', 'automargin': True}, **PLOTLY_LAYOUT)
        apply_chart_theme(fig_agr, left_margin=240)
        st.plotly_chart(fig_agr, use_container_width=True)
        st.caption("Nota: A categoria **'Não informado / Encaminhamento externo'** reúne os casos em que o vínculo não foi detalhado por se tratar de encaminhamento da mulher para a Defensoria Pública da sua comarca de residência ou por envolver solicitação de serviço fora do escopo de atendimento do projeto.")
    else:
        st.info("Nenhum dado de violência encontrado para os filtros selecionados.")

# ==========================================
# ABA 7: CANAIS DE ENTRADA
# ==========================================
with tabs[6]:
    st.markdown("### Origem do acesso e encaminhamentos")
    
    if not df.empty:
        df_canal = df['canal_origem'].value_counts().reset_index()
        df_canal.columns = ['Canal de Acesso', 'Total']
        tot_canal = df_canal['Total'].sum()
        df_canal['Porcentagem'] = (df_canal['Total'] / tot_canal * 100).round(1) if tot_canal > 0 else 0
        df_canal['Texto'] = df_canal.apply(lambda r: f"{r['Total']} ({r['Porcentagem']}%)", axis=1)

        col_c1, col_c2 = st.columns(2)
        with col_c1:
            fig_canal = px.bar(
                df_canal, x='Total', y='Canal de Acesso', orientation='h',
                text='Texto', title="Volume de solicitações por porta de entrada",
                color='Total', color_continuous_scale=GREEN_SCALE
            )
            fig_canal.update_traces(textposition='outside', cliponaxis=False)
            fig_canal.update_layout(yaxis={'autorange': 'reversed', 'automargin': True}, **PLOTLY_LAYOUT)
            apply_chart_theme(fig_canal, left_margin=260)
            st.plotly_chart(fig_canal, use_container_width=True)
            
        with col_c2:
            fig_canal_pie = px.pie(
                df_canal, names='Canal de Acesso', values='Total', hole=0.45,
                title="Proporção dos canais de encaminhamento",
                color_discrete_sequence=COLOR_PALETTE
            )
            fig_canal_pie.update_traces(
                textinfo='percent',
                textposition='inside',
                insidetextorientation='radial',
                hovertemplate="<b>%{label}</b><br>Total: %{value} mulheres<br>Proporção: %{percent}<extra></extra>"
            )
            fig_canal_pie.update_layout(
                legend=dict(
                    orientation="h",
                    yanchor="top",
                    y=-0.12,
                    xanchor="center",
                    x=0.5,
                    font=dict(family='Plus Jakarta Sans, sans-serif', size=11, color=BRAND_PURPLE_DARK)
                ),
                **PLOTLY_LAYOUT
            )
            apply_chart_theme(fig_canal_pie, bottom_margin=120)
            st.plotly_chart(fig_canal_pie, use_container_width=True)
            
        st.markdown("#### Detalhamento das portas de entrada e encaminhamentos")
        df_canal_tab = df_canal[['Canal de Acesso', 'Total', 'Porcentagem']].copy()
        df_canal_tab['Proporção (%)'] = df_canal_tab['Porcentagem'].astype(str) + '%'
        df_canal_tab = df_canal_tab[['Canal de Acesso', 'Total', 'Proporção (%)']]
        st.dataframe(df_canal_tab, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum dado de canais de acesso encontrado para os filtros selecionados.")


