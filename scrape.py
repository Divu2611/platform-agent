# Importing Python Libraries.
import io
import os
import re
import time
import pickle
import PyPDF2
import hashlib
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse

from embedding import get_embeddings
from tools.database import create, retrieve


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
info_logger = setup_logger("info_logger", "logs/data/info.log", logging.INFO)
warning_logger = setup_logger("warning_logger", "logs/data/warning.log", logging.WARNING)
error_logger = setup_logger("error_logger", "logs/data/error.log", logging.ERROR)


def save_set(data_set, file_path):
    """Save a set to a file using pickle."""
    with open(file_path, "wb") as file:
        pickle.dump(data_set, file)

def load_set(file_path):
    """Load a set from a file using pickle."""
    try:
        with open(file_path, "rb") as file:
            return pickle.load(file)
    except (FileNotFoundError, EOFError):
        return set()

# Define file paths for persistence
visited_urls_file = "visited_urls.pkl"
visited_hashes_file = "visited_hashes.pkl"

# Load visited sets from disk (or initialize empty sets)
visited_urls = load_set(visited_urls_file)
visited_hashes = load_set(visited_hashes_file)


checkpoint_file = "checkpoint.txt"
urls_file = "unique_urls.txt"


def save_checkpoint(index):
    with open(checkpoint_file, "w") as f:
        f.write(str(index))


def get_page_hash(content):
    """Generate a hash of the page content to identify duplicate pages."""
    return hashlib.md5(content.encode('utf-8')).hexdigest()

def fetch_webpage(url):
    """Fetch webpage content and extract all links."""
    response = requests.get(url)
    if response.status_code != 200:
        error_logger.error(f"Failed to fetch webpage {url}")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    page_hash = get_page_hash(response.text)

    # Avoid duplicate content
    if page_hash in visited_hashes:
        warning_logger.warning(f"Duplicate page found: {url}")
        return None

    visited_hashes.add(page_hash)
    save_set(visited_hashes, visited_hashes_file)

    # Remove unwanted sections for text extraction
    for unwanted in soup.select(".nav, #nav, nav, .nav_bottom, #nav_bottom, nav_bottom, .nav-item, #nav-item, nav-item, .header, #header, header, .footer, #footer, footer, .sidebar, #sidebar, sidebar, .navbar, #navbar, navbar, .menu, #menu, menu, .breadcrumbs, #breadcrumbs, breadcrumbs, .pagination, #pagination, pagination"):
        unwanted.decompose()  # Remove from DOM

    # Extract only the main content for text scraping
    main_content = soup.find('main') or soup.find('article') or soup.find('div', {'class': 'content'})

    page_text = main_content.get_text(separator=" ", strip=True) if main_content else soup.get_text(separator=" ", strip=True)

    return page_text


def fetch_pdf(url):
    """Fetch PDF content and extract text."""
    response = requests.get(url)
    if response.status_code != 200:
        error_logger.error(f"Failed to fetch PDF {url}")
        return None
    
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(response.content))
    text = ""
    for page in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page].extract_text()
    
    return text


def load_checkpoint():
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, "r") as f:
            return int(f.read().strip())
    return 0


def load_urls(file_path):
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def scrape_page():
    urls = load_urls(urls_file)
    start_index = load_checkpoint()

    for i in range(start_index, len(urls)):
        url = urls[i]

        if url in visited_urls:
            warning_logger.warning(f"Skipping already scraped URL: {url}")
            continue

        if '.xlsx' in url or '.xls' in url or '.csv' in url or '.rtf' in url or '.png' in url or '.jpg' in url or '.jpeg' in url:
            warning_logger.warning(f"Skipping unsupported URL: {url}")
            continue

        page_text = fetch_pdf(url) if url.endswith(".pdf") else fetch_webpage(url)

        if page_text:
            start_time = time.time()

            embeddings, chunks = get_embeddings([page_text])  # Generate embeddings for the extracted text
            if not embeddings or not chunks:
                continue

            chunk_len = len(chunks)

            insert_retrieve_resource_query = f"""
                INSERT INTO resource (location, agent_id)
                VALUES ('{url}', 12)
                RETURNING id;
            """

            rows, columns = retrieve(retrieve_query = insert_retrieve_resource_query)
            resource_id = rows[0][0]

            for j in range(chunk_len):
                insert_start_time = time.time()

                if not chunks[j] or not embeddings[j]:
                    continue

                chunk = chunks[j].replace("'",'"').replace("{%%", "{%").replace("%%}", "%}").replace(":", "::")
                chunk = re.sub(r"%\((\w+)\)s", r":\1", chunk)

                insert_embeddings_query = f"""
                    INSERT INTO embedding (resource_id, chunk, embedding)
                    VALUES ('{resource_id}', '{chunk}', '{embeddings[j]}')
                """

                create(insert_query = insert_embeddings_query)

                insert_end_time = time.time()
                insert_elapsed_time = insert_end_time - insert_start_time
                info_logger.info(f"Inserted chunk {j+1}/{chunk_len} for {url} in {insert_elapsed_time:.2f} seconds")

            end_time = time.time()
            elapsed_time = end_time - start_time

            visited_urls.add(url)
            save_set(visited_urls, visited_urls_file)

            info_logger.info(f"Scraped {url} in {elapsed_time:.2f} seconds")
        else:
            warning_logger.warning(f"Failed to scrape {url} due to missing content")

        save_checkpoint(i + 1)


def is_valid_url(url, base_url):
    """
    Checks if the URL belongs to the same website and hasn't been visited.
    """
    parsed_url = urlparse(url)
    parsed_base = urlparse(base_url)
    
    return url.startswith(base_url) and (parsed_url.netloc == parsed_base.netloc) and (url not in visited_urls)


if __name__ == "__main__":
    scrape_page()