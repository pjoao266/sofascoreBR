import requests
import pandas as pd
import numpy as np

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import json
from datetime import datetime

from classes.utils import *
from SQLconfig.config_mysql import *
from classes.tournaments import Tournament
from classes.players import Player
from classes.events import Event
from classes.managers import Manager
from classes.teams import Team
from classes.referees import Referee

brasileirao = Tournament(id = 325, year = 2024)
brasileirao.run()
brasileirao.save_all(mydb)
print('Salva informações no excel...')
db_to_excel(mydb)
print('Atualiza em git...')
git_push()