# importar librerias
import requests
import lxml.html as html
from tqdm import tqdm
import random
import aiohttp
import asyncio

# inicializar variables y XPATH
url_root = 'https://www.metacritic.com'
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36'}
XPATH_PLATFORM_LIST = '//div[@class="c-filterInput u-grid"]//div[@class="c-filterInput_content u-grid xh-highlight"]//span//text()'
XPATH_GAME_LIST = '//h3[@class="c-finderProductCard_titleHeading"]//span[2]//text()'
XPATH_LAST_PAGE = '//span[@class="c-navigationPagination_itemButtonContent u-flexbox u-flexbox-alignCenter u-flexbox-justifyCenter"]//text()'#'//*[@id="__layout"]/div/div[2]/div[1]/main/section/div[4]/span[2]/span[5]/span/span/span/text()'
XPATH_LINKS = '//div[@class="c-finderProductCard c-finderProductCard-game"]//@href' # hrefs a los juegos de UNA pagina


# funcion para obtener la ultima pagina de la lista de juegos


# funcion para obtener la lista de links por pagina
async def get_links(session, num_page):
    games_page = f'https://www.metacritic.com/browse/game/?releaseYearMin=1910&releaseYearMax=2023&page={num_page}'
    async with session.get(games_page, headers=header) as response:
        home = await response.text()
        parser = html.fromstring(home)   
        game_list = parser.xpath(XPATH_GAME_LIST)        
        #busca la ultima pagina
        links = parser.xpath(XPATH_LINKS)
        for n in range(len(game_list)):
            yield url_root + links[n]

# función para guardar los enlaces en un archivo .txt de manera asíncrona
async def save_links_to_file(link_list):
    with open('links.txt', 'w') as file:
        for x in link_list:
            file.writelines(f'{x}\n')

# función principal
async def main():
    async with aiohttp.ClientSession() as session:
        r = await session.get('https://www.metacritic.com/browse/game/?releaseYearMin=1910&releaseYearMax=2023&page=1', headers=header)
        home = await r.text()
        parser = html.fromstring(home)
        for_strip = parser.xpath(XPATH_LAST_PAGE)
        last_page = int(for_strip[2].strip().replace(',', '')) # stripea los espacios, la coma y lo convierte a entero

        link_list = []

        # recorre las páginas y scrapea los links
        for n in tqdm(range(1, last_page + 1), desc="...scraping urls"):
            async for link in get_links(session, n):  # Espera la finalización de las solicitudes
                link_list.append(link)
                
            # llama a la función para guardar los enlaces en el archivo .txt de manera asíncrona
            await save_links_to_file(link_list)

if __name__ == "__main__":
    asyncio.run(main())