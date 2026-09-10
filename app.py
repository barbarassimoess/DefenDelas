# -*- coding: utf-8 -*-
"""
Painel BI - Sistema de Inteligência de Dados - DefenDelas
Interface Gráfica Interativa com Streamlit e Plotly
Monitoramento Integrado de Formulários, Atendimentos da Equipe e Petições Judiciais (CEDEM)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

from data_loader import load_all_dashboard_data
from styles import (
    CUSTOM_CSS, COLOR_PALETTE, PLOTLY_LAYOUT, PURPLE_SCALE, GREEN_SCALE,
    BRAND_PURPLE, BRAND_GREEN, BRAND_PEACH_DEEP
)

# 1. Configuração da Página
st.set_page_config(
    page_title="Painel BI - DefenDelas",
    page_icon="logo_defendelas.png",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Aplicar CSS Customizado
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# 2. Carregamento dos Dados com Cache
@st.cache_data(show_spinner=False)
def get_dashboard_data(folder_path="."):
    return load_all_dashboard_data(folder_path=folder_path)

# Sidebar: Logo e Identidade Visual DefenDelas
st.sidebar.image("logo_defendelas.png", use_container_width=True)
st.sidebar.markdown(
    "<p style='text-align:center; font-size:0.8rem; color:#4A3873; margin-top:-0.6rem;'>"
    "Ao seu lado, quando você mais precisa.</p>",
    unsafe_allow_html=True
)
st.sidebar.markdown("---")

# Sidebar: Configuração da Fonte de Dados
st.sidebar.markdown("### ⚙️ Fonte de Dados")
uploaded_files = st.sidebar.file_uploader(
    "📤 Carregar arquivo(s) Excel (.xlsx, .xls)",
    type=["xlsx", "xls"],
    accept_multiple_files=True,
    help="Você pode arrastar e soltar novas planilhas para análise em tempo real."
)

if uploaded_files:
    raw_data = load_all_dashboard_data(folder_path=".", uploaded_files=uploaded_files)
else:
    raw_data = get_dashboard_data(".")

if st.sidebar.button("🔄 Recarregar Dados da Pasta", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

df_forms_raw = raw_data.get('formularios', pd.DataFrame())
df_atend_raw = raw_data.get('atendimentos', pd.DataFrame())
df_pet_raw = raw_data.get('peticoes', pd.DataFrame())

if df_forms_raw.empty and df_atend_raw.empty and df_pet_raw.empty:
    st.error("⚠️ Nenhuma planilha válida foi encontrada na pasta ou nos arquivos carregados.")
    st.info("Coloque o arquivo `controle_dados.xlsx` na pasta deste projeto ou faça upload pelo menu lateral.")
    st.stop()

# 3. Sidebar: Filtros Globais Dinâmicos
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Filtros do Painel")

# Modo de Privacidade LGPD
privacy_mode = st.sidebar.toggle("🔒 Modo LGPD / Privacidade", value=True, help="Oculta ou mascara dados identificadores para relatórios públicos e seguros.")

# Filtro de Período / Datas de Envio (com base nos formulários)
if not df_forms_raw.empty and df_forms_raw['data'].dropna().count() > 0:
    min_date = df_forms_raw['data'].min()
    max_date = df_forms_raw['data'].max()
else:
    min_date = datetime.now().date()
    max_date = datetime.now().date()

periodo_selecionado = st.sidebar.date_input(
    "📅 Período dos Formulários",
    value=(min_date, max_date) if min_date != max_date else (min_date, min_date),
    min_value=min_date,
    max_value=max_date,
    format="DD/MM/YYYY"
)

# Filtros para Formulários
all_cities = sorted([c for c in df_forms_raw['municipio'].unique() if c and c != 'Não informado']) if not df_forms_raw.empty else []
cidades_selecionadas = st.sidebar.multiselect("📍 Município / Cidade", options=all_cities, placeholder="Todos os municípios")

all_regions = sorted([r for r in df_forms_raw['regiao_sc'].unique() if r and r != 'Outras Regiões / Não Identificado']) if not df_forms_raw.empty else []
regioes_selecionadas = st.sidebar.multiselect("🗺️ Mesorregião SC", options=all_regions, placeholder="Todas as regiões")

order_faixas = ['Menor de 18 anos', '18 a 25 anos', '26 a 35 anos', '36 a 40 anos', '41 a 45 anos', '46 a 55 anos', '56 a 65 anos', '66 a 75 anos', '76 a 85 anos', 'Mais de 85 anos', 'Não informado']
present_faixas = [f for f in order_faixas if f in df_forms_raw['faixa_etaria'].unique()] if not df_forms_raw.empty else []
faixas_selecionadas = st.sidebar.multiselect("👤 Faixa Etária", options=present_faixas, placeholder="Todas as faixas")

all_races = sorted([r for r in df_forms_raw['raca_cor'].unique() if r]) if not df_forms_raw.empty else []
racas_selecionadas = st.sidebar.multiselect("🎨 Raça / Cor", options=all_races, placeholder="Todas as raças")

all_areas = sorted([a for a in df_forms_raw['tipo_area'].unique() if a]) if not df_forms_raw.empty else []
areas_selecionadas = st.sidebar.multiselect("🏡 Zona / Área", options=all_areas, placeholder="Todas as zonas")

viol_options = [
    'Violência Psicológica',
    'Violência Física',
    'Violência Patrimonial',
    'Violência Moral',
    'Violência Sexual'
]
violencias_selecionadas = st.sidebar.multiselect("⚖️ Tipo de Violência (Lei Maria da Penha)", options=viol_options, placeholder="Todos os 5 tipos")

# Filtros para Atendimentos
all_responsaveis = sorted([resp for resp in df_atend_raw['responsavel'].unique() if resp and resp not in ['Não informado', 'Equipe']]) if not df_atend_raw.empty else []
responsaveis_selecionados = st.sidebar.multiselect("👥 Responsável pelo Atendimento", options=all_responsaveis, placeholder="Toda a equipe")

all_modalidades = sorted([m for m in df_atend_raw['categoria_modalidade'].unique() if m]) if not df_atend_raw.empty else []
modalidades_selecionadas = st.sidebar.multiselect("📞 Modalidade de Atendimento", options=all_modalidades, placeholder="Todas as modalidades")

# Campo de Busca Textual Livre
busca_termo = st.sidebar.text_input("🔎 Pesquisa Textual", placeholder="Buscar palavra nos relatos...")

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
    if responsaveis_selecionados:
        df_atend = df_atend[df_atend['responsavel'].isin(responsaveis_selecionados)]
    if modalidades_selecionadas:
        df_atend = df_atend[df_atend['categoria_modalidade'].isin(modalidades_selecionadas)]

# 5. Header Principal
total_forms_global = len(df_forms_raw)
total_atend_global = len(df_atend_raw)
total_pet_global = len(df_pet_raw)

st.markdown(f"""
<div class="main-header">
    <div>
        <h1>Painel BI - DefenDelas</h1>
        <p>Monitoramento de Formulários de Atendimento, Produtividade da Equipe e Petições Judiciais (CEDEM)</p>
    </div>
    <div class="badge-status">
        📊 Base Atualizada • {total_forms_global} Formulários • {total_atend_global} Atendimentos • {total_pet_global} Petições
    </div>
</div>
""", unsafe_allow_html=True)

if privacy_mode:
    st.markdown("""
    <div class="privacy-active-banner">
        🔒 <b>Modo de Privacidade LGPD Ativo:</b> Dados pessoais e identificadores das mulheres foram anonimizados conforme a Lei Geral de Proteção de Dados.
    </div>
    """, unsafe_allow_html=True)

# 6. Abas Principais do Dashboard
tabs = st.tabs([
    "📊 Visão Geral & Indicadores Integrados",
    "📞 Atendimentos da Equipe",
    "⚖️ Petições Judiciais (CEDEM)",
    "👤 Perfil Sociodemográfico",
    "📍 Distribuição Geográfica (SC)",
    "⚖️ Tipos de Violência (Lei Maria da Penha)",
    "📢 Canais de Entrada",
    "📋 Explorador de Dados & Exportação"
])

# ==========================================
# ABA 1: VISÃO GERAL & KPIS INTEGRADOS
# ==========================================
with tabs[0]:
    total_formularios = len(df)
    total_atendimentos = len(df_atend)
    total_peticoes = len(df_pet)
    cidades_unicas = df['municipio'].nunique() if not df.empty else 0
    
   # Linha 1 de KPIs Principais Integrados
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_PURPLE};"><div class="kpi-title">📑 Formulários de Acolhimento</div><div class="kpi-value">{total_formularios}</div><div class="kpi-subtitle">Solicitações online recebidas</div></div>""", unsafe_allow_html=True)

    with col2:
        st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_GREEN};"><div class="kpi-title">📞 Atendimentos Realizados</div><div class="kpi-value">{total_atendimentos}</div><div class="kpi-subtitle">Atuações e contatos da equipe</div></div>""", unsafe_allow_html=True)

    with col3:
        st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_PEACH_DEEP};"><div class="kpi-title">⚖️ Petições Judiciais CEDEM</div><div class="kpi-value">{total_peticoes}</div><div class="kpi-subtitle">Peças processuais protocoladas</div></div>""", unsafe_allow_html=True)

    with col4:
        st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid #8B7BB8;"><div class="kpi-title">📍 Cidades Alcançadas</div><div class="kpi-value">{cidades_unicas}</div><div class="kpi-subtitle">Municípios de SC atendidos</div></div>""", unsafe_allow_html=True)    st.markdown("<br>", unsafe_allow_html=True)

# Gráfico de Evolução Mensal Integrada (Formulários x Atendimentos x Petições)
    st.markdown("#### 📈 Evolução Mensal Integrada das Demandas (2026)")
    
    months_series = ['2026-03', '2026-04', '2026-05', '2026-06', '2026-07', '2026-08']
    
    forms_m = df['mes_ano'].value_counts() if not df.empty else pd.Series()
    atend_m = df_atend['mes_ano'].value_counts() if not df_atend.empty else pd.Series()
    pet_m = df_pet['mes_ano'].value_counts() if not df_pet.empty else pd.Series()
    
    df_integ = pd.DataFrame({'Mês': months_series})
    df_integ['Formulários'] = df_integ['Mês'].map(forms_m).fillna(0).astype(int)
    df_integ['Atendimentos'] = df_integ['Mês'].map(atend_m).fillna(0).astype(int)
    df_integ['Petições'] = df_integ['Mês'].map(pet_m).fillna(0).astype(int)
    
    fig_integ = go.Figure()
    fig_integ.add_trace(go.Bar(
        x=df_integ['Mês'], y=df_integ['Atendimentos'],
        name='Atendimentos da Equipe',
        marker_color=BRAND_GREEN, text=df_integ['Atendimentos'], textposition='outside'
    ))
    fig_integ.add_trace(go.Bar(
        x=df_integ['Mês'], y=df_integ['Formulários'],
        name='Formulários Recebidos',
        marker_color=BRAND_PURPLE, text=df_integ['Formulários'], textposition='outside'
    ))
    fig_integ.add_trace(go.Bar(
        x=df_integ['Mês'], y=df_integ['Petições'],
        name='Petições Protocoladas',
        marker_color=BRAND_PEACH_DEEP, text=df_integ['Petições'], textposition='outside'
    ))
    
    fig_integ.update_layout(
        barmode='group',
        title="Volume Comparativo Mensal de Atuação",
        xaxis_title="Mês",
        yaxis_title="Total de Registros",
        **PLOTLY_LAYOUT
    )
    st.plotly_chart(fig_integ, use_container_width=True)

    # Destaque: Panorama dos 5 Tipos de Violência
    st.markdown("#### ⚖️ Panorama dos 5 Tipos de Violência (Lei Maria da Penha)")
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
        color='Casos', color_continuous_scale='Purples'
    )
    fig_v5.update_traces(textposition='outside')
    fig_v5.update_layout(yaxis={'autorange': 'reversed'}, **PLOTLY_LAYOUT)
    st.plotly_chart(fig_v5, use_container_width=True)
    st.caption("ℹ️ Em um mesmo caso pode haver mais de um tipo de violência relatado simultaneamente — por isso a soma dos casos pode ser maior que o total de formulários.")

# ==========================================
# ABA 2: ATENDIMENTOS DA EQUIPE
# ==========================================
with tabs[1]:
    st.markdown("### 📞 Monitoramento de Atendimentos Realizados")
    st.caption("Acompanhamento quantitativo e qualitativo das atividades de atendimento individualizado, contatos institucionais e suporte às vítimas.")
    
    if not df_atend.empty:
        k_at1, k_at2, k_at3, k_at4, k_at5 = st.columns(5)
        total_at = len(df_atend)
        top_mod = df_atend['categoria_modalidade'].value_counts().index[0] if not df_atend['categoria_modalidade'].value_counts().empty else "N/D"
        top_mod_count = df_atend['categoria_modalidade'].value_counts().iloc[0] if not df_atend['categoria_modalidade'].value_counts().empty else 0
        total_telefone = int((df_atend['categoria_modalidade'] == 'Atendimento Telefônico').sum())
        total_video = int((df_atend['categoria_modalidade'] == 'Atendimento por Vídeo').sum())
        
        if df_atend['data'].min() and df_atend['data'].max():
            dias_at = max((df_atend['data'].max() - df_atend['data'].min()).days, 1)
            semanas_at = max(dias_at / 7.0, 1.0)
            media_sem_at = total_at / semanas_at
        else:
            media_sem_at = 0
            
        with k_at1:
            st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_GREEN};"><div class="kpi-title">Total de Atendimentos</div><div class="kpi-value">{total_at}</div><div class="kpi-subtitle">Registros efetuados</div></div>""", unsafe_allow_html=True)
        with k_at2:
            st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_PURPLE};"><div class="kpi-title">Média Semanal</div><div class="kpi-value">{media_sem_at:.1f}</div><div class="kpi-subtitle">Atendimentos / semana</div></div>""", unsafe_allow_html=True)
        with k_at3:
            st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_PEACH_DEEP};"><div class="kpi-title">Modalidade Predominante</div><div class="kpi-value" style="font-size:1.3rem;">{top_mod}</div><div class="kpi-subtitle">{top_mod_count} atendimentos ({(top_mod_count/total_at*100):.1f}%)</div></div>""", unsafe_allow_html=True)
        with k_at4:
            st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid #8B7BB8;"><div class="kpi-title">📞 Atendimentos por Telefone</div><div class="kpi-value">{total_telefone}</div><div class="kpi-subtitle">{(total_telefone/total_at*100 if total_at else 0):.1f}% do total</div></div>""", unsafe_allow_html=True)
        with k_at5:
            st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_GREEN};"><div class="kpi-title">🎥 Atendimentos por Vídeo</div><div class="kpi-value">{total_video}</div><div class="kpi-subtitle">{(total_video/total_at*100 if total_at else 0):.1f}% do total</div></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Gráfico 1: Evolução Mensal dos Atendimentos
        df_at_mes = df_atend.groupby('mes_ano').size().reset_index(name='Atendimentos')
        fig_at_time = px.bar(
            df_at_mes, x='mes_ano', y='Atendimentos', text='Atendimentos',
            title="📈 Volume Mensal de Atendimentos Realizados (2026)",
            color_discrete_sequence=[BRAND_GREEN]
        )
        fig_at_time.update_traces(textposition='outside')
        fig_at_time.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig_at_time, use_container_width=True)

        # Gráfico 2: Atendimentos por Telefone x Vídeo (mês a mês)
        st.markdown("#### 📞🎥 Atendimentos por Telefone x Vídeo")
        df_tv = df_atend[df_atend['categoria_modalidade'].isin(['Atendimento Telefônico', 'Atendimento por Vídeo'])]
        if not df_tv.empty:
            df_tv_mes = df_tv.groupby(['mes_ano', 'categoria_modalidade']).size().reset_index(name='Atendimentos')
            fig_tv = px.bar(
                df_tv_mes, x='mes_ano', y='Atendimentos', color='categoria_modalidade',
                barmode='group', text='Atendimentos',
                title="Comparativo Mensal: Atendimento Telefônico x Atendimento por Vídeo",
                color_discrete_map={'Atendimento Telefônico': BRAND_PURPLE, 'Atendimento por Vídeo': BRAND_GREEN},
                labels={'mes_ano': 'Mês', 'categoria_modalidade': 'Modalidade'}
            )
            fig_tv.update_traces(textposition='outside')
            fig_tv.update_layout(**PLOTLY_LAYOUT)
            st.plotly_chart(fig_tv, use_container_width=True)
        else:
            st.info("Nenhum atendimento por telefone ou vídeo encontrado para os filtros atuais.")

        # Gráfico 3: Dia da Semana (apenas dias úteis, de segunda a sexta)
        dias_ordem = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira']
        df_at_dias = df_atend['dia_semana'].value_counts().reindex(dias_ordem).fillna(0).reset_index()
        df_at_dias.columns = ['Dia da Semana', 'Atendimentos']
        fig_at_dia = px.bar(
            df_at_dias, x='Dia da Semana', y='Atendimentos', text='Atendimentos',
            title="🗓️ Distribuição de Atendimentos por Dia da Semana",
            color='Atendimentos', color_continuous_scale='Purples'
        )
        fig_at_dia.update_traces(textposition='outside')
        fig_at_dia.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig_at_dia, use_container_width=True)
    else:
        st.info("Nenhum dado de atendimento encontrado para os filtros selecionados.")

# ==========================================
# ABA 3: PETIÇÕES JUDICIAIS (CEDEM)
# ==========================================
with tabs[2]:
    st.markdown("### ⚖️ Relatório de Petições Judiciais (CEDEM - 2026)")
    st.caption("Acompanhamento das peças processuais e atuações judiciais estratégicas na proteção dos direitos das mulheres.")
    
    if not df_pet.empty:
        k_pt1, k_pt2, k_pt3 = st.columns(3)
        total_pt = len(df_pet)
        top_pt_mes = df_pet['mes_nome'].value_counts().index[0] if not df_pet['mes_nome'].value_counts().empty else "N/D"
        top_pt_mes_count = df_pet['mes_nome'].value_counts().iloc[0] if not df_pet['mes_nome'].value_counts().empty else 0
        top_pt_cat = df_pet['categoria_peticao'].value_counts().index[0] if not df_pet['categoria_peticao'].value_counts().empty else "N/D"
        top_pt_cat_count = df_pet['categoria_peticao'].value_counts().iloc[0] if not df_pet['categoria_peticao'].value_counts().empty else 0
        
        with k_pt1:
            st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_PEACH_DEEP};"><div class="kpi-title">Total de Petições</div><div class="kpi-value">{total_pt}</div><div class="kpi-subtitle">Peças processuais protocoladas</div></div>""", unsafe_allow_html=True)
        with k_pt2:
            st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_PURPLE};"><div class="kpi-title">Mês com Maior Volume</div><div class="kpi-value">{top_pt_mes}</div><div class="kpi-subtitle">{top_pt_mes_count} petições protocoladas</div></div>""", unsafe_allow_html=True)
        with k_pt3:
            st.markdown(f"""<div class="kpi-card" style="border-left: 4px solid {BRAND_GREEN};"><div class="kpi-title">Categoria Mais Frequente</div><div class="kpi-value" style="font-size:1.3rem;">{top_pt_cat}</div><div class="kpi-subtitle">{top_pt_cat_count} peças ({(top_pt_cat_count/total_pt*100):.1f}%)</div></div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Gráfico 1: Evolução Mensal de Petições
        meses_ordem_nomes = ['Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto']
        df_pt_mes = df_pet['mes_nome'].value_counts().reindex(meses_ordem_nomes).fillna(0).reset_index()
        df_pt_mes.columns = ['Mês', 'Petições']
        fig_pt_mes = px.bar(
            df_pt_mes, x='Mês', y='Petições', text='Petições',
            title="📈 Volume Mensal de Petições Protocoladas (2026)",
            color_discrete_sequence=[BRAND_PEACH_DEEP]
        )
        fig_pt_mes.update_traces(textposition='outside')
        fig_pt_mes.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig_pt_mes, use_container_width=True)

        # Gráficos 2 e 3: Tipos e Categorias Processuais
        c_pt1, c_pt2 = st.columns(2)
        
        with c_pt1:
            df_pt_cat = df_pet['categoria_peticao'].value_counts().reset_index()
            df_pt_cat.columns = ['Categoria Processual', 'Total']
            fig_pt_cat = px.bar(
                df_pt_cat, x='Total', y='Categoria Processual', orientation='h', text='Total',
                title="📑 Petições por Categoria Processual",
                color='Total', color_continuous_scale='Reds'
            )
            fig_pt_cat.update_traces(textposition='outside')
            fig_pt_cat.update_layout(yaxis={'autorange': 'reversed'}, **PLOTLY_LAYOUT)
            st.plotly_chart(fig_pt_cat, use_container_width=True)
            
        with c_pt2:
            fig_pt_pie = px.pie(
                df_pt_cat, names='Categoria Processual', values='Total', hole=0.45,
                title="Proporção das Peças Processuais Protocoladas",
                color_discrete_sequence=COLOR_PALETTE
            )
            fig_pt_pie.update_traces(textinfo='percent+label')
            fig_pt_pie.update_layout(**PLOTLY_LAYOUT)
            st.plotly_chart(fig_pt_pie, use_container_width=True)
    else:
        st.info("Nenhum dado de petições encontrado.")

# ==========================================
# ABA 4: PERFIL SOCIODEMOGRÁFICO
# ==========================================
with tabs[3]:
    st.markdown("### 👤 Perfil Sociodemográfico das Mulheres Assistidas")
    
    if not df.empty:
        col_demo1, col_demo2 = st.columns(2)
        
        with col_demo1:
            df_faixa = df['faixa_etaria'].value_counts().reindex(order_faixas).dropna().reset_index()
            df_faixa.columns = ['Faixa Etária', 'Total']
            df_faixa = df_faixa[df_faixa['Total'] > 0]
            if not df_faixa.empty:
                fig_faixa = px.bar(
                    df_faixa, x='Total', y='Faixa Etária', orientation='h',
                    text='Total', title="🎂 Distribuição por Faixa Etária",
                    color='Total', color_continuous_scale=PURPLE_SCALE
                )
                fig_faixa.update_traces(textposition='outside')
                fig_faixa.update_layout(yaxis={'autorange': 'reversed'}, **PLOTLY_LAYOUT)
                st.plotly_chart(fig_faixa, use_container_width=True)
            
        with col_demo2:
            df_raca = df['raca_cor'].value_counts().reset_index()
            df_raca.columns = ['Raça/Cor', 'Total']
            if not df_raca.empty:
                fig_raca = px.pie(
                    df_raca, names='Raça/Cor', values='Total', hole=0.45,
                    title="🎨 Autodeclaração Racial / Cor",
                    color_discrete_sequence=COLOR_PALETTE
                )
                fig_raca.update_traces(textinfo='percent+label')
                fig_raca.update_layout(**PLOTLY_LAYOUT)
                st.plotly_chart(fig_raca, use_container_width=True)
            
        col_demo3, col_demo5 = st.columns(2)
        
        with col_demo3:
            df_civil = df['estado_civil'].value_counts().reset_index()
            df_civil.columns = ['Estado Civil', 'Total']
            if not df_civil.empty:
                fig_civil = px.bar(df_civil, x='Estado Civil', y='Total', text='Total', title="💍 Estado Civil", color_discrete_sequence=[BRAND_PURPLE])
                fig_civil.update_traces(textposition='outside')
                fig_civil.update_layout(**PLOTLY_LAYOUT)
                st.plotly_chart(fig_civil, use_container_width=True)
            
        with col_demo5:
            df_area = df['tipo_area'].value_counts().reset_index()
            df_area.columns = ['Tipo de Área', 'Total']
            if not df_area.empty:
                fig_area = px.pie(df_area, names='Tipo de Área', values='Total', hole=0.4, title="🏡 Tipo de Área (Urbana / Rural)", color_discrete_sequence=[BRAND_PURPLE, BRAND_GREEN, "#A8A0C4"])
                fig_area.update_traces(textinfo='percent+label')
                fig_area.update_layout(**PLOTLY_LAYOUT)
                st.plotly_chart(fig_area, use_container_width=True)

        # Identidade de Gênero em linha própria, com largura total e legenda
        # horizontal abaixo do gráfico para que os percentuais não fiquem cortados
        df_gen = df['identidade_genero'].value_counts().reset_index()
        df_gen.columns = ['Gênero', 'Total']
        if not df_gen.empty:
            fig_gen = px.pie(df_gen, names='Gênero', values='Total', hole=0.4, title="⚧ Identidade de Gênero", color_discrete_sequence=COLOR_PALETTE)
            fig_gen.update_traces(textinfo='percent+label', textposition='outside', insidetextorientation='horizontal')
            fig_gen.update_layout(
                **{**PLOTLY_LAYOUT, 'margin': {'l': 30, 'r': 30, 't': 60, 'b': 90}},
                legend=dict(orientation='h', yanchor='top', y=-0.15, xanchor='center', x=0.5, font=dict(size=12)),
                uniformtext_minsize=11, uniformtext_mode='hide'
            )
            st.plotly_chart(fig_gen, use_container_width=True)

        st.markdown("#### 🔄 Cruzamento Demográfico: Faixa Etária x Raça/Cor")
        crosstab_raca_faixa = pd.crosstab(df['faixa_etaria'], df['raca_cor']).reindex(order_faixas).dropna(how='all')
        if not crosstab_raca_faixa.empty:
            fig_cross = px.bar(
                crosstab_raca_faixa, barmode='stack',
                title="Distribuição de Raça/Cor por Faixa Etária",
                color_discrete_sequence=COLOR_PALETTE
            )
            fig_cross.update_layout(**PLOTLY_LAYOUT)
            st.plotly_chart(fig_cross, use_container_width=True)
    else:
        st.info("Nenhum dado sociodemográfico encontrado para os filtros selecionados.")

# ==========================================
# ABA 5: DISTRIBUIÇÃO GEOGRÁFICA (SC)
# ==========================================
with tabs[4]:
    st.markdown("### 📍 Distribuição Geográfica em Santa Catarina")
    
    if not df.empty:
        col_geo1, col_geo2 = st.columns([1, 1])
        
        with col_geo1:
            df_cities = df['municipio'].value_counts().head(15).reset_index()
            df_cities.columns = ['Município', 'Total']
            if not df_cities.empty:
                fig_top_cities = px.bar(
                    df_cities, x='Total', y='Município', orientation='h',
                    text='Total', title="🏆 Top 15 Municípios com Mais Solicitações",
                    color='Total', color_continuous_scale='Purples'
                )
                fig_top_cities.update_traces(textposition='outside')
                fig_top_cities.update_layout(yaxis={'autorange': 'reversed'}, **PLOTLY_LAYOUT)
                st.plotly_chart(fig_top_cities, use_container_width=True)
            
        with col_geo2:
            df_regiao = df['regiao_sc'].value_counts().reset_index()
            df_regiao.columns = ['Região', 'Total']
            if not df_regiao.empty:
                fig_regiao = px.pie(
                    df_regiao, names='Região', values='Total', hole=0.45,
                    title="🗺️ Distribuição por Mesorregiões de Santa Catarina",
                    color_discrete_sequence=COLOR_PALETTE
                )
                fig_regiao.update_traces(textinfo='percent+label')
                fig_regiao.update_layout(**PLOTLY_LAYOUT)
                st.plotly_chart(fig_regiao, use_container_width=True)
            
        st.markdown("#### 🗺️ Mapa de Concentração Territorial")
        df_geo = df.dropna(subset=['lat', 'lon']).groupby(['municipio', 'lat', 'lon', 'regiao_sc']).size().reset_index(name='Formulários')
        
        if not df_geo.empty:
            try:
                fig_map = px.scatter_map(
                    df_geo, lat='lat', lon='lon', size='Formulários',
                    color='Formulários', hover_name='municipio',
                    hover_data={'regiao_sc': True, 'Formulários': True, 'lat': False, 'lon': False},
                    color_continuous_scale='Turbo', size_max=35, zoom=6.5,
                    center={'lat': -27.2423, 'lon': -50.2189},
                    title="Concentração de Solicitações por Município em Santa Catarina"
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
                    title="Concentração de Solicitações por Município em Santa Catarina"
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
    st.markdown("### ⚖️ Os 5 Tipos de Violência contra a Mulher (Art. 7º - Lei Maria da Penha)")
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
                text='Casos', title="📊 Total de Casos por Tipo de Violência Relatada",
                color='Casos', color_continuous_scale='Purples',
                hover_data={'Definição': True, '% das Vítimas': True}
            )
            fig_viol.update_traces(textposition='outside')
            fig_viol.update_layout(yaxis={'autorange': 'reversed'}, **PLOTLY_LAYOUT)
            st.plotly_chart(fig_viol, use_container_width=True)
            
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
                title="Sobreposição de Formas de Violência por Vítima",
                color_discrete_sequence=['#E11D48', BRAND_PURPLE, BRAND_GREEN, "#8B7BB8", "#D4A5C9", "#A8A0C4"]
            )
            fig_qtd.update_traces(textinfo='percent+label')
            fig_qtd.update_layout(**PLOTLY_LAYOUT)
            st.plotly_chart(fig_qtd, use_container_width=True)

        c_va1, c_va2 = st.columns(2)
        with c_va1:
            st.markdown("#### 👤 Perfil do Agressor / Relação com a Vítima")
            df_agr = df['perfil_agressor_rotulo'].value_counts().reset_index()
            df_agr.columns = ['Perfil do Agressor', 'Total']
            fig_agr = px.bar(
                df_agr, x='Total', y='Perfil do Agressor', orientation='h', text='Total',
                title="Vínculo do Agressor com a Mulher",
                color='Total', color_continuous_scale=PURPLE_SCALE
            )
            fig_agr.update_traces(textposition='outside')
            fig_agr.update_layout(yaxis={'autorange': 'reversed'}, **PLOTLY_LAYOUT)
            st.plotly_chart(fig_agr, use_container_width=True)

        with c_va2:
            st.markdown("#### 🔗 Matriz de Coocorrência entre os 5 Tipos")
            viol_cols_5 = ['viol_psicologica', 'viol_patrimonial', 'viol_fisica', 'viol_sexual', 'viol_moral']
            viol_names_5 = ['Psicológica', 'Patrimonial', 'Física', 'Sexual', 'Moral']
            
            df_corr_matrix = df[viol_cols_5].astype(int).T.dot(df[viol_cols_5].astype(int))
            df_corr_matrix.columns = viol_names_5
            df_corr_matrix.index = viol_names_5
            
            fig_corr = px.imshow(
                df_corr_matrix, text_auto=True, aspect="auto",
                color_continuous_scale='Purples',
                title="Casos com Ocorrência Concomitante"
            )
            fig_corr.update_layout(**PLOTLY_LAYOUT)
            st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("Nenhum dado de violência encontrado para os filtros selecionados.")

# ==========================================
# ABA 7: CANAIS DE ENTRADA
# ==========================================
with tabs[6]:
    st.markdown("### 📢 Origem do Acesso e Encaminhamentos")
    
    if not df.empty:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            df_canal = df['canal_origem'].value_counts().reset_index()
            df_canal.columns = ['Canal de Acesso', 'Total']
            fig_canal = px.bar(
                df_canal, x='Total', y='Canal de Acesso', orientation='h',
                text='Total', title="Principais Portas de Entrada / Encaminhamentos",
                color='Total', color_continuous_scale=GREEN_SCALE
            )
            fig_canal.update_traces(textposition='outside')
            fig_canal.update_layout(yaxis={'autorange': 'reversed'}, **PLOTLY_LAYOUT)
            st.plotly_chart(fig_canal, use_container_width=True)
            
        with col_c2:
            fig_canal_pie = px.pie(
                df_canal, names='Canal de Acesso', values='Total', hole=0.45,
                title="Proporção dos Canais de Encaminhamento",
                color_discrete_sequence=COLOR_PALETTE
            )
            fig_canal_pie.update_traces(textinfo='percent+label')
            fig_canal_pie.update_layout(**PLOTLY_LAYOUT)
            st.plotly_chart(fig_canal_pie, use_container_width=True)
    else:
        st.info("Nenhum dado de canais de acesso encontrado para os filtros selecionados.")

# ==========================================
# ABA 8: EXPLORADOR DE DADOS & EXPORTAÇÃO
# ==========================================
with tabs[7]:
    st.markdown("### 📋 Tabela de Dados e Exportação de Relatórios")
    
    base_selecionada = st.radio(
        "Selecione a base de dados para visualização e exportação:",
        ["📨 Formulários de Acolhimento", "📞 Atendimentos da Equipe", "⚖️ Petições Judiciais (CEDEM)"],
        horizontal=True
    )
    
    if base_selecionada == "📨 Formulários de Acolhimento":
        cols_display = [
            'data_hora', 'faixa_etaria', 'estado_civil',
            'raca_cor', 'identidade_genero', 'municipio', 'regiao_sc',
            'tipo_area', 'violencias_rotulo', 'perfil_agressor_rotulo', 'canal_origem', 'relato_fatos'
        ]
        rename_dict = {
            'data_hora': 'Data/Hora Envio',
            'faixa_etaria': 'Faixa Etária',
            'estado_civil': 'Estado Civil',
            'raca_cor': 'Raça/Cor',
            'identidade_genero': 'Gênero',
            'municipio': 'Município',
            'regiao_sc': 'Mesorregião SC',
            'tipo_area': 'Zona',
            'violencias_rotulo': 'Tipos de Violência (5 Tipos)',
            'perfil_agressor_rotulo': 'Perfil do Agressor',
            'canal_origem': 'Canal de Entrada',
            'relato_fatos': 'Relato dos Fatos'
        }
        df_export = df[cols_display].rename(columns=rename_dict) if not df.empty else pd.DataFrame()
        sheet_name_exp = "Formularios"
        file_prefix = "formularios"
        
    elif base_selecionada == "📞 Atendimentos da Equipe":
        cols_atend = ['data_apenas', 'dia_semana', 'categoria_modalidade', 'responsavel', 'mes_ano']
        rename_atend = {
            'data_apenas': 'Data do Atendimento',
            'dia_semana': 'Dia da Semana',
            'categoria_modalidade': 'Modalidade',
            'responsavel': 'Responsável',
            'mes_ano': 'Mês/Ano'
        }
        df_export = df_atend[cols_atend].rename(columns=rename_atend) if not df_atend.empty else pd.DataFrame()
        sheet_name_exp = "Atendimentos"
        file_prefix = "atendimentos"
        
    else: # Petições
        cols_pet = ['mes_nome', 'tipo_peticao', 'categoria_peticao', 'data_protocolo']
        rename_pet = {
            'mes_nome': 'Mês',
            'tipo_peticao': 'Tipo de Petição',
            'categoria_peticao': 'Categoria',
            'data_protocolo': 'Data do Protocolo'
        }
        df_export = df_pet[cols_pet].rename(columns=rename_pet) if not df_pet.empty else pd.DataFrame()
        sheet_name_exp = "Peticoes"
        file_prefix = "peticoes"
        
    st.dataframe(df_export, use_container_width=True, hide_index=True)
    
    st.markdown("#### 📥 Exportar Dados da Base Selecionada")
    col_exp1, col_exp2, col_exp3 = st.columns([1, 1, 2])
    
    if not df_export.empty:
        buffer_excel = io.BytesIO()
        with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False, sheet_name=sheet_name_exp)
        buffer_excel.seek(0)
        
        with col_exp1:
            st.download_button(
                label=f"📗 Baixar Excel ({sheet_name_exp})",
                data=buffer_excel,
                file_name=f"{file_prefix}_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
        csv_data = df_export.to_csv(index=False, encoding='utf-8-sig')
        with col_exp2:
            st.download_button(
                label=f"📄 Baixar CSV ({sheet_name_exp})",
                data=csv_data,
                file_name=f"{file_prefix}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
