import sys
sys.path.append("../")
from datetime import datetime
from classes.utils import get_api_url, read_api_sofascore
from SQLconfig.config_mysql import mydb

class Manager:
    def __init__(self, id):
        self.id = id
    
    def get_info_manager(self):
        url = get_api_url() + f"manager/{self.id}"
        manager = read_api_sofascore(url, selenium=False)
        self.manager = manager
        self.name = manager['manager']['name']
        if 'team' in manager['manager']:
            self.team_id = manager['manager']['team']['id']
        else:
            self.team_id = None
            
    def save(self, mydb):
        sql = f'INSERT INTO manager (id, name, id_team) VALUES (%s, %s, %s)'
        vars_int = ['id', 'team_id']
        for var in vars_int:
            if self.__dict__[var] != None:
                self.__dict__[var] = int(self.__dict__[var])
        val = (self.id, self.name, self.team_id)
        mycursor = mydb.cursor()
        mycursor.execute(sql, val)
        mydb.commit()
        mycursor.close()
    def __str__(self):
        return f'Manager: {self.name} - ID: {self.id} - Team ID: {self.team_id}'
