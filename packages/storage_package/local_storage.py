import json
import os.path

# Check if data is valid json
def is_json(json_data):
    try:
        json.loads(json.dumps(json_data))
    except ValueError as e:
        return False
    return True

# Create new file at path
def create_new_file(path):
    dir = path.split('/')[:-1]
    dir = '/'.join(dir)
    if not os.path.exists(dir):
        print(f"Directory not found... Creating directory: {dir}")
        os.makedirs(dir)
    file = open(path, 'w', encoding='utf-8')
    file.close

# Get full path of local database of current active sheet
def get_active_path(var_path, active_sheet):
    active_path = var_path + active_sheet.replace(' ', '_') + ".json"
    return active_path

# Function to get locally stored player data from path
def get_stored_player_data(path):
    data = {}
    print("Getting stored player data.")
    if not os.path.exists(path):
        print(f"File not found, creating new database file at {path}...", end=" ")
        create_new_file(path)
        print("SUCCESS")
    else:
        with open(path, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
            except json.decoder.JSONDecodeError:
                print("Selected file is empty.")
    return data
            
# Function to set locally stored player data at path
def set_stored_player_data(data, path):
    print("Setting stored player data.")
    with open(path, 'w', encoding='utf-8') as file:
        if is_json(data):
            json.dump(data, file, ensure_ascii=False, indent=4)
        else:
            print("Data is not valid json, please fix the data.")