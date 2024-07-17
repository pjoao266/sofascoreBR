
API_SCANTRACK_URL = 'https://api.sofascore.com/api/v1/'
PATH = "E:/Programações/sofascoreBR/"
import requests # Import the requests module
import sys
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import json
import pandas as pd
from datetime import datetime
from git import Repo

def get_api_url():
    """
    Returns the API URL for the Scantrack service.
    """
    return API_SCANTRACK_URL

def read_api_sofascore(url, selenium=True, error_stop=False):
    """
    Reads data from the SofaScore API.

    Args:
        url (str): The URL of the API endpoint.
        selenium (bool, optional): Whether to use Selenium for scraping. Defaults to True.
        error_stop (bool, optional): Whether to stop execution on error. Defaults to False.

    Returns:
        dict: The response JSON data.
    """
    if selenium:
        options = webdriver.ChromeOptions()     
        options.headless = True
        options.add_argument("--remote-debugging-port=9222")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument(r"user-data-dir=.\cookies\\test") 

        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.implicitly_wait(20)
        driver.get(url)
        try:
            element = driver.find_element(By.CSS_SELECTOR, "pre")
            response_json = json.loads(element.text)
        except:
            response_json = {'error': {'message': 'Erro ao carregar página'}}
        driver.close()
    else:
         response_json = requests.get(url).json()
    if 'error' in response_json and len(response_json) == 1:
        print('Erro:', response_json['error']['message'])
        if error_stop == True:
            sys.exit()
        else:
            response_json = None
    return response_json

def git_push():
    """
    Pushes the code changes to the Git repository.
    """
    try:
        PATH_OF_GIT_REPO = PATH + '.git/'
        DATE_AND_HOUR = datetime.now().strftime("%d/%m %Hh")
        COMMIT_MESSAGE = 'Atualizações dados ' + DATE_AND_HOUR
        repo = Repo(PATH_OF_GIT_REPO)
        repo.git.add(update=True)
        repo.index.commit(COMMIT_MESSAGE)
        origin = repo.remote(name='origin')
        origin.push()
    except:
        print('Some error occurred while pushing the code')    

def db_to_excel(mydb):
    """
    Converts database tables to Excel files.

    Args:
        mydb: The database connection object.
    """
    mycursor = mydb.cursor()
    sql_show_tables = "SHOW TABLES"
    mycursor.execute(sql_show_tables)
    tables = mycursor.fetchall()
    tables = [table[0] for table in tables]
    for table in tables:
        sql_select_all = f"SELECT * FROM {table}"
        mycursor.execute(sql_select_all)
        result = mycursor.fetchall()
        df = pd.DataFrame(result, columns=mycursor.column_names)
        excel_file = PATH + f"/data/{table}.xlsx"
        df.to_excel(excel_file, index=False)


def get_bin_image(id, type):
    """
    Retrieves the binary image data for a given ID and type.

    Args:
        id: The ID of the image.
        type: The type of the image.

    Returns:
        bytes: The binary image data.
        None: If the image is not found.
    """
    url = get_api_url() + f"/{type}/{id}/image"
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    elif response.status_code == 404:
        return None