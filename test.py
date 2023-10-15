# importar las librerias
import requests
import lxml.html as html
from tqdm import tqdm
import concurrent.futures
import time

# inicializar variables y XPATH
url_root = 'https://www.metacritic.com'
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36'
}
XPATH_GAME_LIST = '//h3[@class="c-finderProductCard_titleHeading"]//span[2]//text()'
XPATH_LAST_PAGE = '//span[@class="c-navigationPagination_itemButtonContent u-flexbox u-flexbox-alignCenter u-flexbox-justifyCenter"]//text()'
XPATH_LINKS = '//div[@class="c-finderProductCard c-finderProductCard-game"]//@href'

# función para obtener la lista de links por pagina
def get_links(num_page):
    games_page = f'https://www.metacritic.com/browse/game/?releaseYearMin=1910&releaseYearMax=2023&page={num_page}'
    response = requests.get(games_page, headers=header)
    
    # Verificar si la página existe
    if response.status_code == 404:
        print(f'Página no encontrada: {games_page}')
        return None
    
    response.raise_for_status()
    home = response.text
    parser = html.fromstring(home)
    links = parser.xpath(XPATH_LINKS)

    return [url_root + link for link in links] # Retorna una lista de enlaces

# función principal
def main():
    # Obtener el número de la última página
    response = requests.get('https://www.metacritic.com/browse/game/?releaseYearMin=1910&releaseYearMax=2023&page=1', headers=header)
    response.raise_for_status()
    parser = html.fromstring(response.text)
    for_strip = parser.xpath(XPATH_LAST_PAGE)
    last_page = int(for_strip[2].strip().replace(',', ''))

    link_list = [] # Lista para almacenar los enlaces
    failed_links = []  # Lista para almacenar los enlaces que no se pudieron raspar

    # Utilizar ThreadPoolExecutor para realizar solicitudes concurrentes
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(get_links, n) for n in range(1, last_page + 1)]
        for n, future in tqdm(enumerate(concurrent.futures.as_completed(futures), 1), total=last_page, desc="...scraping urls"):
            result = future.result()
            if result:
                link_list.extend(result)
            else:
                failed_links.append(f'https://www.metacritic.com/browse/game/?releaseYearMin=1910&releaseYearMax=2023&page={n}')
            
            # Espera la finalización de las solicitudes
            time.sleep(0.01)

    # Guardar los enlaces en el archivo .txt
    with open('links.txt', 'w') as file:
        for link in link_list:
            file.write(f'{link}\n')

    # Guardar los enlaces que no se pudieron raspar en un archivo separado
    with open('failed_links.txt', 'w') as failed_file:
        for link in failed_links:
            failed_file.write(f'{link}\n')

if __name__ == "__main__":
    main()
