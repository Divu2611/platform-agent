# Importing Python Libraries.
import time
import uuid
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin, urlparse

from embedding import get_openai_embeddings
from tools.database import create

visited_urls = set()

def normalize_url(url):
    """
    Normalizes the URL by removing any trailing slashes.
    """
    return url.rstrip('/')


def scrape_page(url, base_url):
    """
    Scrapes a webpage and extracts relevant text content while ignoring navigation and sidebars,
    but still follows links from those sections.
    """
    url = normalize_url(url)
    base_url = normalize_url(base_url)

    if url in visited_urls:
        return

    visited_urls.add(url)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract and store all links first (even from navbars/sidebars)
    links = [urljoin(base_url, a['href']) for a in soup.find_all('a', href=True) if is_valid_url(urljoin(base_url, a['href']), base_url)]

    # Remove unwanted sections for text extraction
    for unwanted in soup.select(".nav, #nav, nav, .nav_bottom, #nav_bottom, nav_bottom, .nav-item, #nav-item, nav-item, .header, #header, header, .footer, #footer, footer, .sidebar, #sidebar, sidebar, .navbar, #navbar, navbar, .menu, #menu, menu, .breadcrumbs, #breadcrumbs, breadcrumbs, .pagination, #pagination, pagination"):
        unwanted.decompose()  # Remove from DOM

    # Extract only the main content for text scraping
    main_content = soup.find('main') or soup.find('article') or soup.find('div', {'class': 'content'})

    page_text = main_content.get_text(separator=" ", strip=True) if main_content else soup.get_text(separator=" ", strip=True)

    embeddings, chunks = get_openai_embeddings([page_text])  # Generate embeddings for the extracted text
    chunk_len = len(chunks)

    for i in range(chunk_len):
        if not chunks[i]:
            continue

        chunk = chunks[i].replace("'",'"')

        insert_query = f"""
            INSERT INTO embeddings (id, chunk, embedding, created_at, updated_at, url)
            VALUES ({uuid.uuid4()}, '{chunk}', {embeddings[i]}, '{datetime.now()}', '{datetime.now()}', '{url}')
        """

        create(keyspace="irona", insert_query=insert_query)  # Store the extracted text and embeddings in the database
        print(f"Inserted chunk {i+1}/{chunk_len} for {url}")

    print()

    # Now, visit all extracted links
    for next_link in links:
        scrape_page(next_link, base_url)
        time.sleep(1)  # Respectful crawling delay


def is_valid_url(url, base_url):
    """
    Checks if the URL belongs to the same website and hasn't been visited.
    """
    parsed_url = urlparse(url)
    parsed_base = urlparse(base_url)
    
    return url.startswith(base_url) and (parsed_url.netloc == parsed_base.netloc) and (url not in visited_urls)


if __name__ == "__main__":
    start_url = "https://www.braze.com/docs"  # Replace with your target URL
    scrape_page(start_url, start_url)