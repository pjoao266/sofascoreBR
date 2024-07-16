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
    return API_SCANTRACK_URL

def read_api_sofascore(url, selenium = True, error_stop = False):
    if selenium:
        options = webdriver.ChromeOptions()     
        options.headless = True
        options.add_argument("--remote-debugging-port=9222")  # this
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument(r"user-data-dir=.\cookies\\test") 

        driver = webdriver.Chrome(ChromeDriverManager().install(), options= options)
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
    try:
        PATH_OF_GIT_REPO = PATH + '.git/'  # make sure .git folder is properly configured
        DATE_AND_HOUR = datetime.now().strftime("%d/%m %Hh")
        COMMIT_MESSAGE = 'Atualizações dados ' + DATE_AND_HOUR
        repo = Repo(PATH_OF_GIT_REPO)
        repo.git.add(update=True)
        repo.index.commit(COMMIT_MESSAGE)
        origin = repo.remote(name='origin')
        origin.push()
    except:
        print('Some error occured while pushing the code')    

def db_to_excel(mydb):
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