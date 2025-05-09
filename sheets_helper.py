import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# Define the scopes
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Connect to Google Sheets
def connect_to_sheets(json_keyfile, sheet_name):
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
    client = gspread.authorize(creds)
    return client.open(sheet_name)

# Append nutrition entry
def append_nutrition_data(sheet, data):
    worksheet = sheet.worksheet("Nutrition")
    worksheet.append_row(list(data.values()))

# Append food scan entry
def append_food_data(sheet, data):
    worksheet = sheet.worksheet("FoodScans")
    worksheet.append_row([data["Name"], data["Meal Timing"], str(data["Nutrition Table"])])
