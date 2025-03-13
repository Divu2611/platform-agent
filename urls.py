# Importing Python Libraries.
import sys
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


sys.setrecursionlimit(20000) 


def setup_logger(name, log_file, level):
    """Function to create a logger for different log levels."""
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger

# Creating loggers for different log levels
info_logger = setup_logger("info_logger", "logs/url/info.log", logging.INFO)
error_logger = setup_logger("error_logger", "logs/url/error.log", logging.ERROR)


def normalize_url(url):
    return url.rstrip('/')

def get_unique_urls(base_url, output_file="unique_urls.txt"):
    visited_urls = set()
    parsed_base = urlparse(base_url)

    def crawl(url):
        url = normalize_url(url)

        if (not url.startswith(base_url) or 
            urlparse(url).netloc != parsed_base.netloc or 
            url in visited_urls):
            return

        info_logger.info(f"Crawling: {url}")
        visited_urls.add(url)

        try:
            response = requests.get(url, timeout=300)
            if response.status_code != 200:
                return
            
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                crawl(full_url)

        except requests.RequestException as e:
            error_logger.error(f"Failed to access {url}: {e}")

    crawl(base_url)

    # Save unique URLs to a file
    with open(output_file, "w", encoding="utf-8") as file:
        for url in sorted(visited_urls):
            file.write(url + "\n")

    info_logger.info(f"Unique URLs saved to {output_file}")

if __name__ == "__main__":
    base_url = "https://www.braze.com/docs"
    get_unique_urls(base_url)
