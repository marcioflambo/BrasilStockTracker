"""
Lista das principais ações brasileiras negociadas na B3
Atualizada com as principais empresas por setor
"""

BRAZILIAN_STOCKS = {
    "Bancos": {
        "ITUB4.SA": "Itaú Unibanco",
        "BBDC4.SA": "Bradesco",
        "BBAS3.SA": "Banco do Brasil",
        "SANB11.SA": "Santander Brasil",
        "BPAC11.SA": "BTG Pactual",
        "ITSA4.SA": "Itaúsa",
        "BBDC3.SA": "Bradesco ON",
        "ITUB3.SA": "Itaú Unibanco ON"
    },
    "Petróleo e Gás": {
        "PETR4.SA": "Petrobras",
        "PETR3.SA": "Petrobras ON",
        "PRIO3.SA": "PetroRio",
        "RECV3.SA": "Petro Rec",
        "UGPA3.SA": "Ultrapar"
    },
    "Mineração": {
        "VALE3.SA": "Vale",
        "CSNA3.SA": "CSN",
        "USIM5.SA": "Usiminas",
        "GGBR4.SA": "Gerdau",
        "GOAU4.SA": "Gerdau Met"
    },
    "Varejo": {
        "MGLU3.SA": "Magazine Luiza",
        "LREN3.SA": "Lojas Renner",
        "AMER3.SA": "Americanas",
        "VVAR3.SA": "Via Varejo",
        "CRFB3.SA": "Carrefour Brasil",
        "ASAI3.SA": "Assaí",
        "PCAR3.SA": "P.Açúcar-CBD"
    },
    "Alimentícias e Bebidas": {
        "ABEV3.SA": "Ambev",
        "JBSS3.SA": "JBS",
        "BRFS3.SA": "BRF",
        "SMTO3.SA": "São Martinho",
        "BEEF3.SA": "Minerva"
    },
    "Siderurgia": {
        "CSNA3.SA": "CSN",
        "USIM5.SA": "Usiminas",
        "GGBR4.SA": "Gerdau",
        "GOAU4.SA": "Gerdau Met"
    },
    "Telecomunicações": {
        "VIVT3.SA": "Telefônica Brasil",
        "TIMS3.SA": "TIM",
        "OIBR3.SA": "Oi"
    },
    "Energia Elétrica": {
        "ELET3.SA": "Eletrobras",
        "ELET6.SA": "Eletrobras PNB",
        "CPFE3.SA": "CPFL Energia",
        "EGIE3.SA": "Engie Brasil",
        "EQTL3.SA": "Equatorial",
        "CPLE6.SA": "Copel",
        "CMIG4.SA": "Cemig",
        "ENEV3.SA": "Eneva"
    },
    "Construção Civil": {
        "MRVE3.SA": "MRV",
        "CYRE3.SA": "Cyrela",
        "EVEN3.SA": "Even",
        "EZTC3.SA": "EZTec",
        "JHSF3.SA": "JHSF",
        "TCSA3.SA": "TecnoSolo"
    },
    "Papel e Celulose": {
        "SUZB3.SA": "Suzano",
        "KLBN11.SA": "Klabin Unit",
        "FIBR3.SA": "Fibria"
    },
    "Tecnologia": {
        "TOTS3.SA": "Totvs",
        "POSI3.SA": "Positivo",
        "LWSA3.SA": "Locaweb"
    },
    "Logística": {
        "RAIL3.SA": "Rumo",
        "LOGN3.SA": "Log-In",
        "STBP3.SA": "Santos Brasil"
    },
    "Saúde": {
        "RDOR3.SA": "Rede D'Or",
        "HAPV3.SA": "Hapvida",
        "QUAL3.SA": "Qualicorp",
        "FLRY3.SA": "Fleury",
        "DASA3.SA": "Dasa"
    },
    "Educação": {
        "COGN3.SA": "Cogna",
        "YDUQ3.SA": "Yduqs",
        "ANIM3.SA": "Ânima"
    },
    "Aviação": {
        "GOLL4.SA": "Gol",
        "AZUL4.SA": "Azul"
    },
    "Químicas": {
        "BRASKEM": "Braskem",
        "UNIP6.SA": "Unipar"
    }
}

def get_all_tickers():
    """Retorna lista de todos os tickers disponíveis"""
    all_tickers = []
    for sector_stocks in BRAZILIAN_STOCKS.values():
        all_tickers.extend(sector_stocks.keys())
    return sorted(list(set(all_tickers)))

def get_tickers_by_sector(sector):
    """Retorna tickers de um setor específico"""
    return list(BRAZILIAN_STOCKS.get(sector, {}).keys())

def get_sectors():
    """Retorna lista de setores disponíveis"""
    return list(BRAZILIAN_STOCKS.keys())

def search_stocks(query):
    """Busca ações por nome ou ticker"""
    query = query.upper()
    results = []
    
    for sector, stocks in BRAZILIAN_STOCKS.items():
        for ticker, name in stocks.items():
            if query in ticker.upper() or query in name.upper():
                results.append({
                    'ticker': ticker,
                    'name': name,
                    'sector': sector
                })
    
    return results

def get_stock_name(ticker):
    """Retorna o nome da empresa pelo ticker"""
    for sector_stocks in BRAZILIAN_STOCKS.values():
        if ticker in sector_stocks:
            return sector_stocks[ticker]
    return ticker.replace('.SA', '')

# Lista de ações mais populares para sugestões
POPULAR_STOCKS = [
    "ITUB4.SA", "PETR4.SA", "VALE3.SA", "BBDC4.SA", "ABEV3.SA",
    "MGLU3.SA", "ELET3.SA", "JBSS3.SA", "SUZB3.SA", "VIVT3.SA",
    "BRFS3.SA", "CSNA3.SA", "LREN3.SA", "RAIL3.SA", "USIM5.SA",
    "GGBR4.SA", "CPFE3.SA", "MRVE3.SA", "TOTS3.SA", "RDOR3.SA"
]