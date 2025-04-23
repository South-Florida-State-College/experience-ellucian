import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Base URL of the directory
base_url = "https://sfsc.sharepoint.com/sites/pod/Forms/Forms/Faculty%20Forms.aspx"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36"
}