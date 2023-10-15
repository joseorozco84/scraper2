import requests
import lxml.html as html
import csv
from tqdm import tqdm

# Define the URL for Metacritic's root and the user agent header
url_root = 'https://www.metacritic.com'
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36'}

# XPATHs for scraping
XPATH_NAME = '//div[@class="c-productHero_title g-inner-spacing-bottom-medium g-outer-spacing-top-medium"]//text()'
XPATH_PUBLISHER = '//div[@class="c-gameDetails_Distributor u-flexbox u-flexbox-row"]//span[@class="g-outer-spacing-left-medium-fluid g-color-gray70 u-block"]//text()'
XPATH_GENRE = '//li[@class="c-genreList_item"]//span[@class="c-globalButton_label"]//text()'
XPATH_RATING = '//div[@class="c-siteReviewScore_background c-siteReviewScore_background-critic_large"]//text()'
XPATH_RELEASE_DATE = '//div[@class="c-gameDetails_ReleaseDate u-flexbox u-flexbox-row"]//span[@class="g-outer-spacing-left-medium-fluid g-color-gray70 u-block"]//text()'
XPATH_PLATFORMS = '//div[@class="c-gameDetails_Platforms u-flexbox u-flexbox-row"]//ul[@class="g-outer-spacing-left-medium-fluid"]//text()'
# XPATH_METASCORE = '//a[@class="c-ScoreCard_scoreContent_number"]//text()'
# XPATH_USERSCORE = '//a[@class="c-ScoreCard_scoreContent_number"]//text()'

# Read game links from the text file
with open('game_links_test.txt', 'r') as file:
    game_links = [line.strip() for line in file]

# Create a list to store the extracted data for each game
game_data_list = []

# Iterate through the game links and scrape data for each game
for game_page in tqdm(game_links):
    with requests.Session() as s:
        r = s.get(game_page, headers=header)
        home = r.content.decode('utf-8')
        parser = html.fromstring(home)

        name = parser.xpath(XPATH_NAME)[0].strip()
        publisher = parser.xpath(XPATH_PUBLISHER)[0].strip()
        genre = parser.xpath(XPATH_GENRE)[0].strip()
        rating = parser.xpath(XPATH_RATING)[0].strip()
        release_date = parser.xpath(XPATH_RELEASE_DATE)[0].strip()
        # metascore = parser.xpath(XPATH_METASCORE)[0].strip()
        # userscore = parser.xpath(XPATH_USERSCORE)[2].strip()
        platforms = [p.strip() for p in parser.xpath(XPATH_PLATFORMS)]

        # Store the extracted data in a dictionary
        game_data = {
            "name": name,
            "publisher": publisher,
            "genre": genre,
            "rating": rating,
            "release Date": release_date,
            # "metascore": metascore,
            # "userscore": userscore,
            "platforms": ", ".join(platforms)
        }

        # Append the game data to the list
        game_data_list.append(game_data)

# Define the CSV filename
csv_filename = "game_info.csv"

# Write the data for all games to the CSV file
with open(csv_filename, mode="w", newline="", encoding="utf-8") as csv_file:
    fieldnames = game_data_list[0].keys()
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(game_data_list)

print(f"Data for {len(game_data_list)} games has been saved to {csv_filename}")
