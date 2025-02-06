import json

# Function to get locally stored player data
def get_stored_player_data(path):
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

# Function to locally store player data
def set_stored_player_data(data, path):
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)