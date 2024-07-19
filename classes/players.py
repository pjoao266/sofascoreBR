import sys
sys.path.append("../")
from datetime import datetime
from classes.utils import get_api_url, read_api_sofascore, get_bin_image
from SQLconfig.config_mysql import mydb

class Player:
    def __init__(self, id):
        """
        Initialize a Player object.

        Parameters:
        - id (int): The ID of the player.
        """
        self.id = id

    def get_info_players(self):
        """
        Get information about the player from the API and store it in the Player object.
        """
        url = get_api_url() + f"player/{self.id}"
        dados_players = read_api_sofascore(url, selenium=False)
        dados_players = dados_players['player']
        self.name = dados_players['name']
        self.shortName = dados_players['shortName']
        self.teamId = dados_players['team']['id']

        if 'height' in dados_players:
            self.height = dados_players['height']
        else:
            self.height = None

        if 'jerseyNumber' in dados_players:
            self.jerseyNumber = dados_players['jerseyNumber']
        else:
            self.jerseyNumber = None

        if 'dateOfBirthTimestamp' in dados_players:
            date_of_birth = datetime.fromtimestamp(dados_players['dateOfBirthTimestamp'])
            self.date_of_birth = date_of_birth
            current_date = datetime.now()
            interval_years = current_date - date_of_birth
            interval_years = current_date - date_of_birth
            self.age = int(interval_years.days/365)
        else:
            self.age = None
        
        if 'preferredFoot' in dados_players:
            self.preferredFoot = dados_players['preferredFoot']
        else:
            self.preferredFoot = None

    def get_player_position(self):
        """
        Get the player's position from the API and store it in the Player object.
        """
        dict_rename_positions ={
            'ST': ['CA', 'ATA'],
            'LW': ['PE', 'ATA'],
            'RW': ['PD', 'ATA'],
            'AM': ['MEI', 'MC'],
            'ML': ['ME', 'MC'],
            'MR': ['MD', 'MC'],
            'CM': ['MC', 'MC'],
            'MC': ['MC', 'MC'],
            'DM': ['VOL', 'VOL'],
            'DC': ['ZAG', 'ZAG'],
            'DR': ['LD', 'LAT'],
            'DL': ['LE', 'LAT'],
            'GK': ['GOL', 'GOL']
        }
        
        url = get_api_url() + f"player/{self.id}/characteristics"
        response = read_api_sofascore(url, selenium=False)['positions']

        if len(response) == 0:
            positions = ['UNK']
            grand_position = ['UNK']
        else:
            positions = []
            grand_position = []
            for position in response:
                positions.append(dict_rename_positions[position][0])
                grand_position.append(dict_rename_positions[position][1])
    
        if positions[0] == 'MC' and 'VOL' in positions:
            index_vol = positions.index('VOL')
            positions[index_vol] = 'MC'
            positions[0] = 'VOL'
            grand_position[index_vol] = 'MEI'
            grand_position[0] = 'VOL'

        primary_position = positions[0]
        primary_grand_position = grand_position[0]
        all_positions = '/'.join(positions)

        self.position = primary_position
        self.grand_position = primary_grand_position
        self.all_positions = all_positions

    def save(self, mydb):
        """
        Save the player's information to the database.

        Parameters:
        - mydb: The MySQL database connection.
        """
        mycursor = mydb.cursor()
        sql = "INSERT INTO player (id, id_team, name, shortName, position, grand_position, all_positions, height, jerseyNumber, birthDate, preferredFoot, image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        vars_int = ['id', 'teamId', 'height', 'jerseyNumber']
        vars_tot = ['id', 'teamId', 'name', 'shortName', 'position', 'grand_position', 'all_positions', 'height', 'jerseyNumber', 'date_of_birth', 'preferredFoot']
        for var in vars_tot:
            if var in self.__dict__:
                if var in vars_int and self.__dict__[var] != None:
                    self.__dict__[var] = int(self.__dict__[var])
                else:
                    self.__dict__[var] = self.__dict__[var]
            else:
                self.__dict__[var] = None
        image = get_bin_image(self.id, 'player')
        val = (self.id, self.teamId, self.name, self.shortName, self.position, self.grand_position, self.all_positions, self.height, self.jerseyNumber, self.date_of_birth, self.preferredFoot, image)
        mycursor.execute(sql, val)
        mydb.commit()
        mycursor.close()
        
    def __str__(self):
        """
        Return a string representation of the Player object.
        """
        return f"Player: {self.shortName} - ID: {self.id} - Team ID: {self.teamId} - Position: {self.position}"