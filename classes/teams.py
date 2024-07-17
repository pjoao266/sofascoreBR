import sys
sys.path.append("../")
from datetime import datetime
from classes.utils import get_api_url, read_api_sofascore, get_bin_image
from SQLconfig.config_mysql import mydb

class Team:
    def __init__(self, id, tournament_id, season_id):
        """
        Initializes a Team object with the given id, tournament_id, and season_id.

        Args:
        - id (int): The id of the team.
        - tournament_id (int): The id of the tournament the team belongs to.
        - season_id (int): The id of the season the team belongs to.
        """
        self.id = id
        self.tournament_id = tournament_id
        self.season_id = season_id
        
        
    def get_infos_team(self):
        """
        Retrieves the information of the team from the API and updates the object's attributes.

        This method makes a request to the API to get the information of the team with the given id.
        It updates the object's attributes with the retrieved information, including the team's name,
        tournament_id, and season_id. If the tournament_id or season_id is not provided during object
        initialization, it will be retrieved from the API.

        Note: This method requires the 'get_api_url' and 'read_api_sofascore' functions from the 'utils' module.

        Returns:
        None
        """
        url = get_api_url() + f"team/{self.id}"
        infos_team = read_api_sofascore(url, selenium=False)
        self.name = infos_team['team']['name']
        if self.tournament_id == None or self.season_id == None:
            self.tournament_id = infos_team['team']['primaryUniqueTournament']['id']
            url = get_api_url() + f"unique-tournament/{self.tournament_id}/seasons"
            infos_tournament = read_api_sofascore(url, selenium=False)['seasons']
            self.season_id = infos_tournament[0]['id']
            
    def save(self, mydb):
        """
        Saves the team object to the database.

        This method checks if the team already exists in the database by querying the 'team' table
        with the team's id, tournament_id, and season_id. If the team does not exist, it inserts a new
        row into the 'team' table with the team's id, name, tournament_id, season_id, and image.

        Note: This method requires the 'get_bin_image' function from the 'utils' module.

        Args:
        - mydb: The database connection object.

        Returns:
        None
        """
        sql_check = f"SELECT * FROM team WHERE id = {int(self.id)} AND id_tournament = {int(self.tournament_id)} AND id_season = {int(self.season_id)}"
        mycursor = mydb.cursor()
        mycursor.execute(sql_check)
        myresult = mycursor.fetchall()
        mycursor.close()
        if len(myresult) <= 0:
            sql = f"INSERT INTO team (id, name, id_tournament, id_season, image) VALUES (%s, %s, %s, %s, %s)"
            image = get_bin_image(self.id, 'team')
            val = (int(self.id), self.name, int(self.tournament_id), int(self.season_id), image)
            mycursor = mydb.cursor()
            mycursor.execute(sql, val)
            mydb.commit()
            mycursor.close()
        
    def __str__(self):
        """
        Returns a string representation of the Team object.

        Returns:
        A string representation of the Team object in the format:
        "Team: {name} - ID: {id} - Tournament ID: {tournament_id} - Season ID: {season_id}"
        """
        return f"Team: {self.name} - ID: {self.id} - Tournament ID: {self.tournament_id} - Season ID: {self.season_id}"