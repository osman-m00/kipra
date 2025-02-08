import requests
from bs4 import BeautifulSoup
import time
from typing import Dict, Any
import re

def clean_text(text: str) -> str:
    """Clean the text by removing extra whitespace and special characters."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep periods, commas, and basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    return text.strip()

def get_blog_links() -> list:
    """Get all blog post links from the main blog page and pagination."""
    base_url = 'https://kipra.homes/blog/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    blog_links = set()
    page = 1
    
    while True:
        if page == 1:
            url = base_url
        else:
            url = f'{base_url}page/{page}/'
        
        print(f"Fetching blog links from page {page}...")
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            break
            
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all('article')
        
        if not articles:
            break
            
        for article in articles:
            # Find the main link in each article
            link = article.find('a', href=True)
            if link and 'kipra.homes/blog/' in link['href']:
                blog_links.add(link['href'])
        
        # Check if there's a next page
        next_page = soup.find('a', class_='next')
        if not next_page:
            break
            
        page += 1
        time.sleep(1)  # Be nice to the server
    
    return list(blog_links)

def scrape_blog_content(url: str) -> Dict[str, Any]:
    """Scrape content from a single blog post."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"Scraping blog: {url}")
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get title
        title = soup.find('h1', class_='entry-title')
        if not title:
            title = soup.find('h1')
        title_text = clean_text(title.get_text()) if title else ''
        
        # Get date
        date = soup.find('time', class_='entry-date')
        date_text = date.get_text() if date else ''
        
        # Get main content
        content_div = soup.find('div', class_='entry-content')
        if not content_div:
            content_div = soup.find('article')
        
        if content_div:
            # Remove unwanted elements
            for element in content_div.find_all(['script', 'style', 'iframe', 'form']):
                element.decompose()
            
            # Get all paragraphs and headings
            content_elements = content_div.find_all(['p', 'h2', 'h3', 'h4', 'ul', 'ol'])
            content_text = '\n'.join([clean_text(elem.get_text()) for elem in content_elements])
        else:
            content_text = ''
        
        # Get categories/tags
        categories = []
        category_links = soup.find_all('a', {'rel': 'category tag'})
        for cat in category_links:
            categories.append(cat.get_text())
        
        return {
            'title': title_text,
            'date': date_text,
            'content': content_text,
            'categories': categories,
            'url': url
        }
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None

def scrape_all_blogs() -> Dict[str, Dict[str, Any]]:
    """Scrape all blog posts and return their content."""
    print("Starting blog scraping process...")
    blog_links = get_blog_links()
    print(f"Found {len(blog_links)} blog posts to scrape")
    
    blog_contents = {}
    for link in blog_links:
        content = scrape_blog_content(link)
        if content:
            blog_contents[link] = content
        time.sleep(1)  # Be nice to the server
    
    print(f"Successfully scraped {len(blog_contents)} blog posts")
    return blog_contents

if __name__ == "__main__":
    # Test the scraper
    blogs = scrape_all_blogs()
    print("\nSample of scraped blogs:")
    for url, blog in list(blogs.items())[:3]:
        print(f"\nTitle: {blog['title']}")
        print(f"Date: {blog['date']}")
        print(f"Categories: {', '.join(blog['categories'])}")
        print(f"Content preview: {blog['content'][:200]}...") 