import time
import requests
import logging
import random
import os
import requests
import pytz
from openai import OpenAI
from math import ceil
from bs4 import BeautifulSoup
from urllib.parse import quote
from datetime import datetime, timedelta
from db_config import get_connection
from BingImageCreator import ImageGen

auth_cookie = os.environ.get('BING_AUTH_COOKIE')

openai_api_key = os.environ.get('OPENAI_API_KEY')
if openai_api_key:
    client = OpenAI(api_key=openai_api_key)
else:
    raise EnvironmentError("OPENAI_API_KEY not found in environment variables")

logging.basicConfig(level=logging.DEBUG, filename='debug.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')


def generate_design(prompt):
    image_gen = ImageGen(auth_cookie=auth_cookie, auth_cookie_SRCHHPGUSR=auth_cookie)

    try:
        links = image_gen.get_images(prompt)
        return links
    except Exception as e:
        # Handle or log the exception as needed
        return None

def search_redbubble(query):
    try:
        # Encode the query for URL
        encoded_query = quote(query)
        url = f"https://www.redbubble.com/shop/?query={encoded_query}"

        # Set headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

        time.sleep(1)
        
        # Make a request to the URL
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code != 200:
            return f"Error: Received status code {response.status_code}", url

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')


        def contains_results(tag):
            return tag.name == 'span' and 'Results' in tag.text

        results_info = soup.find_all(contains_results)

        # Extract and return results and URL
        if results_info and results_info[0].text:
            logging.debug(f"{results_info[0].text.strip()} for {query}")
            return results_info[0].text.strip(), url
        else:
            logging.debug(f"No results available for {query}")
            # Return "0 Results" if results info is not found or is empty
            return "0 Results", url

    except Exception as e:
        return f"An error occurred: {e}", url

def find_top_tv_shows():
    logging.debug("Function start")
    conn = None  # Initialize conn outside of the try block
    try:
        conn = get_connection()
        logging.debug("Database connection established")

        cur = conn.cursor()

        # Check the last updated time
        logging.debug("Checking last update time")
        cur.execute("SELECT MAX(last_updated) FROM top_tv_shows")
        last_updated_result = cur.fetchone()
        last_updated = last_updated_result[0] if last_updated_result else None

        if last_updated and datetime.now() - last_updated < timedelta(hours=48):
            # Data is fresh, fetch from database
            cur.execute("SELECT title, href FROM top_tv_shows ORDER BY id")
            shows = cur.fetchall()
            logging.debug("Fetching data from database")
        else:
            # Data is old or not present, scrape the website
            scraped_shows = scrape_top_tv_shows()  # Scrape function to be implemented
            logging.debug("Scraping new data")

            # Clear old data
            cur.execute("DELETE FROM top_tv_shows")

            # Insert new data
            for show in scraped_shows:
                cur.execute("INSERT INTO top_tv_shows (title, href) VALUES (%s, %s)", (show['text'], show['href']))
                logging.debug("Data inserted into database")

            conn.commit()  # Commit the transaction
            shows = scraped_shows

    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            logging.debug("Database connection closed")

    # Randomize and return the top 25 shows
    random.shuffle(shows)
    return shows[:25]


def scrape_top_tv_shows():
    logging.debug("Scraping top tv shows")
    try:
        url = "https://editorial.rottentomatoes.com/guide/popular-tv-shows/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

        time.sleep(1)
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return f"Error: Received status code {response.status_code}"

        time.sleep(1)
        soup = BeautifulSoup(response.text, 'html.parser')
        class_elements = soup.find_all(class_="article_movie_title")

        results = []
        for element in class_elements:
            a_tag = element.find('a')
            if a_tag and a_tag.has_attr('href'):
                href = a_tag['href']
                text = a_tag.get_text(strip=True)
                # Add 'media_type': 'tv' to each result item
                results.append({'href': href, 'text': text, 'media_type': 'tv show'})

        random.shuffle(results)
        return results

    except Exception as e:
        return f"An error occurred: {e}"


def scrape_top_movies():
    logging.debug("Scraping top movies")
    try:
        url = "https://editorial.rottentomatoes.com/guide/popular-movies/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logging.error(f"Error: Received status code {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        class_elements = soup.find_all(class_="article_movie_title")  # Modify this if the HTML class differs for movies

        results = []
        for element in class_elements:
            a_tag = element.find('a')
            if a_tag and a_tag.has_attr('href'):
                href = a_tag['href']
                text = a_tag.get_text(strip=True)
                results.append({'href': href, 'text': text, 'media_type': 'movie'})

        random.shuffle(results)
        return results

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return []

def scrape_top_anime():
    logging.debug("Scraping top anime")
    try:
        url = "https://myanimelist.net/topanime.php?type=airing"  # Replace with the actual URL of the top anime page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logging.error(f"Error: Received status code {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        detail_elements = soup.find_all(class_="detail", limit=25)

        results = []
        for element in detail_elements:
            a_tag = element.find('a')
            if a_tag and a_tag.has_attr('href'):
                href = a_tag['href']
                text = a_tag.get_text(strip=True)
                results.append({'href': href, 'text': text, 'media_type': 'anime'})

        random.shuffle(results)
        return results

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return []

def scrape_top_books():
    logging.debug("Scraping top books")
    try:
        url = "https://www.goodreads.com/list/show/143500.Best_Books_of_the_Decade_2020_s"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

        time.sleep(1)
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return f"Error: Received status code {response.status_code}"

        soup = BeautifulSoup(response.text, 'html.parser')
        book_elements = soup.find_all('a', class_="bookTitle")

        results = []
        for element in book_elements:
            href = "https://www.goodreads.com" + element.get('href')
            book_title = element.find('span').get_text(strip=True)
            results.append({'href': href, 'text': book_title, 'media_type': 'book'})

        random.shuffle(results)
        return results

    except Exception as e:
        return f"An error occurred: {e}"

def find_top_media():
    cst_timezone = pytz.timezone('America/Chicago')  # CST timezone
    current_time_cst = datetime.now(cst_timezone).strftime('%Y-%m-%d %I:%M:%S %p')
    logging.debug(f"Find Top Media started at {current_time_cst}")
    
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Fetch media from various sources and update database
        media_sources = {
            'tv show': scrape_top_tv_shows,
            'movie': scrape_top_movies,
            'anime': scrape_top_anime,
            'book': scrape_top_books
        }

        for media_type, scrape_function in media_sources.items():
            logging.debug(f"Fetching {media_type}")

            # Check the last updated time
            cur.execute("SELECT MAX(last_updated) FROM top_media WHERE media_type = %s", (media_type,))
            last_updated_result = cur.fetchone()
            last_updated = last_updated_result[0] if last_updated_result else None

            if not last_updated or datetime.now() - last_updated > timedelta(hours=48):
                # Data is old or not present, scrape new data
                scraped_media = scrape_function()
                logging.debug(f"Scraping new data for {media_type}")

                # Update database with new data
                for media_item in scraped_media:
                    cur.execute("INSERT INTO top_media (title, href, media_type, last_updated) VALUES (%s, %s, %s, %s) ON CONFLICT (href) DO NOTHING",
                                (media_item['text'], media_item['href'], media_type, datetime.now()))
                
                conn.commit()  # Commit the transaction

        # Fetch a balanced number of items per media type from the database
        final_media_list = []
        for media_type in media_sources.keys():
            cur.execute("SELECT title, href, media_type FROM top_media WHERE media_type = %s ORDER BY RANDOM() LIMIT 7", (media_type,))
            final_media_list.extend(cur.fetchall())

        # Shuffle the final list to mix media types
        random.shuffle(final_media_list)

        return final_media_list[:25]  # Ensure only 25 items are returned

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return []
    finally:
        if conn:
            conn.close()
            logging.debug("Database connection closed")
