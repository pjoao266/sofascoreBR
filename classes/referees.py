import sys
sys.path.append("../")
from datetime import datetime
from classes.utils import get_api_url, read_api_sofascore, get_bin_image
from SQLconfig.config_mysql import mydb

class Referee:
    """
    Represents a referee.

    Attributes:
        id (int): The ID of the referee.
        name (str): The name of the referee.
    """

    def __init__(self, id):
        """
        Initializes a Referee object.

        Args:
            id (int): The ID of the referee.
        """
        self.id = id
    
    def get_info_referee(self):
        """
        Retrieves information about the referee from the API.
        """
        url = get_api_url() + f"referee/{self.id}"
        referee = read_api_sofascore(url, selenium=False)
        self.name = referee['referee']['name']

    def save(self, mydb):
        """
        Saves the referee's information to the database.

        Args:
            mydb: The MySQL database connection object.
        """
        sql = f'INSERT INTO referee (id, name, image) VALUES (%s, %s, %s)'
        val = (int(self.id), self.name)
        image = get_bin_image(self.id, 'referee')
        mycursor = mydb.cursor()
        mycursor.execute(sql, val)
        mydb.commit()
        mycursor.close()
        
    def __str__(self):
        """
        Returns a string representation of the referee.

        Returns:
            str: A string representation of the referee.
        """
        return f'Referee: {self.name} - ID: {self.id}'