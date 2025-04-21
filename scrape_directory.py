import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Base URL of the directory
base_url = "https://www.southflorida.edu/faculty-staff/employee-directory"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36"
}

# List to store employee data
employees = []

# Function to scrape a single page
def scrape_page(url):
    print(f"Scraping: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Error: Failed to fetch {url} (Status: {response.status_code})")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='tshowcase-box-table')
        if not table:
            print("Error: No employee table found")
            return None

        rows = table.find_all('tr', class_='ts-align-left')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 3:
                continue

            name_link = cols[0].find('a')
            name = name_link.text.strip() if name_link else "N/A"
            title = cols[1].text.strip() if cols[1].text.strip() else "N/A"
            phone = cols[2].text.strip() if cols[2].text.strip() else "N/A"
            email = "N/A"  # Will try to get from profile page
            department = "N/A"  # Will try to get from profile page

            # Try to scrape profile page for email and department
            if name_link and 'href' in name_link.attrs:
                profile_url = name_link['href']
                try:
                    profile_response = requests.get(profile_url, headers=headers, timeout=5)
                    if profile_response.status_code == 200:
                        profile_soup = BeautifulSoup(profile_response.text, 'html.parser')
                        email_link = profile_soup.find('a', href=lambda x: x and x.startswith('mailto:'))
                        if email_link:
                            email = email_link.text.strip() or email_link['href'].replace('mailto:', '').strip()
                        # Adjust this selector after inspecting a profile page
                        dept_elem = profile_soup.find('p', class_='department')  # Hypothetical
                        if dept_elem:
                            department = dept_elem.text.strip()
                except Exception as e:
                    print(f"Error scraping profile {profile_url}: {e}")

            employees.append({
                'Name': name,
                'Title': title,
                'Department': department,
                'Email': email,
                'Phone': phone
            })

        # Find next page link
        pager = soup.find('div', class_='tshowcase_pager')
        if not pager:
            return None
        next_page = pager.find('a', text='Next Page >')
        if next_page and 'href' in next_page.attrs:
            return f"{base_url}{next_page['href']}"
        return None

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

# Scrape all pages
current_url = base_url
page_count = 0
max_pages = 18  # From provided HTML

while current_url and page_count < max_pages:
    next_url = scrape_page(current_url)
    current_url = next_url
    page_count += 1
    time.sleep(1)  # Avoid overwhelming the server

# Save to CSV
if employees:
    df = pd.DataFrame(employees)
    df.to_csv('employee_directory.csv', index=False)
    print(f"Success! Saved {len(employees)} employees to employee_directory.csv")
else:
    print("Error: No data scraped. The table may be JavaScript-rendered or the site blocked the request.")