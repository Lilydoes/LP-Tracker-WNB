import requests
from urllib.parse import urlencode

# Numerical rank map
ROMAN_TO_INT = {'I':1, 'II':2, 'III':3, 'IV':4}

# Tiers where rank shouldn't be included
NO_RANK = ['Master', 'Grandmaster', 'Challenger']

# Function to extract riot id and region from op.gg urls
def get_riot_id(url):
    temp_container = []
    player_container = []

    temp_container = url.replace('https://www.op.gg/summoners/','').split('/')
    if temp_container[0] == 'eune':
        temp_container[0] == 'eun'
    player_container.append(temp_container[0])
    temp_container = temp_container[1].replace('%20',' ').split('-')
    player_container.append(temp_container[0])
    player_container.append(temp_container[1])
    return player_container

# Function for a get request to the riot api
def get_riot_api_request(url, params):
    try:
        response = requests.get(url, params=urlencode(params))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        print(f'Issue getting account information from API')
        return None

# Get summoner id from riot api
def get_riot_api_summoner_id(url_prefix, stored_player_data, params):
    id = stored_player_data['id']
    tag = stored_player_data['tag']

    get_account_request_url = url_prefix[0] + f'/riot/account/v1/accounts/by-riot-id/{id}/{tag}'
    player_account = get_riot_api_request(get_account_request_url, params)
    if player_account != None:
        puuid = player_account['puuid']
        get_summoner_request_url = url_prefix[1] + f'/lol/summoner/v4/summoners/by-puuid/{puuid}'
        player_summoner = get_riot_api_request(get_summoner_request_url, params)

        summoner_id = player_summoner['id']

        stored_player_data['summoner_id'] = summoner_id
        


# Function to get player info from riot API
def get_riot_api_player_info(route, player, stored_player_data, queue_type, params):
    region = stored_player_data['region']
    
    url_prefix = []
    url_prefix.append(f'https://{route}.api.riotgames.com')
    url_prefix.append(f'https://{region}1.api.riotgames.com')    

    # Attempt to fetch encrypted summoner id for player if not found
    if stored_player_data['summoner_id'] == '':
        print(f"Player {player}'s summoner id not found, retrieving from riot and adding to local storage...", end=' ')
        get_riot_api_summoner_id(url_prefix, stored_player_data, params)
        print('SUCCESS')
    
    # Attempt to fetch rank if encrypted summoner id for player exists
    if stored_player_data['summoner_id'] != '':
        get_league_request_url = url_prefix[1] + f"/lol/league/v4/entries/by-summoner/{stored_player_data['summoner_id']}"
        player_ranks = get_riot_api_request(get_league_request_url, params)
        
        player_solo_rank = []
        for i in range(0, len(player_ranks)):
            if player_ranks[i]['queueType'] == queue_type:
                player_solo_rank = player_ranks[i]
                break
        
        if player_solo_rank == []:
            combined_rank = "Complete placements"
        else:
            tier = player_solo_rank['tier'].casefold().capitalize()
            rank = ''
            if tier not in NO_RANK:
                rank = str(ROMAN_TO_INT[player_solo_rank['rank']]) + ' '
            lp = str(player_solo_rank['leaguePoints']) + ' LP'
            
            combined_rank = tier + ' ' + rank + lp
            if stored_player_data['region'] != 'euw':
                if stored_player_data['region'] == ('eun'):
                    combined_rank += " (" + stored_player_data['region'].upper() + "e)"
                else:
                    combined_rank += " (" + stored_player_data['region'].upper() + ")"
            
            
                
        stored_player_data['rank'] = combined_rank
    else:
        stored_player_data['rank'] = "Error fetching rank, check riot id..."
    