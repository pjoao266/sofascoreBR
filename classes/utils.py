API_SCANTRACK_URL = 'https://api.sofascore.com/api/v1/'
import requests # Import the requests module
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import json

def get_api_url():
    return API_SCANTRACK_URL

def read_api_sofascore(url, selenium = True):
    if selenium:
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.implicitly_wait(15)
        driver.maximize_window()
        driver.get(url)
        element = driver.find_element(By.CSS_SELECTOR, "pre")
        response_json = json.loads(element.text)
        driver.close()
    else:
         response_json = requests.get(url).json()
    if 'error' in response_json and len(response_json) == 1:
        print('Erro:', response_json['error']['message'])
        sys.exit()
    return response_json
