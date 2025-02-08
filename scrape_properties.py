import requests
from bs4 import BeautifulSoup
import time

def get_property_listings(property_type=None, location=None):
    base_url = 'https://kipra.homes/property/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(base_url, headers=headers)
        properties = []
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            property_items = soup.find_all('div', class_='property-item')
            
            for item in property_items:
                title_elem = item.find('h3', class_='title')
                if not title_elem:
                    continue
                    
                title = title_elem.get_text(strip=True)
                link = title_elem.find('a')['href'] if title_elem.find('a') else None
                location_elem = item.find('div', class_='location')
                item_location = location_elem.get_text(strip=True) if location_elem else ''
                price_elem = item.find('div', class_='price')
                price = price_elem.get_text(strip=True) if price_elem else ''
                
                # Filter based on criteria if provided
                if property_type and property_type.lower() not in title.lower():
                    continue
                if location and location.lower() not in item_location.lower():
                    continue
                
                properties.append({
                    'title': title,
                    'location': item_location,
                    'price': price,
                    'link': link
                })
                
        return properties
    except Exception as e:
        print(f"Error scraping properties: {str(e)}")
        return []

if __name__ == "__main__":
    # Test the scraper
    properties = get_property_listings()
    print(f"Found {len(properties)} properties") 