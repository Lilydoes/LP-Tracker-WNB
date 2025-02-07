# Create body to insert data into google sheets through its API
def create_body_container(range, values):
    body_container = {
        'valueInputOption': 'USER_ENTERED',
        'data': [
            {
                'range': range,
                'values': values
            }
        ]
    }
    return body_container

# Function to get data from google sheets
def get_sheet_data(sheet, sheet_id, sheet_range):
    result = (
        sheet.values()
        .get(spreadsheetId=sheet_id, range=sheet_range)
        .execute()
    )
    values = result.get("values", [])
    
    if not values:
        print("No data found.")
    
    return values

# Function to fill out range with data on google sheets
def set_sheet_data(sheet, sheet_id, sheet_range, sheet_data):
    body_container = create_body_container(sheet_range, sheet_data)

    request = (
        sheet.values()
        .batchUpdate(spreadsheetId=sheet_id, body=body_container)
    )
    response = request.execute()

    return response

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