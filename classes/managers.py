import sys
sys.path.append("../")
from datetime import datetime
from classes.utils import get_api_url, read_api_sofascore, get_bin_image
from SQLconfig.config_mysql import mydb

class Manager:
    def __init__(self, id):
        """
        Initializes a Manager object with the given id.

        Args:
        - id (int): The id of the manager.
        """
        self.id = id
    
    def get_info_manager(self):
        """
        Retrieves information about the manager from the API and stores it in the object.
        """
        url = get_api_url() + f"manager/{self.id}"
        manager = read_api_sofascore(url, selenium=False)
        self.manager = manager
        self.name = manager['manager']['name']
        if 'team' in manager['manager']:
            self.team_id = manager['manager']['team']['id']
        else:
            self.team_id = None
            
    def save(self, mydb):
        """
        Saves the manager object to the database.

        Args:
        - mydb: The database connection object.

        Returns:
        - None
        """
        sql = 'INSERT INTO manager (id, name, id_team, image) VALUES (%s, %s, %s, %s)'
        vars_int = ['id', 'team_id']
        for var in vars_int:
            if self.__dict__[var] != None:
                self.__dict__[var] = int(self.__dict__[var])
        image = get_bin_image(self.id, 'manager')
        val = (self.id, self.name, self.team_id, image)
        mycursor = mydb.cursor()
        mycursor.execute(sql, val)
        mydb.commit()
        mycursor.close()
        
    def __str__(self):
        """
        Returns a string representation of the Manager object.

        Returns:
        - str: A string representation of the Manager object.
        """
        return f'Manager: {self.name} - ID: {self.id} - Team ID: {self.team_id}'
