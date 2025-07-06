### GOOGLE SHEETS VARIABLES ###

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


### RIOT API VARIABLES ###

# Riot API queries
ROUTE = "europe"

# Ranked solo queue ID and type
QUEUE_TYPE = "RANKED_SOLO_5x5"


### SHEET VARIABLES

# Spreadsheet ranges
RANGE_PLAYERS_START = "A2"
RANGE_PLAYERS_END = "I"

# Player count sheet
COUNT_SHEET = "Player Count"
COUNT_RANGE = "A2:B7"
COUNT_FULL = COUNT_SHEET + "!" + COUNT_RANGE

# Player rank column
PLAYER_RANK_COLUMN = "F"

# Player id column
PLAYER_ID_COLUMN = "G"

# Time sheet
TIME_SHEET = "Welcome!"
TIME_CELL = "L16:M16"
TIME_FULL = TIME_SHEET + "!" + TIME_CELL