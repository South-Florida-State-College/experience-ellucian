import requests
from bs4 import BeautifulSoup
import re
import csv

# Function to clean text
def clean_text(text):
    return re.sub(r'\s+', ' ', text.strip())

# Function to scrape procedures from the website
def scrape_procedures(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract sidebar menu procedures
        sidebar = soup.select_one('.sideNav .sidebarMenu')
        procedures = []
        if sidebar:
            for li in sidebar.find_all('li', recursive=False):
                a_tag = li.find('a')
                if a_tag and a_tag.get('href'):
                    title = clean_text(a_tag.get_text())
                    procedure_id = title.split()[0] if title.split()[0].replace('.', '').isdigit() else ''
                    procedures.append({
                        'id': procedure_id,
                        'title': title,
                        'url': a_tag['href'],
                        'category': ''
                    })
                
                # Handle nested items (e.g., International Student Classification)
                for sub_li in li.find_all('li', recursive=True):
                    sub_a = sub_li.find('a')
                    if sub_a and sub_a.get('href'):
                        procedures.append({
                            'id': '',
                            'title': clean_text(sub_a.get_text()),
                            'url': sub_a['href'],
                            'category': ''
                        })
        
        # Extract categorized procedures
        categories = soup.select('.col-md-9 h2')
        for h2 in categories:
            category = clean_text(h2.get_text())
            for sibling in h2.find_next_siblings():
                if sibling.name == 'h2':
                    break
                if sibling.name == 'p':
                    for a_tag in sibling.find_all('a'):
                        if a_tag.get('href'):
                            title = clean_text(a_tag.get_text())
                            procedure_id = title.split()[0] if title.split()[0].replace('.', '').isdigit() else ''
                            # Update or append procedure with category
                            found = False
                            for proc in procedures:
                                if proc['title'] == title or proc['url'] == a_tag['href']:
                                    proc['category'] = category
                                    found = True
                                    break
                            if not found:
                                procedures.append({
                                    'id': procedure_id,
                                    'title': title,
                                    'url': a_tag['href'],
                                    'category': category
                                })
        
        return procedures
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

# Function to save procedures to CSV
def save_to_csv(procedures, filename='procedures.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'title', 'url', 'category'])
        writer.writeheader()
        for proc in procedures:
            writer.writerow(proc)
    print(f"CSV file '{filename}' generated successfully.")

# Main execution
if __name__ == "__main__":
    url = "https://www.southflorida.edu/procedures"
    procedures = scrape_procedures(url)
    
    if procedures:
        save_to_csv(procedures)
    else:
        print("No procedures found.")