import sys
sys.path.append("../")
from datetime import datetime
from classes.utils import get_api_url, read_api_sofascore, get_bin_image
from SQLconfig.config_mysql import mydb

class Referee:
    def __init__(self, id):
        self.id = id
    
    def get_info_referee(self):
        url = get_api_url() + f"referee/{self.id}"
        referee = read_api_sofascore(url, selenium=False)
        self.name = referee['referee']['name']

    def save(self, mydb):
        sql = f'INSERT INTO referee (id, name, image) VALUES (%s, %s, %s)'
        val = (int(self.id), self.name)
        image = get_bin_image(self.id, 'referee')
        mycursor = mydb.cursor()
        mycursor.execute(sql, val)
        mydb.commit()
        mycursor.close()
        
    def __str__(self):
        return f'Referee: {self.name} - ID: {self.id}'