import json
import pandas as pd

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

json_data = read_file('python/data/TOTAL_TOTAL.json')

# Load JSON data
data = json.loads(json_data)

# Initialize an empty DataFrame
df = pd.DataFrame()

# Process the JSON data and append to the DataFrame
for entry in data:
    month = entry['month']
    year = entry['year']
    for day, values in entry['data'].items():
        values['Day'] = day
        values['Month'] = month
        values['Year'] = year
        df = df._append(values, ignore_index=True)

# Reorder columns to have 'Day', 'Month', 'Year' first
columns_order = ['Day', 'Month', 'Year'] + [col for col in df.columns if col not in ['Day', 'Month', 'Year']]
df = df[columns_order]

# Export the DataFrame to Excel
df.to_excel('python/data/output.xlsx', index=False)