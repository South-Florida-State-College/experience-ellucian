import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime

# Scrape the page
url = "https://sfsc.interviewexchange.com/static/clients/430SFM1/index.jsp"
response = requests.get(url)

if response.status_code != 200:
    print(f"Failed to fetch the page. Status code: {response.status_code}")
    exit()

soup = BeautifulSoup(response.text, "html.parser")

# Extract job listings
jobs = []
table = soup.find("table", class_="effect1")
if not table:
    print("No table with class 'effect1' found on the page.")
    exit()

for link in table.find_all("a"):
    title = link.text.strip()
    href = link.get("href")
    jobs.append({
        "title": title,
        "link": href,
        "pubDate": datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
    })

# Create RSS feed
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

# Save RSS feed
output_file = "jobs.rss"
try:
    tree = ET.ElementTree(rss)
    tree.write(output_file)
    print(f"RSS feed generated: {output_file}")
except Exception as e:
    print(f"Failed to write RSS feed: {e}")