class Player:
    def __init__(self, id):
        self.id = id
        self.get_info_players()

    def get_info_players(self):
        url = get_api_url() + f"player/{self.id}"
        dados_players = read_api_sofascore(url, selenium=False)
        dados_players = dados_players['player']
        self.name = dados_players['name']
        self.shortName = dados_players['shortName']
        self.teamId = dados_players['team']['id']
        self.position = dados_players['position']

        if 'height' in dados_players:
            self.height = dados_players['height']

        if 'jerseyNumber' in dados_players:
            self.jerseyNumber = dados_players['jerseyNumber']

        if 'dateOfBirthTimestamp' in dados_players:
            date_of_birth = datetime.fromtimestamp(dados_players['dateOfBirthTimestamp'])
            current_date = datetime.now()
            interval_years = current_date - date_of_birth
            interval_years = current_date - date_of_birth
            self.age = int(interval_years.days/365)
        
        if 'preferredFoot' in dados_players:
            self.preferredFoot = dados_players['preferredFoot']
        
        
    def __str__(self):
        return f"Player: {self.shortName} - ID: {self.id} - Team ID: {self.teamId} - Position: {self.position}"