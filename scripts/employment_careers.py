from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime
import sys

# Configure headless browser
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
driver = webdriver.Chrome(options=options)

# Scrape the page
url = "https://sfsc.interviewexchange.com/static/clients/430SFM1/index.jsp"
try:
    driver.get(url)
    driver.implicitly_wait(10)  # Wait for content
    soup = BeautifulSoup(driver.page_source, "html.parser")
except Exception as e:
    print(f"Error fetching page: {e}")
    driver.quit()
    sys.exit(1)

driver.quit()

# Extract job listings
jobs = []
table = soup.find("table", class_="effect1")
if table:
    for link in table.find_all("a"):
        title = link.text.strip()
        href = link.get("href")
        if title and href:
            if not href.startswith("http"):
                href = f"https://sfsc.interviewexchange.com/static/clients/430SFM1/{href}"
            jobs.append({
                "title": title,
                "link": href,
                "pubDate": datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
            })
else:
    print("No table with class 'effect1' found.")
    sys.exit(1)

if not jobs:
    print("No job listings found in the table.")

# Create and save RSS feed
rss = ET.Element("rss", version="2.0")
channel = ET.SubElement(rss, "channel")
ET.SubElement(channel, "title").text = "SFSC Job Postings"
ET.SubElement(channel, "link").text = url
ET.SubElement(channel, "description").text = "Job postings from South Florida State College"

for job in jobs:
    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = job["title"]
    ET.SubElement(item, "link").text = job["link"]
    ET.SubElement(item, "description").text = job["title"]
    ET.SubElement(item, "pubDate").text = job["pubDate"]

try:
    tree = ET.ElementTree(rss)
    tree.write("jobs.rss", encoding="utf-8", xml_declaration=True)
    print("RSS feed generated: jobs.rss")
except Exception as e:
    print(f"Error saving RSS file: {e}")
    print("\nRSS content (save manually):")
    ET.dump(rss)