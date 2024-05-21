import matplotlib.pyplot as plt
import pandas as pd
import json

def read_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Data
data = read_file('python/data/TOTAL_TOTAL.json')

# Convert data to DataFrame
def convert_to_dataframe(data):
    records = []
    for entry in data:
        month = entry["month"]
        year = entry["year"]
        for day, values in entry["data"].items():
            record = {"Month": month, "Year": year, "Day": int(day)}
            record.update(values)
            records.append(record)
    return pd.DataFrame(records)

df = convert_to_dataframe(data)

# Create a cumulative day number for sequential plotting
df['Cumulative Day'] = 0
cumulative_days = 0
month_days_dict = {
    "JAN": 31, "FEB": 28, "MAR": 31, "APR": 30, "MAY": 31, "JUN": 30,
    "JUL": 31, "AUG": 31, "SEP": 30, "OCT": 31, "NOV": 30, "DEC": 31
}

for month in df['Month'].unique():
    month_df = df[df['Month'] == month].copy()
    month_days = month_days_dict[month]
    month_df['Cumulative Day'] = month_df['Day'] + cumulative_days
    df.loc[df['Month'] == month, 'Cumulative Day'] = month_df['Cumulative Day']
    cumulative_days += month_days

# Plotting
fig, ax = plt.subplots(figsize=(16, 8))

# Plot total customers for each day in each month
for month in df["Month"].unique():
    monthly_data = df[df["Month"] == month]
    plt.plot(monthly_data["Cumulative Day"], monthly_data["Total Customers"], label=f"{month} {monthly_data['Year'].iloc[0]}")

plt.axhline(y=10, color='b', linestyle='--', linewidth=1)
plt.axhline(y=20, color='b', linestyle='--', linewidth=1)
plt.axhline(y=30, color='b', linestyle='--', linewidth=1)

# Adjust x-axis ticks
tick_positions = [0]
tick_labels = ['']
day_count = 0
for month in df['Month'].unique():
    month_days = month_days_dict[month]
    for day in range(1, month_days + 1):
        day_count += 1
        tick_positions.append(day_count)
        tick_labels.append(str(day))
    tick_positions.append(day_count)
    tick_labels.append(month)
    
#######################################

# Enable individual days labels
plt.xticks(ticks=tick_positions, labels=tick_labels)

#######################################

plt.xlabel("Day")
plt.ylabel("Total Customers")
plt.title("Total Customers per Day for Each Month (Sequential)")

# Set y-axis ticks to display only whole numbers
plt.yticks(range(int(df['Total Customers'].max()) + 1))

plt.legend()
plt.grid(True)

plt.show()