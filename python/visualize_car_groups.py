import json
import matplotlib.pyplot as plt
import numpy as np

colors = {
    "A": "blue",
    "B": "green",
    "C": "red",
    "E": "orange",
    "G": "pink",
    "H": "gray",
    "I": "olive",
    "K": "cyan",
    "M": "purple",
    "N": "brown"
}

data = json.load(open('python/data/TOTAL_TOTAL.json'))

# Function to visualize car groups for an entire month
def plot_car_groups_for_month(data, year, month):
    # Find the data for the given month and year
    for entry in data:
        if entry['year'] == year and entry['month'] == month:
            month_data = entry['data']
            break
    else:
        print("Data not found for the specified month and year")
        return

    # Extract days, car groups, and their counts
    days = sorted(month_data.keys())
    car_groups = [group for group in month_data[days[0]] if group != "Total Customers"]
    group_counts = {group: [month_data[day].get(group, 0) for day in days] for group in car_groups}

    # Plotting the stacked bar chart
    plt.figure(figsize=(12, 8))
    bottom = np.zeros(len(days))

    for group in car_groups:
        counts = group_counts[group]    
        bars = plt.bar(days, counts, bottom=bottom, label=group, color=colors[group])
        for bar, count in zip(bars, counts):
            if count > 0:
                plt.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() / 2, str(count), ha='center', va='center', fontsize=8, color='white')
        bottom += counts

    plt.xlabel('Day of Month')
    plt.ylabel('Number of Customers')
    plt.title(f'Car Group Distribution in {month} {year}')
    plt.legend(title='Car Groups', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Example usage: Plot data for June 2024
plot_car_groups_for_month(data, "2024", "JUN")

# Example usage: Plot data for July 2024
plot_car_groups_for_month(data, "2024", "JUL")

# Example usage: Plot data for August 2024
plot_car_groups_for_month(data, "2024", "AUG")