import json

def read_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
    
data = read_file('python/data/OUT_OF_TOWN.json')

# Sort data by date
sorted_data = sorted(data["data"], key=lambda x: x["date"])

# Save sorted data to file
with open('python/data/OUT_OF_TOWN_TOTAL.txt', 'a') as file:
    for entry in sorted_data:
        file.write(f"{entry['date'][0:2]} {entry['date'][2:5]}, Car Group: {entry['car_group']} - From {entry['out_sta']} to {entry['in_sta']}\n")

# # Print sorted list of one-way rentals
# print("One-Way Rentals:")
# for entry in sorted_data:
#     print(f"{entry['date'][0:2]} {entry['date'][2:5]}, Car Group: {entry['car_group']} - From {entry['out_sta']} to {entry['in_sta']}")