from bs4 import BeautifulSoup
import csv
import requests

# Fetch the FAQ page content
url = "https://www.southflorida.edu/current-students/faq"
response = requests.get(url)
html = response.text
soup = BeautifulSoup(html, "html.parser")

with open("sfsc_faq_output.csv", "w", newline='', encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Category", "Question", "Answer Summary", "Links"])

    current_category = None
    for element in soup.find_all(['h2', 'div'], recursive=True):
        # Update category when an h2 is found
        if element.name == 'h2':
            current_category = element.get_text(strip=True)
        # For each FAQ panel
        if element.name == 'div' and 'panel' in element.get('class', []):
            # Question
            question_tag = element.find('h4', class_='panel-title')
            question = question_tag.get_text(strip=True) if question_tag else ""
            # All panel-body divs (sometimes there are multiple)
            panel_bodies = element.find_all('div', class_='panel-body')
            answer_parts = []
            links = []
            for panel_body in panel_bodies:
                answer_parts.append(panel_body.get_text(" ", strip=True))
                links += [a['href'] for a in panel_body.find_all('a', href=True)]
            answer = " ".join(answer_parts)
            writer.writerow([current_category, question, answer, ", ".join(links)])

print("✅ FAQ content has been saved to sfsc_faq_output.csv")
