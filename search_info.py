import time
import logging
import random
import os
import requests
import pytz
from flask import current_app
from openai import OpenAI
from math import ceil
from bs4 import BeautifulSoup
from urllib.parse import quote
from datetime import datetime, timedelta
from db_config import db
from models import User, Subscription, TopTVShow, TopMedia
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
    try:
        # Check the last updated time
        logging.debug("Checking last update time")
        last_updated_result = db.session.query(db.func.max(TopTVShow.last_updated)).scalar()
        if last_updated_result and datetime.now() - last_updated_result < timedelta(hours=48):
            # Data is fresh, fetch from database
            shows = TopTVShow.query.order_by(TopTVShow.id).all()
            logging.debug("Fetching data from database")
        else:
            # Data is old or not present, scrape the website
            scraped_shows = scrape_top_tv_shows()
            logging.debug("Scraping new data")

            # Clear old data
            TopTVShow.query.delete()

            # Insert new data
            for show in scraped_shows:
                new_show = TopTVShow(title=show['text'], href=show['href'])
                db.session.add(new_show)
                logging.debug("Data inserted into database")

            db.session.commit()  # Commit the transaction
            shows = scraped_shows

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        db.session.rollback()

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
            logging.error(f"Error: Received status code {response.status_code}")
            return []

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
        logging.error(f"An error occurred: {e}")
        return []


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
    with app.app_context():
        cst_timezone = pytz.timezone('America/Chicago')
        current_time_cst = datetime.now(cst_timezone).strftime('%Y-%m-%d %I:%M:%S %p')
        logging.debug(f"Find Top Media started at {current_time_cst}")

        try:
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
                last_updated_result = db.session.query(db.func.max(TopMedia.last_updated)).filter(TopMedia.media_type == media_type).scalar()
                if not last_updated_result or datetime.now() - last_updated_result > timedelta(hours=48):
                    # Data is old or not present, scrape new data
                    scraped_media = scrape_function()
                    logging.debug(f"Scraping new data for {media_type}")

                    # Update database with new data
                    # Clear old data
                    TopMedia.query.filter(TopMedia.media_type == media_type).delete()
                    for media_item in scraped_media:
                        new_media = TopMedia(title=media_item['text'], href=media_item['href'], media_type=media_type)
                        db.session.add(new_media)

                    db.session.commit()  # Commit the transaction

            # Fetch a balanced number of items per media type from the database
            final_media_list = []
            for media_type in media_sources.keys():
                media_items = TopMedia.query.filter(TopMedia.media_type == media_type).order_by(db.func.random()).limit(7).all()
                final_media_list.extend(media_items)

            # Shuffle the final list to mix media types
            random.shuffle(final_media_list)

            # Convert TopMedia objects to dictionaries
            final_media_dicts = [{'title': media.title, 'href': media.href, 'media_type': media.media_type} for media in final_media_list[:25]]
            return final_media_dicts

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return []

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def process_image(filepath):
    api_key = os.getenv('REMOVE_BG_API_KEY')  # Ensure you've set this environment variable
    response = requests.post(
        'https://api.remove.bg/v1.0/removebg',
        files={'image_file': open(filepath, 'rb')},
        data={'size': 'auto'},
        headers={'X-Api-Key': api_key},
    )
    if response.status_code == requests.codes.ok:
        output_path = filepath.rsplit('.', 1)[0] + '_no_bg.png'
        with open(output_path, 'wb') as out:
            out.write(response.content)
        return output_path
    else:
        print("Error:", response.status_code, response.text)
        return filepath  # Return original if error
