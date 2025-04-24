import requests
from bs4 import BeautifulSoup
import re
import csv

# Function to clean text
def clean_text(text):
    return re.sub(r'\s+', ' ', text.strip())

# Function to scrape policies from the website
def scrape_policies(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract policies from the main content
        main_content = soup.select_one('.col-md-9.col-sm-8')
        policies = []
        current_category = ''
        
        if main_content:
            for element in main_content.find_all(['h2', 'p']):
                if element.name == 'h2':
                    current_category = clean_text(element.get_text())
                elif element.name == 'p':
                    a_tag = element.find('a')
                    if a_tag and a_tag.get('href'):
                        title = clean_text(a_tag.get_text())
                        policy_id = title.split()[0] if title.split()[0].replace('.', '').isdigit() else ''
                        policies.append({
                            'id': policy_id,
                            'title': title,
                            'url': a_tag['href'] if a_tag['href'].startswith('http') else f"https://www.southflorida.edu{a_tag['href']}",
                            'category': current_category
                        })
        
        return policies
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

# Function to save policies to CSV
def save_to_csv(policies, filename='policies.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'title', 'url', 'category'])
        writer.writeheader()
        for policy in policies:
            writer.writerow(policy)
    print(f"CSV file '{filename}' generated successfully.")

# Main execution
if __name__ == "__main__":
    url = "https://www.southflorida.edu/policies"
    policies = scrape_policies(url)
    
    if policies:
        save_to_csv(policies)
    else:
        print("No policies found.")