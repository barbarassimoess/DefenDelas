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

from data_loader import load_all_dashboard_data, CITIES_DB

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
df_atend_raw = raw_data.get('atendimentos', pd.DataFrame())
df_pet_raw = raw_data.get('peticoes', pd.DataFrame())

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

st.markdown(f"""
<div class="main-header">
    <div>
        <h1>Painel de dados - DefenDelas</h1>
        <p>Monitoramento de formulários de acolhimento, atendimentos e petições judiciais (CEDEM)</p>
    </div>
    <div class="badge-status">
        Base atualizada (até Outubro/2026) • {total_forms_global} formulários • {total_atend_global} atendimentos • {total_pet_global} petições
    </div>
</div>
""", unsafe_allow_html=True)

if privacy_mode:
    st.markdown("""
    <div class="privacy-active-banner">
        <b>Modo de privacidade LGPD ativo:</b> Dados pessoais e identificadores das mulheres foram anonimizados conforme a Lei Geral de Proteção de Dados.
    </div>
    """, unsafe_allow_html=True)

# 6. Abas Principais do Dashboard
tabs = st.tabs([
    "📊 Visão geral & indicadores integrados",
    "📞 Atendimentos (telefone & vídeo)",
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
    total_telefone = int((df_atend['categoria_modalidade'] == 'Telefone (mensagem)').sum()) if not df_atend.empty else 0
    total_video = int((df_atend['categoria_modalidade'] == 'Atendimento por vídeo').sum()) if not df_atend.empty else 0
    total_peticoes = len(df_pet)
    cidades_unicas = df['municipio'].nunique() if not df.empty else 0
    
    # Linha 1 de KPIs Principais Integrados
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_PURPLE};"><div class="kpi-title">Formulários recebidos</div><div class="kpi-value">{total_formularios}</div><div class="kpi-subtitle">Solicitações registradas até Out/2026</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_PURPLE_DARK};"><div class="kpi-title">Telefone (mensagem)</div><div class="kpi-value">{total_telefone}</div><div class="kpi-subtitle">Contatos contínuos e WhatsApp</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_GREEN};"><div class="kpi-title">Atendimentos por vídeo</div><div class="kpi-value">{total_video}</div><div class="kpi-subtitle">Sessões com comparecimento</div></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_PEACH_DEEP};"><div class="kpi-title">Petições judiciais CEDEM</div><div class="kpi-value">{total_peticoes}</div><div class="kpi-subtitle">Peças processuais protocoladas</div></div>""", unsafe_allow_html=True)
    with col5:
        st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_GREEN_DARK};"><div class="kpi-title">Cidades alcançadas</div><div class="kpi-value">{cidades_unicas}</div><div class="kpi-subtitle">Municípios de SC atendidos</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Gráfico de Evolução Mensal Integrada (Formulários x Atendimentos x Petições)
    st.markdown("#### Evolução mensal integrada das demandas (2026)")
    
    months_series = ['2026-03', '2026-04', '2026-05', '2026-06', '2026-07', '2026-08', '2026-09', '2026-10']
    
    forms_m = df['mes_ano'].value_counts() if not df.empty else pd.Series()
    tel_m = df_atend[df_atend['categoria_modalidade'] == 'Telefone (mensagem)']['mes_ano'].value_counts() if not df_atend.empty else pd.Series()
    vid_m = df_atend[df_atend['categoria_modalidade'] == 'Atendimento por vídeo']['mes_ano'].value_counts() if not df_atend.empty else pd.Series()
    pet_m = df_pet['mes_ano'].value_counts() if not df_pet.empty else pd.Series()
    
    df_integ = pd.DataFrame({'Mês': months_series})
    df_integ['Formulários'] = df_integ['Mês'].map(forms_m).fillna(0).astype(int)
    df_integ['Telefone'] = df_integ['Mês'].map(tel_m).fillna(0).astype(int)
    df_integ['Vídeo'] = df_integ['Mês'].map(vid_m).fillna(0).astype(int)
    df_integ['Petições'] = df_integ['Mês'].map(pet_m).fillna(0).astype(int)
    
    fig_integ = go.Figure()
    fig_integ.add_trace(go.Bar(
        x=df_integ['Mês'], y=df_integ['Telefone'],
        name='Telefone (mensagem)',
        marker_color=BRAND_PURPLE_DARK, text=df_integ['Telefone'], textposition='outside'
    ))
    fig_integ.add_trace(go.Bar(
        x=df_integ['Mês'], y=df_integ['Vídeo'],
        name='Atendimentos por vídeo',
        marker_color=BRAND_GREEN, text=df_integ['Vídeo'], textposition='outside'
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
        title="Volume comparativo mensal de atuação",
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
# ABA 2: ATENDIMENTOS DA EQUIPE
# ==========================================
with tabs[1]:
    st.markdown("### Monitoramento de atendimentos realizados (Março a Outubro/2026)")
    st.caption("Acompanhamento contínuo das atividades de atendimento individualizado por telefone (mensagem) e por vídeo.")
    
    if not df_atend.empty:
        total_telefone = int((df_atend['categoria_modalidade'] == 'Telefone (mensagem)').sum())
        total_video = int((df_atend['categoria_modalidade'] == 'Atendimento por vídeo').sum())
        total_geral_efetivo = len(df_atend)
        
        dias_uteis = df_atend['data_apenas'].dropna().nunique()
        semanas_uteis = max(1, round(dias_uteis / 5, 1))
        
        media_semanal_tel = round(total_telefone / semanas_uteis, 1) if semanas_uteis else 0
        media_diaria_tel = round(total_telefone / dias_uteis, 1) if dias_uteis else 0
        
        dias_com_video = df_atend[df_atend['categoria_modalidade'] == 'Atendimento por vídeo']['data_apenas'].dropna().nunique()
        media_semanal_vid = round(total_video / semanas_uteis, 1) if semanas_uteis else 0
        media_diaria_vid = round(total_video / dias_com_video, 1) if dias_com_video else 0
        
        media_semanal_total = round(total_geral_efetivo / semanas_uteis, 1) if semanas_uteis else 0
        media_diaria_total = round(total_geral_efetivo / dias_uteis, 1) if dias_uteis else 0
        
        # Linha 1 de KPIs (Dados Consolidados até Outubro/2026)
        k_at1, k_at2, k_at3 = st.columns(3)
        with k_at1:
            st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_PURPLE_DARK};"><div class="kpi-title">Telefone (mensagem / WhatsApp)</div><div class="kpi-value">{total_telefone}</div><div class="kpi-subtitle">{(total_telefone/total_geral_efetivo*100):.1f}% do total • Atendimentos continuados</div></div>""", unsafe_allow_html=True)
        with k_at2:
            st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_GREEN};"><div class="kpi-title">Atendimentos por vídeo</div><div class="kpi-value">{total_video}</div><div class="kpi-subtitle">{(total_video/total_geral_efetivo*100):.1f}% do total • Sessões com comparecimento</div></div>""", unsafe_allow_html=True)
        with k_at3:
            st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_PEACH_DEEP};"><div class="kpi-title">Total geral de atendimentos</div><div class="kpi-value">{total_geral_efetivo}</div><div class="kpi-subtitle">{dias_uteis} dias com atividades registradas</div></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Linha 2 de Médias Semanais e Diárias
        k_at4, k_at5, k_at6 = st.columns(3)
        with k_at4:
            st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_PURPLE_DARK};"><div class="kpi-title">Média semanal (Telefone)</div><div class="kpi-value">{media_semanal_tel}</div><div class="kpi-subtitle">{media_diaria_tel} atendimentos por dia ativo</div></div>""", unsafe_allow_html=True)
        with k_at5:
            st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_GREEN};"><div class="kpi-title">Média semanal (Vídeo)</div><div class="kpi-value">{media_semanal_vid}</div><div class="kpi-subtitle">{media_diaria_vid} sessões por dia com agendamentos</div></div>""", unsafe_allow_html=True)
        with k_at6:
            st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_PEACH_DEEP};"><div class="kpi-title">Média semanal consolidada</div><div class="kpi-value">{media_semanal_total}</div><div class="kpi-subtitle">{media_diaria_total} atendimentos por dia (todas as modalidades)</div></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Gráfico 1: Evolução Mensal dos Atendimentos por Modalidade (Março a Outubro)
        meses_rotulos = {
            '2026-03': 'Mar/2026', '2026-04': 'Abr/2026', '2026-05': 'Mai/2026',
            '2026-06': 'Jun/2026', '2026-07': 'Jul/2026', '2026-08': 'Ago/2026',
            '2026-09': 'Set/2026', '2026-10': 'Out/2026'
        }
        df_evol_at = df_atend.groupby(['mes_ano', 'categoria_modalidade']).size().reset_index(name='Atendimentos')
        df_evol_at['Mês'] = df_evol_at['mes_ano'].map(meses_rotulos).fillna(df_evol_at['mes_ano'])
        
        fig_evol_at = px.bar(
            df_evol_at, x='Mês', y='Atendimentos', color='categoria_modalidade',
            title="Evolução mensal dos atendimentos por modalidade (2026)",
            barmode='group',
            color_discrete_sequence=[BRAND_PURPLE_DARK, BRAND_GREEN, BRAND_PEACH_DEEP, BRAND_PURPLE_LIGHT, BRAND_GREEN_DARK, '#C49B7A', '#A388C8', '#85A344']
        )
        fig_evol_at.update_traces(textposition='outside', cliponaxis=False)
        fig_evol_at.update_layout(
            legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5, font=dict(family='Plus Jakarta Sans, sans-serif', size=11, color=BRAND_PURPLE_DARK)),
            **PLOTLY_LAYOUT
        )
        apply_chart_theme(fig_evol_at, top_margin=60, bottom_margin=80)
        st.plotly_chart(fig_evol_at, use_container_width=True)

        # Consolidação das modalidades de atendimento (conforme layout oficial da imagem)
        st.markdown("#### Consolidação das modalidades de atendimento")
        
        categorias_excluir_modalidades = [
            'encaminhamento formal',
            'atendimento presencial',
            'petição / demanda jurídica',
            'peticao / demanda juridica',
            'atendimento geral'
        ]
        df_tab = df_atend[
            ~df_atend['categoria_modalidade'].str.lower().isin(categorias_excluir_modalidades) &
            ~df_atend['categoria_modalidade'].str.lower().str.contains('cancel|ausên|ausen')
        ].copy()
        
        df_agg = df_tab['categoria_modalidade'].value_counts().reset_index()
        df_agg.columns = ['Modalidade de Atendimento', 'Total Realizado']
        tot_filtrado = df_agg['Total Realizado'].sum()
        df_agg['Proporção (%)'] = (df_agg['Total Realizado'] / tot_filtrado * 100).round(1).astype(str) + '%'
        
        # Média semanal calculada com base em 33 semanas úteis (165 dias úteis com atividades)
        semanas_ref = 33.0
        df_agg['Média Semanal'] = (df_agg['Total Realizado'] / semanas_ref).round(2).astype(str) + ' / sem'
        
        st.dataframe(df_agg, use_container_width=True, hide_index=True)

        # Nota Oficial: Telefone e Mensagens (WhatsApp) - idêntica à imagem
        st.markdown(f"""
        <div style="background-color: #F8F6FD; border-left: 4px solid {BRAND_PURPLE}; padding: 1.15rem 1.4rem; border-radius: 10px; margin-top: 1.5rem; margin-bottom: 1.2rem;">
            <h4 style="margin: 0 0 0.5rem 0; color: {BRAND_PURPLE_DARK}; font-size: 1.05rem;">
                📞 Acompanhamento contínuo por telefone e mensagens (WhatsApp)
            </h4>
            <p style="margin: 0 0 0.6rem 0; font-size: 0.93rem; color: #1F2937; line-height: 1.55;">
                No período analisado (março a outubro de 2026), foram registrados <b>2496 atendimentos</b> distribuídos em <b>165 dias com atividades</b> (aproximadamente 33 semanas úteis).
            </p>
            <p style="margin: 0 0 0.6rem 0; font-size: 0.93rem; color: #1F2937; line-height: 1.55;">
                O atendimento por telefone e mensagens de texto/áudio configurou-se como o <b>principal canal de orientação e acompanhamento individualizado</b>, respondendo por <b>2006 atendimentos</b> com uma média de <b>60.8 atendimentos por semana</b> (12.2 por dia com atendimentos).
            </p>
            <p style="margin: 0; font-size: 0.88rem; color: #4B5563; line-height: 1.5; font-style: italic; border-top: 1px dashed #D1D5DB; padding-top: 0.65rem;">
                <b>Dinâmica entre formulários e atendimentos continuados:</b> Os formulários de acolhimento representam a porta de entrada formal para novos casos no serviço. A partir dessa entrada, cada assistida gera múltiplos atendimentos de retorno e acompanhamento ao longo dos meses por telefone, WhatsApp e vídeo.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Nota Oficial: Demanda por Vídeo - idêntica à imagem
        st.markdown(f"""
        <div style="background-color: #F0FDF4; border-left: 4px solid {BRAND_GREEN}; padding: 1.05rem 1.3rem; border-radius: 10px; margin-top: 0.5rem; margin-bottom: 1.5rem;">
            <h4 style="margin: 0 0 0.45rem 0; color: {BRAND_GREEN_DARK}; font-size: 1.0rem;">
                📹 Atendimentos individualizados por vídeo
            </h4>
            <p style="margin: 0; font-size: 0.92rem; color: #1F2937; line-height: 1.55;">
                Foram realizadas <b>299 sessões por vídeo com comparecimento efetivo</b>, realizadas ao longo de <b>134 dias</b>, representando uma média de <b>9.1 sessões por semana</b> (2.2 sessões por dia em que a modalidade ocorreu).
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Nenhum dado de atendimento encontrado para os filtros selecionados.")

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


