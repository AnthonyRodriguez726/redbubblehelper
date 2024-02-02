from search_info import find_top_media
import time
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

def test_rewrite_prompt():
    results = find_top_media()
    print(results)

if __name__ == "__main__":
    test_rewrite_prompt()