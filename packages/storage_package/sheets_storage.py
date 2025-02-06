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
        return
    
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
