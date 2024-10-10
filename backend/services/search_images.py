import requests
import csv
import time

# Sua chave de API do Pexels
API_KEY = 'm8kSLAlR4urMeEI5QFBxaSewSozpxTDgTsF2NLMaAxUWy6H08EomOeRY'
BASE_URL = 'https://api.pexels.com/v1/search'
# Lista de tópicos ampliada, cobrindo várias áreas relacionadas à construção
SEARCH_QUERIES = [
    'construction tools', 'buildings', 'construction workers', 'heavy machinery',
    'construction site', 'architecture', 'cranes', 'building materials',
    'blueprints', 'scaffolding', 'safety equipment', 'demolition', 'excavation',
    'concrete', 'paving', 'bricks', 'roadwork', 'industrial buildings', 'power tools',
    'construction equipment', 'bulldozers', 'excavators', 'construction blueprints',
    'urban development', 'industrial design', 'construction management', 'hard hats',
    'renovation', 'construction cranes', 'engineering projects', 'plumbing tools',
    'electrical tools', 'masonry work', 'construction planning', 'building foundation',
    'insulation materials', 'land surveying', 'civil engineering', 'steel beams',
    'heavy lifting', 'construction safety', 'road construction', 'home building',
    'roofing', 'earthmoving equipment', 'land development', 'structural engineering',
    'urban construction', 'construction workers teamwork', 'construction progress',
    'asphalt paving', 'bridge construction', 'tower cranes'
]

RESULTS_PER_PAGE = 80  # máximo permitido por requisição
TOTAL_PHOTOS_DESIRED = 10000  # 10 mil fotos
total_photos = []

headers = {
    'Authorization': API_KEY
}


def fetch_photos(query, page):
    params = {
        'query': query,
        'per_page': RESULTS_PER_PAGE,
        'page': page
    }
    response = requests.get(BASE_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Erro ao buscar fotos para {query}: {response.status_code}')
        return None

# Função para coletar fotos de diferentes consultas


def collect_photos():
    for query in SEARCH_QUERIES:
        print(f"Buscando fotos para: {query}")
        # Distribui as requisições para cada consulta com base no total desejado
        for i in range(1, (TOTAL_PHOTOS_DESIRED // len(SEARCH_QUERIES)) // RESULTS_PER_PAGE + 2):
            result = fetch_photos(query, i)
            if result and 'photos' in result:
                photos = result['photos']
                for photo in photos:
                    # Adiciona a URL da imagem original
                    total_photos.append(photo['src']['original'])
                time.sleep(1)  # Atraso para evitar limites de taxa da API
            if len(total_photos) >= TOTAL_PHOTOS_DESIRED:
                return


# Coleta as fotos
collect_photos()

# Cria um arquivo CSV com as URLs das fotos
with open('fotos_construcao.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['URL'])
    for photo_url in total_photos:
        writer.writerow([photo_url])

print(f'Total de fotos coletadas: {len(total_photos)}')
