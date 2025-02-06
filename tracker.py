### THINGS TO GET DONE ###
# 1. create function to syncronize local database and sheets
# 1.1 add players not in local database
# 1.2 remove players from local database that doesn't exist on sheets
# 2. Modify update_player_data so it adds ranks to sheets only
# 3. Save the player data to the local database after all each sheet has updated
##########################

### IMPORTS ###

import os.path
from dotenv import load_dotenv

import time
import datetime

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from packages.player_package.player import *
from packages.storage_package.sheets_storage import *
from packages.storage_package.local_storage import *
from packages.riot_api_package.riot_api import get_riot_api_player_info


### VARIABLES ###

# Variable path
VAR_PATH = "var/"

# Load enviroment variables
ENVIRONMENT_PATH = VAR_PATH + "keys.env"
load_dotenv(ENVIRONMENT_PATH)

# Paths to Google sheets credentials and log in token
TOKEN_PATH = VAR_PATH + "token.json"
CREDS_PATH = VAR_PATH + "service_credentials.json"

# Path to locally stored player data
LOCAL_DB_PATH = VAR_PATH + "players.json"

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# Load riot api key
PARAMS = {
        'api_key': os.getenv("API_KEY")
    }

# Spreadsheet ID
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# Riot API queries
ROUTE = "europe"

# Spreadsheet ranges
RANGE_PLAYERS_START = "A2"
RANGE_PLAYERS_END = "I"

# Player count sheet
COUNT_SHEET = "Player Count"
COUNT_RANGE = "A2:B7"
COUNT_FULL = COUNT_SHEET + "!" + COUNT_RANGE

# Time sheet
TIME_SHEET = "Welcome"
TIME_CELL = "L16:M16"
TIME_FULL = TIME_SHEET + "!" + TIME_CELL

# Ranked solo queue ID and type
QUEUE_TYPE = "RANKED_SOLO_5x5"


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

# Function to get area of spreadsheet containing player information
def get_ranges(sheet, sheet_id, count_range, range_start, range_column_end):
    sheets = []
    all_ranges = []
    # Get end row with player info
    container = get_sheet_data(sheet, sheet_id, count_range)
    start_row = int(range_start[1:])
    
    for sheet in container:
        end_row = str(start_row + int(sheet[1]) - 1)
        range_players_end = range_column_end + end_row
        sheets.append(sheet[0])
        all_ranges.append(sheet[0] + "!" + range_start + ":" + range_players_end)

    return [sheets, all_ranges]

# Function to extract riot id and region from op.gg urls
def get_riot_id(url):
    temp_container = []
    player_container = []

    temp_container = url.replace('https://www.op.gg/summoners/','').split('/')
    player_container.append(temp_container[0])
    temp_container = temp_container[1].replace('%20',' ').split('-')
    player_container.append(temp_container[0])
    player_container.append(temp_container[1])

    return player_container

# Function to get rank data from database for all players in stored_players_data
def get_rank_data(route, players, stored_players_data, queue_type, params):
    rank_container = []
    for player, i in players:
        print(f"Updating player data and adding to sheet... {i+1}/{len(players)}", end="\r")
        player_data = stored_players_data[player]
        # Update player information from RIOT API
        get_riot_api_player_info(route, player, player_data, queue_type, params)

        # Fill player data if player info contains data, otherwise return empty
        if player_data['rank'] != '':
            rank_container.append(player_data['rank'])
        else:
            print("")
            print(f"Failed to fetch rank for {player}, please update manually.")
        time.sleep(1)
        
    return rank_container

# MAKE THIS FUNCTION WORK PLS

# Function to update players and stats to local storage and google sheets
def update_player_data(sheet, sheet_players):
    player_count = len(sheet_players)
    stored_player_data = get_stored_player_data(LOCAL_DB_PATH)
    empty_rows = []

    get_rank_data(sheet_players[i], stored_player_data)

    for i in range(0, player_count):
        if not sheet_players[i]:
            print(f"Row {i+1} empty...")
            empty_rows.append(i)
        
        
    
    if empty_rows:
        print("Removing empty rows from sheet...")
        for i in empty_rows:
            print(f"Removing row {i}...")
            del sheet_players[i]
        print("Empty rows removed.")
    
    # Sort players based on LP gained
    #sheet_players.sort(key=lambda x: (int(x[6]), -int(x[8])), reverse=True)

    # Update player information in local storage
    set_stored_player_data(stored_player_data, LOCAL_DB_PATH)

    # Update player information in google sheets
    set_sheet_data(sheet, SPREADSHEET_ID, range_players, sheet_players)

### Main program ###

def main():
    print("Connecting to spreadsheet...", end=" ")
    creds = None
    sheet = auth_sheets_api(creds, CREDS_PATH, SCOPES)
    print("SUCCESS")
    try:
        while (True):
            print(f"Update started at {[datetime.datetime.now().strftime("%H:%M CET %x")]}")
            try:
                print(f"Retrieving player count and sheets...")
                [active_sheets, sheet_ranges] = get_ranges(sheet, COUNT_FULL, RANGE_PLAYERS_START, RANGE_PLAYERS_END)
                for active_sheet, i in active_sheets:
                    print(f"Updating player data in sheet: {active_sheet}")
                    # Get all players from Google sheets
                    print("Getting player data from spreadsheet...", end=" ")
                    sheet_players = get_sheet_data(sheet, SPREADSHEET_ID, sheet_ranges[i])
                    print("SUCCESS")
                    print(f"{len(sheet_players)} player(s) found in sheet.")
                    # Update Google sheets based off of data acquired from riot API
                    update_player_data(sheet, sheet_players)
                    print(f"Sheet: {active_sheet} has finished updating at {[datetime.datetime.now().strftime("%H:%M CET %x")]}")
                    
                    
                    time.sleep(120)
            except:
                print("Error countered, retying in 5 minutes...")
                time.sleep(300)
            # Update update time in google sheets
            current_time = [[datetime.datetime.now().strftime("%H:%M CET %x")]]
            set_sheet_data(sheet, SPREADSHEET_ID, TIME_FULL, current_time)
            print(f"Update finished at {current_time}")
    
    except HttpError as err:
        print(err)


if __name__ == "__main__":
    main()
