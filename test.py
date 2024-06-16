
# Convert a JSON to TXT file

# Example JSON
"""
    "date": "15JUN",
    "length": "014",
    "in_sta": "TOS",
    "out_sta": "OSL",
    "car_group": "E"
"""

# Example TXT
"""
   E - 15JUN - 29JUN - OSL -> TOS
"""

import json
import datetime

def convert_rental_length_to_date(date, length):
    date = datetime.datetime.strptime(date, "%d%b")
    return (date + datetime.timedelta(days=int(length))).strftime("%d%b").upper()

def json_to_txt(json_file, txt_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    
    with open(txt_file, 'w') as f:
        for car in data:
            f.write(f"{car['car_group']} - {car['date']} - {convert_rental_length_to_date(car['date'], car['length'])} - {car['out_sta']} -> {car['in_sta']}\n")
    
json_to_txt("python/data/OneWayRentals_BUDGET_SEP.json", "OneWayRentals_BUDGET_SEP.txt")