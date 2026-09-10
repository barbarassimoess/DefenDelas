# -*- coding: utf-8 -*-
"""
Módulo de Carga, Limpeza, Padronização e Enriquecimento de Dados XLSX
Desenvolvido para o Sistema de Painel BI - DefenDelas / Formulários de Atendimento,
Atendimentos da Equipe e Petições Judiciais (CEDEM).
"""

import os
import glob
import io
import re
import unicodedata
import pandas as pd
import numpy as np
from datetime import datetime

# Data de corte do painel: nenhum registro após esta data deve ser exibido
# (o painel deve considerar apenas atendimentos/formulários até 31/08/2026)
DATA_CUTOFF = pd.Timestamp('2026-08-31 23:59:59')

# Coordenadas e Regiões de Municípios de Santa Catarina e Principais Cidades
CITIES_DB = {
    'Florianópolis': {'lat': -27.5954, 'lon': -48.5480, 'regiao': 'Grande Florianópolis'},
    'São José': {'lat': -27.6136, 'lon': -48.6366, 'regiao': 'Grande Florianópolis'},
    'Palhoça': {'lat': -27.6455, 'lon': -48.6678, 'regiao': 'Grande Florianópolis'},
    'Biguaçu': {'lat': -27.4939, 'lon': -48.6558, 'regiao': 'Grande Florianópolis'},
    'Santo Amaro da Imperatriz': {'lat': -27.6872, 'lon': -48.7786, 'regiao': 'Grande Florianópolis'},
    'Governador Celso Ramos': {'lat': -27.3158, 'lon': -48.5589, 'regiao': 'Grande Florianópolis'},
    'Tijucas': {'lat': -27.2414, 'lon': -48.6347, 'regiao': 'Grande Florianópolis'},
    'Canelinha': {'lat': -27.2625, 'lon': -48.7667, 'regiao': 'Grande Florianópolis'},
    'São João Batista': {'lat': -27.2761, 'lon': -48.8492, 'regiao': 'Grande Florianópolis'},
    'Antônio Carlos': {'lat': -27.5186, 'lon': -48.7694, 'regiao': 'Grande Florianópolis'},
    'Águas Mornas': {'lat': -27.6975, 'lon': -48.8242, 'regiao': 'Grande Florianópolis'},
    
    'Joinville': {'lat': -26.3045, 'lon': -48.8487, 'regiao': 'Norte Catarinense'},
    'Jaraguá do Sul': {'lat': -26.4850, 'lon': -49.0800, 'regiao': 'Norte Catarinense'},
    'São Francisco do Sul': {'lat': -26.2433, 'lon': -48.6381, 'regiao': 'Norte Catarinense'},
    'Itapoá': {'lat': -26.1172, 'lon': -48.6147, 'regiao': 'Norte Catarinense'},
    'Barra Velha': {'lat': -26.6322, 'lon': -48.6836, 'regiao': 'Norte Catarinense'},
    'São Bento do Sul': {'lat': -26.2503, 'lon': -49.3786, 'regiao': 'Norte Catarinense'},
    'Mafra': {'lat': -26.1114, 'lon': -49.8058, 'regiao': 'Norte Catarinense'},
    'Garuva': {'lat': -26.0294, 'lon': -48.8550, 'regiao': 'Norte Catarinense'},
    'Araquari': {'lat': -26.3708, 'lon': -48.7208, 'regiao': 'Norte Catarinense'},
    'Canoinhas': {'lat': -26.1772, 'lon': -50.3900, 'regiao': 'Norte Catarinense'},
    'Porto União': {'lat': -26.2381, 'lon': -51.0783, 'regiao': 'Norte Catarinense'},
    'Guaramirim': {'lat': -26.4731, 'lon': -49.0036, 'regiao': 'Norte Catarinense'},
    'Corupá': {'lat': -26.4253, 'lon': -49.2436, 'regiao': 'Norte Catarinense'},
    'Schroeder': {'lat': -26.4122, 'lon': -49.0733, 'regiao': 'Norte Catarinense'},
    'Campo Alegre': {'lat': -26.1931, 'lon': -49.2661, 'regiao': 'Norte Catarinense'},
    'Papanduva': {'lat': -26.3714, 'lon': -50.1411, 'regiao': 'Norte Catarinense'},
    
    'Blumenau': {'lat': -26.9194, 'lon': -49.0661, 'regiao': 'Vale do Itajaí'},
    'Itajaí': {'lat': -26.9078, 'lon': -48.6619, 'regiao': 'Vale do Itajaí'},
    'Brusque': {'lat': -27.0981, 'lon': -48.9169, 'regiao': 'Vale do Itajaí'},
    'Balneário Camboriú': {'lat': -26.9930, 'lon': -48.6353, 'regiao': 'Vale do Itajaí'},
    'Camboriú': {'lat': -27.0253, 'lon': -48.6547, 'regiao': 'Vale do Itajaí'},
    'Navegantes': {'lat': -26.8978, 'lon': -48.6547, 'regiao': 'Vale do Itajaí'},
    'Itapema': {'lat': -27.0911, 'lon': -48.6111, 'regiao': 'Vale do Itajaí'},
    'Porto Belo': {'lat': -27.1578, 'lon': -48.5539, 'regiao': 'Vale do Itajaí'},
    'Penha': {'lat': -26.7711, 'lon': -48.6475, 'regiao': 'Vale do Itajaí'},
    'Balneário Piçarras': {'lat': -26.7667, 'lon': -48.6708, 'regiao': 'Vale do Itajaí'},
    'Gaspar': {'lat': -26.9317, 'lon': -48.9592, 'regiao': 'Vale do Itajaí'},
    'Guabiruba': {'lat': -27.0850, 'lon': -48.9817, 'regiao': 'Vale do Itajaí'},
    'Indaial': {'lat': -26.8978, 'lon': -49.2319, 'regiao': 'Vale do Itajaí'},
    'Pomerode': {'lat': -26.7408, 'lon': -49.1764, 'regiao': 'Vale do Itajaí'},
    'Timbó': {'lat': -26.8233, 'lon': -49.2717, 'regiao': 'Vale do Itajaí'},
    'Rio do Sul': {'lat': -27.2142, 'lon': -49.6433, 'regiao': 'Vale do Itajaí'},
    'Ibirama': {'lat': -27.0569, 'lon': -49.5186, 'regiao': 'Vale do Itajaí'},
    'Botuverá': {'lat': -27.1989, 'lon': -49.0742, 'regiao': 'Vale do Itajaí'},
    'Agrolândia': {'lat': -27.4089, 'lon': -49.8258, 'regiao': 'Vale do Itajaí'},
    'Agronômica': {'lat': -27.2658, 'lon': -49.7119, 'regiao': 'Vale do Itajaí'},
    'Aurora': {'lat': -27.3108, 'lon': -49.6331, 'regiao': 'Vale do Itajaí'},
    'Trombudo Central': {'lat': -27.2978, 'lon': -49.7919, 'regiao': 'Vale do Itajaí'},
    
    'Criciúma': {'lat': -28.6775, 'lon': -49.3703, 'regiao': 'Sul Catarinense'},
    'Tubarão': {'lat': -28.4736, 'lon': -49.0072, 'regiao': 'Sul Catarinense'},
    'Araranguá': {'lat': -28.9358, 'lon': -49.4858, 'regiao': 'Sul Catarinense'},
    'Imbituba': {'lat': -28.2400, 'lon': -48.6703, 'regiao': 'Sul Catarinense'},
    'Laguna': {'lat': -28.4819, 'lon': -48.7806, 'regiao': 'Sul Catarinense'},
    'Içara': {'lat': -28.7136, 'lon': -49.3000, 'regiao': 'Sul Catarinense'},
    'Urussanga': {'lat': -28.5244, 'lon': -49.3214, 'regiao': 'Sul Catarinense'},
    'Nova Veneza': {'lat': -28.6369, 'lon': -49.4989, 'regiao': 'Sul Catarinense'},
    'Sombrio': {'lat': -29.1139, 'lon': -49.6167, 'regiao': 'Sul Catarinense'},
    'Passo de Torres': {'lat': -29.3139, 'lon': -49.7239, 'regiao': 'Sul Catarinense'},
    'Braço do Norte': {'lat': -28.2736, 'lon': -49.1650, 'regiao': 'Sul Catarinense'},
    'Orleans': {'lat': -28.3589, 'lon': -49.2917, 'regiao': 'Sul Catarinense'},
    'Capivari de Baixo': {'lat': -28.4453, 'lon': -48.9567, 'regiao': 'Sul Catarinense'},
    'Jaguaruna': {'lat': -28.6144, 'lon': -49.0267, 'regiao': 'Sul Catarinense'},
    'Forquilhinha': {'lat': -28.7478, 'lon': -49.4725, 'regiao': 'Sul Catarinense'},
    'Turvo': {'lat': -28.9264, 'lon': -49.6789, 'regiao': 'Sul Catarinense'},
    'Santa Rosa do Sul': {'lat': -29.1369, 'lon': -49.7119, 'regiao': 'Sul Catarinense'},
    'Praia Grande': {'lat': -29.1961, 'lon': -50.1097, 'regiao': 'Sul Catarinense'},
    'Garopaba': {'lat': -28.0269, 'lon': -48.6144, 'regiao': 'Sul Catarinense'},
    'Gravatal': {'lat': -28.3242, 'lon': -49.0381, 'regiao': 'Sul Catarinense'},
    'Siderópolis': {'lat': -28.5981, 'lon': -49.4242, 'regiao': 'Sul Catarinense'},
    'Morro da Fumaça': {'lat': -28.6508, 'lon': -49.2131, 'regiao': 'Sul Catarinense'},
    
    'Lages': {'lat': -27.8158, 'lon': -50.3261, 'regiao': 'Serrana'},
    'Curitibanos': {'lat': -27.2831, 'lon': -50.5842, 'regiao': 'Serrana'},
    'São Joaquim': {'lat': -28.2936, 'lon': -49.9317, 'regiao': 'Serrana'},
    'Correia Pinto': {'lat': -27.5850, 'lon': -50.3617, 'regiao': 'Serrana'},
    'Otacílio Costa': {'lat': -27.4819, 'lon': -50.1214, 'regiao': 'Serrana'},
    'Urupema': {'lat': -27.9558, 'lon': -49.8758, 'regiao': 'Serrana'},
    'Urubici': {'lat': -28.0150, 'lon': -49.5917, 'regiao': 'Serrana'},
    
    'Chapecó': {'lat': -27.1008, 'lon': -52.6153, 'regiao': 'Oeste Catarinense'},
    'Concórdia': {'lat': -27.2336, 'lon': -52.0231, 'regiao': 'Oeste Catarinense'},
    'Caçador': {'lat': -26.7753, 'lon': -51.0125, 'regiao': 'Oeste Catarinense'},
    'Videira': {'lat': -27.0083, 'lon': -51.1517, 'regiao': 'Oeste Catarinense'},
    'Fraiburgo': {'lat': -27.0269, 'lon': -50.9214, 'regiao': 'Oeste Catarinense'},
    'São Miguel do Oeste': {'lat': -26.7269, 'lon': -53.5186, 'regiao': 'Oeste Catarinense'},
    'Xanxerê': {'lat': -26.8747, 'lon': -52.4039, 'regiao': 'Oeste Catarinense'},
    'Joaçaba': {'lat': -27.1772, 'lon': -51.5033, 'regiao': 'Oeste Catarinense'},
    'Maravilha': {'lat': -26.7617, 'lon': -53.1728, 'regiao': 'Oeste Catarinense'},
    'Pinhalzinho': {'lat': -26.8458, 'lon': -52.9933, 'regiao': 'Oeste Catarinense'},
    'Monte Carlo': {'lat': -27.2236, 'lon': -50.9819, 'regiao': 'Oeste Catarinense'},
    'Campos Novos': {'lat': -27.4019, 'lon': -51.2253, 'regiao': 'Oeste Catarinense'},
    'Seara': {'lat': -27.1519, 'lon': -52.3117, 'regiao': 'Oeste Catarinense'},
    'São Lourenço do Oeste': {'lat': -26.3592, 'lon': -52.8517, 'regiao': 'Oeste Catarinense'},
    'Guarujá do Sul': {'lat': -26.3853, 'lon': -53.5328, 'regiao': 'Oeste Catarinense'},
    'Romelândia': {'lat': -26.5058, 'lon': -53.3153, 'regiao': 'Oeste Catarinense'},
    
    'Curitiba': {'lat': -25.4284, 'lon': -49.2733, 'regiao': 'Outro Estado (PR)'},
    'Campo Largo': {'lat': -25.4597, 'lon': -49.5275, 'regiao': 'Outro Estado (PR)'},
    'São Paulo': {'lat': -23.5505, 'lon': -46.6333, 'regiao': 'Outro Estado (SP)'},
    'Porto Alegre': {'lat': -30.0346, 'lon': -51.2177, 'regiao': 'Outro Estado (RS)'},
}

def remove_accents(text):
    if not isinstance(text, str):
        return ''
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)]).lower().strip()

def normalize_city(raw_name):
    if not isinstance(raw_name, str) or not raw_name.strip():
        return 'Não informado'
    
    s = raw_name.strip()
    s = re.sub(r'[\r\n\t]+', ' ', s)
    s = re.sub(r'\s*[/,-]?\s*SC\b.*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s*[/,-]?\s*Santa Catarina\b.*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s*[/,-]?\s*Brasil\b.*', '', s, flags=re.IGNORECASE)
    s = s.strip()
    
    slug = remove_accents(s)
    slug = re.sub(r'[^a-z0-9\s]', '', slug).strip()
    
    synonyms = {
        'florianopolis': 'Florianópolis',
        'florianoplis': 'Florianópolis',
        'floripa': 'Florianópolis',
        'fln': 'Florianópolis',
        'tapera': 'Florianópolis',
        'tapera da base': 'Florianópolis',
        'sao jose': 'São José',
        's jose': 'São José',
        'palhoca': 'Palhoça',
        'biguacu': 'Biguaçu',
        'criciuma': 'Criciúma',
        'joinville': 'Joinville',
        'brusque': 'Brusque',
        'busque': 'Brusque',
        'itapoa': 'Itapoá',
        'barra velha': 'Barra Velha',
        'sao francisco do sul': 'São Francisco do Sul',
        'sao chico': 'São Francisco do Sul',
        'sao francisco': 'São Francisco do Sul',
        'balneario balance': 'Balneário Camboriú',
        'balneario camboriu': 'Balneário Camboriú',
        'balneario': 'Balneário Camboriú',
        'bc': 'Balneário Camboriú',
        'camboriu': 'Camboriú',
        'navegantes': 'Navegantes',
        'ararangua': 'Araranguá',
        'imbituba': 'Imbituba',
        'itajai': 'Itajaí',
        'fraiburgo': 'Fraiburgo',
        'friburgo': 'Fraiburgo',
        'passo de torres': 'Passo de Torres',
        'guabiruba': 'Guabiruba',
        'jaragua do sul': 'Jaraguá do Sul',
        'jaragua': 'Jaraguá do Sul',
        'lages': 'Lages',
        'chapeco': 'Chapecó',
        'nova veneza': 'Nova Veneza',
        'itapema': 'Itapema',
        'monte carlo': 'Monte Carlo',
        'blumenau': 'Blumenau',
        'tubarao': 'Tubarão',
        'cacador': 'Caçador',
        'concordia': 'Concórdia',
        'gaspar': 'Gaspar',
        'laguna': 'Laguna',
        'sombrio': 'Sombrio',
        'tijucas': 'Tijucas',
        'videira': 'Videira',
        'porto belo': 'Porto Belo',
        'santo amaro da imperatriz': 'Santo Amaro da Imperatriz',
        'santo amaro': 'Santo Amaro da Imperatriz',
        'sao bento do sul': 'São Bento do Sul',
        'governador celso ramos': 'Governador Celso Ramos',
        'icara': 'Içara',
        'urussanga': 'Urussanga',
        'canelinha': 'Canelinha',
        'mafra': 'Mafra',
        'curitibanos': 'Curitibanos',
        'sao joaquim': 'São Joaquim',
        'penha': 'Penha',
        'picarras': 'Balneário Piçarras',
        'balneario picarras': 'Balneário Piçarras',
        'rio do sul': 'Rio do Sul',
        'forquilhinha': 'Forquilhinha',
        'turvo': 'Turvo',
        'praia grande': 'Praia Grande',
        'garopaba': 'Garopaba',
        'sao miguel do oeste': 'São Miguel do Oeste',
        'xanxere': 'Xanxerê',
        'joacaba': 'Joaçaba',
        'maravilha': 'Maravilha',
        'pinhalzinho': 'Pinhalzinho',
        'braco do norte': 'Braço do Norte',
        'orleans': 'Orleans',
        'gravatal': 'Gravatal',
        'termas do gravatal': 'Gravatal',
        'sideropolis': 'Siderópolis',
        'morro da fumaca': 'Morro da Fumaça',
        'guaramirim': 'Guaramirim',
        'corupa': 'Corupá',
        'schroeder': 'Schroeder',
        'campo alegre': 'Campo Alegre',
        'papanduva': 'Papanduva',
        'botuvera': 'Botuverá',
        'agrolandia': 'Agrolândia',
        'agronomica': 'Agronômica',
        'aurora': 'Aurora',
        'trombudo central': 'Trombudo Central',
        'guaruja do sul': 'Guarujá do Sul',
        'romelandia': 'Romelândia',
        'curitiba': 'Curitiba',
        'campo largo': 'Campo Largo',
        'porto alegre': 'Porto Alegre',
        'sao paulo': 'São Paulo',
    }
    
    for key, std_name in synonyms.items():
        if slug == key or slug.startswith(key + ' ') or slug.endswith(' ' + key):
            return std_name
            
    for std_name in CITIES_DB.keys():
        if remove_accents(std_name) == slug:
            return std_name
            
    return s.title()

def get_city_coords_and_region(city_name):
    if city_name in CITIES_DB:
        info = CITIES_DB[city_name]
        return info['lat'], info['lon'], info['regiao']
    return None, None, 'Outras Regiões / Não Identificado'

def normalize_age_bracket(val):
    if pd.isna(val) or not str(val).strip() or str(val).strip().lower() in ['nan', 'none', '']:
        return 'Não informado'
    s = str(val).strip()
    
    if 'menor' in s.lower() or '<' in s or '17' in s:
        return 'Menor de 18 anos'
    if '18' in s and '25' in s:
        return '18 a 25 anos'
    if '26' in s and '35' in s:
        return '26 a 35 anos'
    if '36' in s and '40' in s:
        return '36 a 40 anos'
    if '41' in s and '45' in s:
        return '41 a 45 anos'
    if '46' in s and '55' in s:
        return '46 a 55 anos'
    if '56' in s and '65' in s:
        return '56 a 65 anos'
    if '66' in s and '75' in s:
        return '66 a 75 anos'
    if '76' in s and '85' in s:
        return '76 a 85 anos'
    if '85' in s or '86' in s or 'mais' in s.lower():
        return 'Mais de 85 anos'
        
    return s

def normalize_race(val):
    if pd.isna(val) or not str(val).strip():
        return 'Não informado'
    s = str(val).strip().capitalize()
    slug = remove_accents(s)
    if 'branc' in slug:
        return 'Branca'
    if 'pard' in slug or 'maren' in slug or 'moren' in slug:
        return 'Parda'
    if 'pret' in slug or 'negr' in slug:
        return 'Preta'
    if 'indig' in slug:
        return 'Indígena'
    if 'amar' in slug or 'orient' in slug:
        return 'Amarela'
    if 'prefiro' in slug or 'nao' in slug:
        return 'Prefiro não informar'
    return s

def normalize_gender(val):
    if pd.isna(val) or not str(val).strip():
        return 'Não informado'
    s = str(val).strip()
    slug = remove_accents(s)
    if 'cis' in slug or slug == 'mulher' or slug == 'feminino' or slug == 'mulher normal' or slug == 'mulher mesmo' or slug == 'mulher heterossexual':
        return 'Mulher Cisgênero'
    if 'trans' in slug or 'travesti' in slug:
        return 'Mulher Trans / Travesti'
    if 'binari' in slug or 'nb' in slug:
        return 'Não-binária'
    if 'prefiro' in slug or 'nao' in slug or '?' in slug:
        return 'Prefiro não informar'
    return 'Outra'

def normalize_marital_status(val):
    if pd.isna(val) or not str(val).strip():
        return 'Não informado'
    s = str(val).strip()
    slug = remove_accents(s)
    if 'solteir' in slug:
        return 'Solteira'
    if 'casad' in slug:
        return 'Casada'
    if 'estavel' in slug or 'uniao' in slug or 'amasiad' in slug or 'junto' in slug or 'conviv' in slug:
        return 'União Estável'
    if 'divorc' in slug:
        return 'Divorciada'
    if 'separad' in slug or 'desquitad' in slug:
        return 'Separada'
    if 'viuv' in slug:
        return 'Viúva'
    return 'Outro / Não informado'

def normalize_area(val):
    if pd.isna(val) or not str(val).strip():
        return 'Não informado'
    s = str(val).strip().capitalize()
    slug = remove_accents(s)
    if 'rural' in slug:
        return 'Zona rural'
    if 'urban' in slug:
        return 'Zona urbana'
    return 'Não informado'

def normalize_agressor_profile(val):
    if pd.isna(val) or not str(val).strip():
        return 'Não informado'
    s = remove_accents(str(val))
    if 'ex-' in s or 'ex ' in s or 'excompanheir' in s or 'exmarido' in s or 'exnamorad' in s:
        return 'Ex-companheiro(a)'
    if 'companheir' in s or 'marido' in s or 'namorad' in s or 'espos' in s or 'conjuge' in s:
        return 'Companheiro(a) atual'
    if 'filh' in s or 'mae' in s or 'pai' in s or 'net' in s or 'prim' in s or 'ti' in s or 'sogr' in s or 'parent' in s:
        return 'Familiar (Filho, Mãe, etc.)'
    if 'vizinh' in s or 'conhecid' in s or 'amig' in s:
        return 'Conhecido(a) / Vizinho(a)'
    return 'Outro / Não informado'

def extract_violence_types(text):
    """
    Classifica com rigor os 5 tipos canônicos de violência da Lei Maria da Penha (Art. 7º):
    1. Violência Psicológica
    2. Violência Física
    3. Violência Patrimonial
    4. Violência Moral
    5. Violência Sexual
    """
    if pd.isna(text) or not isinstance(text, str):
        return {
            'viol_psicologica': False,
            'viol_fisica': False,
            'viol_patrimonial': False,
            'viol_moral': False,
            'viol_sexual': False,
            'medida_protetiva': False,
            'demanda_familia_guarda_pensao': False,
            'tipos_violencia_5': []
        }
        
    s = remove_accents(text).lower()
    
    is_psico = bool(re.search(r'(psicolog|verbal|ofens|ofend|humilh|xing|gritos|gritar|deboch|persegui|control|terror|tortura psic|abuso psic|destruicao emoc|ameac|matar|morte|arma|faca|tiro|revolver|vai me matar|medo de morrer|perigo|stalking|vigi|ligacoes sem parar|mensagens sem parar|chantag|manipul|diminu|inferno|me proibe|isol|me perturba|nao me deixa em paz)', s))
    is_fisica = bool(re.search(r'(fisic|agred|agress|bateu|bater|machuc|soco|tapa|empurr|puxao|puxou|cabelo|esgan|enforc|hematoma|marcas|espanc|lesao|estape|paulada|chute|chutou|coronhada|facada|mord|arranh|queimad|violencia corporal|bofetada|atropel)', s))
    is_patrimonial = bool(re.search(r'(patrimonial|bens|dinheiro|financeir|cartao|conta|quebrou|destruiu|estragou|roubou|tomou|furto|reteve|bloqueou|veiculo|carro|moto|celular quebrou|sem renda|corte|sustento|documento|tomou meus|destruicao de bens|queimar|vendeu minhas coisas|prejuizo financeiro)', s))
    is_moral = bool(re.search(r'(moral|caluni|difam|injuri|expos|mentira|acusacao falsa|reputacao|fotos intimas|vazou|difamando|falsa acusacao|denegri|honra|difamatoria|caluniosa|falsas acusacoes)', s))
    is_sexual = bool(re.search(r'(sexual|abuso sexual|estupr|forcada|relacao forcada|tocar|passar a mao|assedio|violencia sexual|forcou a ter|forcar a ter|ato libidinoso|importunacao sexual)', s))
    
    is_protetiva = bool(re.search(r'(medida protetiva|protetiva|maria da penha|descumpr|afastamento|intima|boletim|b\.o|delegacia|oficial de justica)', s))
    is_familia = bool(re.search(r'(pensao|alimento|guarda|filh|filha|crianca|menor|divorcio|partilha|visita|paternidade|convivencia)', s))
    
    tipos_5 = []
    if is_psico: tipos_5.append('Violência Psicológica')
    if is_fisica: tipos_5.append('Violência Física')
    if is_patrimonial: tipos_5.append('Violência Patrimonial')
    if is_moral: tipos_5.append('Violência Moral')
    if is_sexual: tipos_5.append('Violência Sexual')
    
    return {
        'viol_psicologica': is_psico,
        'viol_fisica': is_fisica,
        'viol_patrimonial': is_patrimonial,
        'viol_moral': is_moral,
        'viol_sexual': is_sexual,
        'medida_protetiva': is_protetiva,
        'demanda_familia_guarda_pensao': is_familia,
        'tipos_violencia_5': tipos_5
    }

def extract_referral_channel(text):
    if pd.isna(text) or not isinstance(text, str) or not text.strip():
        return 'Não informado'
    s = remove_accents(text)
    
    if re.search(r'\b(cras|creas|assistencia social|assistente social|cras / creas)\b', s):
        return 'CRAS / CREAS / Assistência Social'
    if re.search(r'\b(forum|vara|juiz|justica|tribunal|judiciario|oficial de justica|promotoria|ministerio publico)\b', s):
        return 'Poder Judiciário / Fórum / Vara'
    if re.search(r'\b(delegacia|policia|boletim|b\.o|bo|dpcami|boletim de ocorrencia)\b', s):
        return 'Delegacia / Polícia / Boletim de Ocorrência'
    if re.search(r'\b(defensoria|oab|advogad|defensora|defensor)\b', s):
        return 'Defensoria Pública / OAB'
    if re.search(r'\b(instagram|rede social|facebook|google|internet|site|tiktok|whatsapp)\b', s):
        return 'Redes Sociais / Internet'
    if re.search(r'\b(amig|familiar|conhecid|indicac|mae|prima|vizinh|irma|parente|colega)\b', s):
        return 'Indicação (Amigos/Familiares)'
    if re.search(r'\b(caps|posto|saude|hospital|medico|psicolog)\b', s):
        return 'Saúde / CAPS / Posto'
        
    return 'Outros / Indicação Direta'

def mask_name(val):
    if not isinstance(val, str) or not val.strip():
        return '***'
    parts = val.strip().split()
    if len(parts) == 1:
        return parts[0][0].upper() + '***'
    return ' '.join([p[0].upper() + '.' for p in parts if p])

def mask_cpf(val):
    if pd.isna(val) or not str(val).strip():
        return '***'
    digits = re.sub(r'\D', '', str(val))
    if len(digits) >= 11:
        return f'***.{digits[3:6]}.{digits[6:9]}-**'
    return '***.***.***-**'

def mask_rg(val):
    if pd.isna(val) or not str(val).strip():
        return '***'
    return '***.***-**'

def mask_phone(val):
    if pd.isna(val) or not str(val).strip():
        return '***'
    digits = re.sub(r'\D', '', str(val))
    if len(digits) >= 10:
        return f'({digits[:2]}) 9****-{digits[-4:]}'
    return '(**) 9****-****'

def mask_email(val):
    if not isinstance(val, str) or '@' not in val:
        return '***'
    user, domain = val.split('@', 1)
    if len(user) <= 2:
        masked_user = user[0] + '***'
    else:
        masked_user = user[:2] + '***' + user[-1]
    return f'{masked_user}@{domain}'

def match_column(col_name):
    c = remove_accents(str(col_name))
    
    if re.search(r'\b(carimbo|timestamp|data/hora|data_hora)\b', c) or c.startswith('data de atendimento'):
        return 'data_hora'
    if re.search(r'\bnome\b', c):
        return 'nome'
    if re.search(r'\b(celular|whatsapp)\b', c):
        return 'celular'
    if re.search(r'\b(fixo|telefone fixo)\b', c):
        return 'telefone_fixo'
    if re.search(r'\b(e-mail|email)\b', c):
        return 'email'
    if re.search(r'\b(nascimento|data de nascimento)\b', c):
        return 'data_nascimento'
    if re.search(r'\bcpf\b', c):
        return 'cpf'
    if re.search(r'\brg\b', c):
        return 'rg'
    if re.search(r'\b(faixa etaria|faixa_etaria)\b', c) or (re.search(r'\bidade\b', c) and 'identidade' not in c and 'cidade' not in c):
        return 'faixa_etaria'
    if re.search(r'\b(estado civil|estado_civil)\b', c):
        return 'estado_civil'
    if re.search(r'\b(racial|raca|etnia)\b', c) or re.search(r'\bcor\b', c):
        return 'raca_cor'
    if re.search(r'\b(genero|identidade de genero)\b', c):
        return 'identidade_genero'
    if re.search(r'\b(endereco|logradouro)\b', c):
        return 'endereco'
    if re.search(r'\b(municipio|cidade)\b', c):
        return 'municipio'
    if re.search(r'\b(tipo de area|zona)\b', c):
        return 'tipo_area'
    if re.search(r'\b(fatos|violencia sofrida|relato|conte resumidamente|tipo da violencia)\b', c):
        return 'relato_fatos'
    if re.search(r'\b(agressor|agressora|perfil)\b', c):
        return 'perfil_agressor'
    if re.search(r'\b(conheceu|como conheceu|forma conheceu)\b', c):
        return 'como_conheceu'
        
    return None

def process_single_dataframe(df, source_file, sheet_name):
    col_mapping = {}
    used_canonicals = set()
    
    for col in df.columns:
        canonical = match_column(col)
        if canonical and canonical not in used_canonicals:
            col_mapping[col] = canonical
            used_canonicals.add(canonical)
            
    df_renamed = df.rename(columns=col_mapping)
    
    expected_cols = [
        'data_hora', 'nome', 'celular', 'telefone_fixo', 'email', 
        'data_nascimento', 'cpf', 'rg', 'faixa_etaria', 'estado_civil', 
        'raca_cor', 'identidade_genero', 'endereco', 'municipio', 
        'tipo_area', 'relato_fatos', 'perfil_agressor', 'como_conheceu'
    ]
    
    for ec in expected_cols:
        if ec not in df_renamed.columns:
            df_renamed[ec] = np.nan
            
    res = df_renamed[expected_cols].copy()
    res['fonte_arquivo'] = source_file
    res['fonte_aba'] = str(sheet_name)
    
    res = res.dropna(subset=['nome', 'relato_fatos', 'data_hora'], how='all')
    return res

def load_data_from_excel(file_source, filename='Planilha'):
    dfs = []
    try:
        if hasattr(file_source, 'seek'):
            file_source.seek(0)
        xl = pd.ExcelFile(file_source)
        for sheet in xl.sheet_names:
            if 'atend' in remove_accents(sheet) or 'peti' in remove_accents(sheet):
                continue
            try:
                df = xl.parse(sheet)
                if df is not None and not df.empty:
                    df_proc = process_single_dataframe(df, filename, sheet)
                    if not df_proc.empty:
                        dfs.append(df_proc)
            except Exception as e:
                print(f'Erro ao processar aba {sheet} de {filename}: {e}')
    except Exception as e:
        print(f'Erro ao abrir Excel {filename}: {e}')
        
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()

def load_all_data(folder_path='.', uploaded_files=None):
    all_dfs = []
    search_dirs = [folder_path]
    dados_subfolder = os.path.join(folder_path, 'dados')
    if os.path.exists(dados_subfolder) and os.path.isdir(dados_subfolder):
        search_dirs.append(dados_subfolder)
        
    for sdir in search_dirs:
        patterns = [os.path.join(sdir, '*.xlsx'), os.path.join(sdir, '*.xls')]
        for pat in patterns:
            for file_path in glob.glob(pat):
                fname = os.path.basename(file_path)
                if fname.startswith('~$') or 'backup' in fname.lower():
                    continue
                df_file = load_data_from_excel(file_path, fname)
                if not df_file.empty:
                    all_dfs.append(df_file)
                    
    if uploaded_files:
        for uf in uploaded_files:
            fname = uf.name
            if fname.startswith('~$') or 'backup' in fname.lower():
                continue
            df_up = load_data_from_excel(uf, fname)
            if not df_up.empty:
                all_dfs.append(df_up)
                
    if not all_dfs:
        return pd.DataFrame()
        
    combined = pd.concat(all_dfs, ignore_index=True)
    if 'data_hora' in combined.columns and combined['data_hora'].dropna().count() > 0:
        combined = combined.drop_duplicates(subset=['data_hora', 'municipio', 'faixa_etaria', 'relato_fatos'], keep='first')
    else:
        combined = combined.drop_duplicates(keep='first')

    combined = enrich_dataframe(combined)

    # Considerar apenas registros até 31/08/2026
    if 'data_hora' in combined.columns:
        combined = combined[
            combined['data_hora'].isna() | (combined['data_hora'] <= DATA_CUTOFF)
        ].copy()

    return combined

def enrich_dataframe(df):
    if df.empty:
        return df
        
    df = df.copy()
    
    # 1. Tratar Datas e Dias da Semana Reais de Envio do Formulário pelas Mulheres
    df['data_hora'] = pd.to_datetime(df['data_hora'], errors='coerce')
    df['data'] = df['data_hora'].dt.date
    df['ano'] = df['data_hora'].dt.year
    df['mes'] = df['data_hora'].dt.month
    df['mes_ano'] = df['data_hora'].dt.strftime('%Y-%m')
    df['hora'] = df['data_hora'].dt.hour
    
    dias_map = {
        0: 'Segunda-feira',
        1: 'Terça-feira',
        2: 'Quarta-feira',
        3: 'Quinta-feira',
        4: 'Sexta-feira',
        5: 'Sábado',
        6: 'Domingo'
    }
    df['dia_semana'] = df['data_hora'].dt.dayofweek.map(dias_map)
    
    df['municipio'] = df['municipio'].apply(normalize_city)
    df['faixa_etaria'] = df['faixa_etaria'].apply(normalize_age_bracket)
    df['raca_cor'] = df['raca_cor'].apply(normalize_race)
    df['identidade_genero'] = df['identidade_genero'].apply(normalize_gender)
    df['estado_civil'] = df['estado_civil'].apply(normalize_marital_status)
    df['tipo_area'] = df['tipo_area'].apply(normalize_area)
    df['perfil_agressor_rotulo'] = df['perfil_agressor'].apply(normalize_agressor_profile)
    df['canal_origem'] = df['como_conheceu'].apply(extract_referral_channel)
    
    coords_regions = [get_city_coords_and_region(m) for m in df['municipio']]
    df['lat'] = [cr[0] for cr in coords_regions]
    df['lon'] = [cr[1] for cr in coords_regions]
    df['regiao_sc'] = [cr[2] for cr in coords_regions]
    
    # 5 Tipos Canônicos de Violência da Lei Maria da Penha
    viol_extractions = [extract_violence_types(f) for f in df['relato_fatos']]
    df['viol_psicologica'] = [v['viol_psicologica'] for v in viol_extractions]
    df['viol_fisica'] = [v['viol_fisica'] for v in viol_extractions]
    df['viol_patrimonial'] = [v['viol_patrimonial'] for v in viol_extractions]
    df['viol_moral'] = [v['viol_moral'] for v in viol_extractions]
    df['viol_sexual'] = [v['viol_sexual'] for v in viol_extractions]
    
    # Contextos adicionais
    df['medida_protetiva'] = [v['medida_protetiva'] for v in viol_extractions]
    df['demanda_familia_guarda_pensao'] = [v['demanda_familia_guarda_pensao'] for v in viol_extractions]
    
    # Lista e contagem estrita dos 5 tipos de violência
    df['tipos_violencia_lista'] = [v['tipos_violencia_5'] for v in viol_extractions]
    df['qtd_violencias'] = [len(v['tipos_violencia_5']) for v in viol_extractions]
    df['violencias_rotulo'] = df['tipos_violencia_lista'].apply(lambda x: ', '.join(x) if x else 'Não especificada')
    
    df['nome_mascarado'] = df['nome'].apply(mask_name)
    df['cpf_mascarado'] = df['cpf'].apply(mask_cpf)
    df['rg_mascarado'] = df['rg'].apply(mask_rg)
    df['celular_mascarado'] = df['celular'].apply(mask_phone)
    df['email_mascarado'] = df['email'].apply(mask_email)
    
    return df

def categorize_atendimento_modalidade(val):
    if not val or pd.isna(val):
        return 'Outros'
    s = str(val).lower()
    if 'telefone' in s:
        return 'Atendimento Telefônico'
    if 'vídeo' in s or 'video' in s:
        return 'Atendimento por Vídeo'
    if 'whatsapp' in s:
        return 'WhatsApp'
    if 'e-mail' in s or 'email' in s:
        return 'E-mail'
    if 'presencial' in s:
        return 'Atendimento Presencial'
    if 'encaminhamento' in s:
        return 'Encaminhamento Formal'
    if 'petição' in s or 'peticao' in s or 'mpu' in s:
        return 'Petição / Demanda Jurídica'
    if 'contato' in s or 'conversa' in s or 'reunião' in s or 'reuniao' in s:
        return 'Articulação de Rede / Órgãos'
    return 'Atendimento Geral'

def load_atendimentos_from_excel(file_source, filename='Planilha'):
    try:
        if hasattr(file_source, 'seek'):
            file_source.seek(0)
        xl = pd.ExcelFile(file_source)
        sheet_atend = None
        for s in xl.sheet_names:
            if 'atend' in remove_accents(s):
                sheet_atend = s
                break
                
        if not sheet_atend:
            return pd.DataFrame()
            
        df_raw = xl.parse(sheet_atend, header=None)
        if df_raw.empty or df_raw.shape[1] < 2:
            return pd.DataFrame()
            
        df = pd.DataFrame()
        df['data_raw'] = df_raw.iloc[:, 0]
        df['modalidade_raw'] = df_raw.iloc[:, 1]
        df['responsavel'] = df_raw.iloc[:, 2] if df_raw.shape[1] > 2 else 'Equipe'
        
        df = df.dropna(subset=['data_raw', 'modalidade_raw', 'responsavel'], how='all').copy()
        df = df[df['responsavel'].astype(str).str.strip().str.lower() != 'pendente'].copy()
        
        df['data'] = pd.to_datetime(df['data_raw'], errors='coerce')
        df['data'] = df['data'].ffill()
        df['data_apenas'] = df['data'].dt.date
        df['ano'] = df['data'].dt.year
        df['mes'] = df['data'].dt.month
        df['mes_ano'] = df['data'].dt.strftime('%Y-%m')
        
        dias_map = {0: 'Segunda-feira', 1: 'Terça-feira', 2: 'Quarta-feira', 3: 'Quinta-feira', 4: 'Sexta-feira', 5: 'Sábado', 6: 'Domingo'}
        df['dia_semana'] = df['data'].dt.dayofweek.map(dias_map)
        
        df['modalidade'] = df['modalidade_raw'].astype(str).str.strip()
        df['categoria_modalidade'] = df['modalidade'].apply(categorize_atendimento_modalidade)
        df['responsavel'] = df['responsavel'].astype(str).str.strip().replace({'nan': 'Não informado', 'None': 'Não informado'})
        
        df['fonte_arquivo'] = filename
        df['fonte_aba'] = sheet_atend
        return df
    except Exception as e:
        print(f"Erro ao carregar atendimentos de {filename}: {e}")
        return pd.DataFrame()

def load_atendimentos_data(folder_path='.', uploaded_files=None):
    all_dfs = []
    search_dirs = [folder_path]
    dados_subfolder = os.path.join(folder_path, 'dados')
    if os.path.exists(dados_subfolder) and os.path.isdir(dados_subfolder):
        search_dirs.append(dados_subfolder)
        
    for sdir in search_dirs:
        patterns = [os.path.join(sdir, '*.xlsx'), os.path.join(sdir, '*.xls')]
        for pat in patterns:
            for file_path in glob.glob(pat):
                fname = os.path.basename(file_path)
                if fname.startswith('~$') or 'backup' in fname.lower():
                    continue
                df_at = load_atendimentos_from_excel(file_path, fname)
                if not df_at.empty:
                    all_dfs.append(df_at)
                    
    if uploaded_files:
        for uf in uploaded_files:
            fname = uf.name
            if fname.startswith('~$') or 'backup' in fname.lower():
                continue
            df_at = load_atendimentos_from_excel(uf, fname)
            if not df_at.empty:
                all_dfs.append(df_at)
                
    if not all_dfs:
        return pd.DataFrame()
        
    combined = pd.concat(all_dfs, ignore_index=True)

    # Considerar apenas atendimentos até 31/08/2026
    if 'data' in combined.columns:
        combined = combined[
            combined['data'].isna() | (combined['data'] <= DATA_CUTOFF)
        ].copy()

    return combined

def categorize_peticao_tipo(val):
    if not val or pd.isna(val):
        return 'Outras Petições'
    s = str(val).lower()
    if 'pedido de mpu' in s or 'pedido incidental de mpu' in s:
        return 'Pedido de MPU (Inicial / Incidental)'
    if 'descumprimento' in s:
        return 'Descumprimento de MPU'
    if 'habilita' in s:
        return 'Pedido de Habilitação'
    if 'revoga' in s:
        return 'Revogação de MPU'
    if 'agravo' in s or 'recurso' in s or 'embargos' in s:
        return 'Recursos / Embargos'
    if 'intermedi' in s:
        return 'Petição Intermediária'
    if 'diversas' in s:
        return 'Petições Diversas'
    return 'Outras Petições'

def load_peticoes_from_excel(file_source, filename='Planilha'):
    try:
        if hasattr(file_source, 'seek'):
            file_source.seek(0)
        xl = pd.ExcelFile(file_source)
        sheet_pet = None
        for s in xl.sheet_names:
            if 'peti' in remove_accents(s):
                sheet_pet = s
                break
                
        if not sheet_pet:
            return pd.DataFrame()
            
        df_raw = xl.parse(sheet_pet, skiprows=2)
        if df_raw.empty or df_raw.shape[1] < 2:
            return pd.DataFrame()
            
        df = pd.DataFrame()
        df['mes_nome'] = df_raw.iloc[:, 0].astype(str).str.strip()
        df['tipo_peticao'] = df_raw.iloc[:, 1].astype(str).str.strip()
        df['data_protocolo'] = pd.to_datetime(df_raw.iloc[:, 3], errors='coerce') if df_raw.shape[1] > 3 else pd.NaT
        
        df = df[~df['mes_nome'].isin(['nan', 'None', '', 'Mês'])].copy()
        df = df[~df['tipo_peticao'].isin(['nan', 'None', '', 'Petição'])].copy()
        
        df['categoria_peticao'] = df['tipo_peticao'].apply(categorize_peticao_tipo)
        
        meses_ordem = {
            'janeiro': 1, 'fevereiro': 2, 'março': 3, 'marco': 3,
            'abril': 4, 'maio': 5, 'junho': 6, 'julho': 7,
            'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
        }
        df['mes_num'] = df['mes_nome'].apply(lambda m: meses_ordem.get(remove_accents(str(m)), 0))
        df['mes_ano'] = df.apply(
            lambda r: f"2026-{r['mes_num']:02d}" if r['mes_num'] > 0 else "2026-N/D", axis=1
        )
        
        df['fonte_arquivo'] = filename
        df['fonte_aba'] = sheet_pet
        return df
    except Exception as e:
        print(f"Erro ao carregar petições de {filename}: {e}")
        return pd.DataFrame()

def load_peticoes_data(folder_path='.', uploaded_files=None):
    all_dfs = []
    search_dirs = [folder_path]
    dados_subfolder = os.path.join(folder_path, 'dados')
    if os.path.exists(dados_subfolder) and os.path.isdir(dados_subfolder):
        search_dirs.append(dados_subfolder)
        
    for sdir in search_dirs:
        patterns = [os.path.join(sdir, '*.xlsx'), os.path.join(sdir, '*.xls')]
        for pat in patterns:
            for file_path in glob.glob(pat):
                fname = os.path.basename(file_path)
                if fname.startswith('~$') or 'backup' in fname.lower():
                    continue
                df_pt = load_peticoes_from_excel(file_path, fname)
                if not df_pt.empty:
                    all_dfs.append(df_pt)
                    
    if uploaded_files:
        for uf in uploaded_files:
            fname = uf.name
            if fname.startswith('~$') or 'backup' in fname.lower():
                continue
            df_pt = load_peticoes_from_excel(uf, fname)
            if not df_pt.empty:
                all_dfs.append(df_pt)
                
    if not all_dfs:
        return pd.DataFrame()
        
    combined = pd.concat(all_dfs, ignore_index=True)
    return combined

def load_all_dashboard_data(folder_path='.', uploaded_files=None):
    df_forms = load_all_data(folder_path=folder_path, uploaded_files=uploaded_files)
    df_atend = load_atendimentos_data(folder_path=folder_path, uploaded_files=uploaded_files)
    df_pet = load_peticoes_data(folder_path=folder_path, uploaded_files=uploaded_files)
    return {
        'formularios': df_forms,
        'atendimentos': df_atend,
        'peticoes': df_pet
    }
