### IMPORTS ###

import os.path
from dotenv import load_dotenv

import time
import datetime

import re

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from packages.player_package.player import *
from packages.storage_package.sheets_storage import *
from packages.storage_package.local_storage import *
from packages.riot_api_package.riot_api import get_riot_api_player_info, get_riot_id, get_riot_api_id

from vars.paths import *
from vars.variables import *


### VARIABLES ###

load_dotenv(ENVIRONMENT_PATH)

# Load riot api key
PARAMS = {
        'api_key': os.getenv("API_KEY")
    }

# Spreadsheet ID
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")


### FUNCTIONS ###

# Retrieve service account credientials to connect to sheets API
def auth_sheets_api(creds, creds_path, scopes):
    if os.path.exists(creds_path):
        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
    # If there are no (valid) credentials available, return an error.
    else:
        raise Exception("Invalid credentials, please provide sufficient credentials.")
    
    # Construct Resource to interact with sheets API
    service = build("sheets", "v4", credentials=creds)
    # Call the Sheets API
    sheet = service.spreadsheets()
    return sheet

# Get player names from sheet_players and add them to list
def get_player_names(sheet_players):
    player_names = []
    for player in sheet_players:
        player_names.append(player[0])
    return player_names

def get_id_data(stored_player_data, players):
    id_container = []
    print("Getting riot ids for players.")
    
    for i, player in enumerate(players):
        print(f"Retrieving ids... {i+1}/{len(stored_player_data)}", end="\r")
        player_data = stored_player_data[player]

        # Fill player data if player info contains data, otherwise return empty
        id_container.append([player_data['region'] + '/' + player_data['id'] + '-' + player_data['tag']])
        
    return id_container

# Function to get rank data from database for all players in stored_players_data
def get_rank_data(route, stored_player_data, players, queue_type, params):
    rank_container = []
    print("Getting rank data for players.")
    
    for i, player in enumerate(players):
        print(f"Updating player data and adding to sheet... {i+1}/{len(stored_player_data)}", end="\r")
        player_data = stored_player_data[player]
        # Update player information from RIOT API
        get_riot_api_player_info(route, player, player_data, queue_type, params)

        # Fill player data if player info contains data, otherwise return empty
        rank_container.append([player_data['rank']])
        
        time.sleep(1)
    print("Updating player data and adding to sheet... SUCCESS")
    return rank_container

# Synchronizes player data between google sheet and local database
def synchronize_player_data(stored_player_data, sheet_players):
    
    print("Identifying discrepancies between local database and google sheet.")

    dict_keys = list(stored_player_data.keys())

    # Remove players from local database that doesn't exist in google sheet
    for player in dict_keys:
        exists = 0
        for sheet_player_data in sheet_players:
            if player in sheet_player_data:
                player_data = stored_player_data[player]
                exists = 1
                stored_riot_id = player_data['region'] + '/' + player_data['id'] + '-' + player_data['tag']
                if player_data['puuid'] != '':
                    print(f"Player {player}'s puuid found in local database, verifying database riot id...", end=" ")
                    get_riot_api_id(ROUTE_ALT, player, player_data, PARAMS)
                    print("SUCCESS")
                elif player_data['puuid'] == '':
                    print(f"Player {player} has no puuid, readding to local database...", end=" ")
                    del stored_player_data[player]
                    print("SUCCESS")
                elif stored_riot_id != sheet_player_data[6].replace('%20',' '):
                    print(f"Riot id mismatch for player {player}, readding to local database...", end=" ")
                    del stored_player_data[player]
                    print("SUCCESS")
                break
        
        if exists == 0:
            print(f"Player {player} in local database not found, removing from local database...", end=" ")
            del stored_player_data[player]
            print("SUCCESS")
    
    # Add all missing players from google sheet that doesn't exist in local database
    for player in sheet_players:
        try:
            stored_player_data[player[0]]
        except:
            print(f"Player: {player[0]} not found, adding to database...", end=" ")
            id_container = get_riot_id(player[6])
            player_dict = createPlayerDict(player[0], id_container[0], id_container[1], id_container[2])
            stored_player_data = updatePlayerDict(stored_player_data, player_dict)
            print("SUCCESS")

    print("Database and google sheet has been synchronized.")

# Function to update players and stats to local storage and google sheets
def update_player_data(sheet, sheet_id, sheet_range, stored_player_data, sheet_players, local_path, id_column, rank_column, route, queue_type, params):
    # Get player names in order of google sheet
    players = get_player_names(sheet_players)
    
    # Get and save ids and ranks for players
    ids = get_id_data(stored_player_data, players)
    ranks = get_rank_data(route, stored_player_data, players, queue_type, params)

    # Update player information in local storage
    set_stored_player_data(stored_player_data, local_path)

    # Get id and rank range for specific sheet
    sheet_range_split = sheet_range.split("!")
    id_range = sheet_range_split[0] + "!" + re.sub("[^0-9:]", id_column, sheet_range_split[1])
    rank_range = sheet_range_split[0] + "!" + re.sub("[^0-9:]", rank_column, sheet_range_split[1])

    # Update player information in google sheets
    set_sheet_data(sheet, sheet_id, id_range, ids)
    set_sheet_data(sheet, sheet_id, rank_range, ranks)


### Main program ###

def main():
    print("Connecting to spreadsheet...", end=" ")
    creds = None
    sheet = auth_sheets_api(creds, CREDS_PATH, SCOPES)
    print("SUCCESS")
    try:
        while (True):
            print(f"Update started at {datetime.datetime.now().strftime("%H:%M CET %x")}")
            print(f"Retrieving player count and sheets...")
            [active_sheets, sheet_ranges] = get_ranges(sheet, SPREADSHEET_ID, COUNT_FULL, RANGE_PLAYERS_START, RANGE_PLAYERS_END)
            # Wait 5 seconds to collect ranges
            time.sleep(5)
            
            for i, active_sheet in enumerate(active_sheets):
                print(f"Updating player data in sheet: [{active_sheet}]")
                # Get all players from Google sheets
                print("Getting player data from spreadsheet...", end=" ")
                sheet_players = get_sheet_data(sheet, SPREADSHEET_ID, sheet_ranges[i])
                print("SUCCESS")
                print(f"{len(sheet_players)} player(s) found in sheet.")
                active_path = get_active_path(LOCAL_STORAGE_PATH, active_sheet)
        
                stored_player_data = get_stored_player_data(active_path)
                # Syncronize sheet and local database
                synchronize_player_data(stored_player_data, sheet_players)
                # Update Google sheets based off of data acquired from riot API
                update_player_data(sheet, SPREADSHEET_ID, sheet_ranges[i], stored_player_data, sheet_players, active_path, PLAYER_ID_COLUMN, PLAYER_RANK_COLUMN, ROUTE, QUEUE_TYPE, PARAMS)
                print(f"Sheet: [{active_sheet}] has finished updating at {datetime.datetime.now().strftime("%H:%M CET %x")}")
                
            
            # Update update time in google sheets
            current_time = [[datetime.datetime.now().strftime("%H:%M CET %x")]]
            set_sheet_data(sheet, SPREADSHEET_ID, TIME_FULL, current_time)
            print(f"Update finished at {current_time[0][0]}")

            time.sleep(600)
    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()
