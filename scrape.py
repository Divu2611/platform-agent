import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from embedding import get_openai_embeddings

visited_urls = set()

def scrape_page(url, base_url):
    """
    Scrapes a webpage and extracts relevant text content while ignoring navigation and sidebars,
    but still follows links from those sections.
    """
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

    # **Extract and store all links first (even from navbars/sidebars)**
    links = [urljoin(base_url, a['href']) for a in soup.find_all('a', href=True) if is_valid_url(urljoin(base_url, a['href']), base_url)]

    # **Remove unwanted sections for text extraction**
    for unwanted in soup.select(".nav, #nav, nav, .nav_bottom, #nav_bottom, nav_bottom, .nav-item, #nav-item, nav-item, .header, #header, header, .footer, #footer, footer, .sidebar, #sidebar, sidebar, .navbar, #navbar, navbar, .menu, #menu, menu, .breadcrumbs, #breadcrumbs, breadcrumbs, .pagination, #pagination, pagination"):
        unwanted.decompose()  # Remove from DOM

    # **Extract only the main content for text scraping**
    main_content = soup.find('main') or soup.find('article') or soup.find('div', {'class': 'content'})
    
    if main_content:
        page_text = main_content.get_text(separator=" ", strip=True)
    else:
        page_text = soup.get_text(separator=" ", strip=True)

    embedding = get_openai_embeddings([page_text])  # Generate embeddings for the extracted text

    # **Now, visit all extracted links**
    for next_link in links:
        scrape_page(next_link, base_url)
        time.sleep(1)  # Respectful crawling delay

def is_valid_url(url, base_url):
    """
    Checks if the URL belongs to the same website and hasn't been visited.
    """
    parsed_url = urlparse(url)
    parsed_base = urlparse(base_url)
    
    return (parsed_url.netloc == parsed_base.netloc) and (url not in visited_urls)

if __name__ == "__main__":
    start_url = "https://www.braze.com/docs"  # Replace with your target URL
    scrape_page(start_url, start_url)