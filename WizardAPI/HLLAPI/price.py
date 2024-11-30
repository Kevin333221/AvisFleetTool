import json
import datetime
from pathlib import Path

from coreFunctions import *
from config import *

# TKinter progress bar
Total_data_to_collect = 50

def get_prices_for_all_rates(rac, date, out_sta, in_sta, car_groups, progress_label=None):

    data = {}
    for car_group in car_groups:
        data[car_group] = []
    
    prices = get_prices_for_every_car_group(rac, date, out_sta, in_sta, car_groups, 1, progress_label)
    for car_group in car_groups:
        data[car_group].append(prices[car_group])
    
    prices = get_prices_for_every_car_group(rac, date, out_sta, in_sta, car_groups, 4, progress_label)
    for car_group in car_groups:
        data[car_group].append(prices[car_group])
    
    prices = get_prices_for_every_car_group(rac, date, out_sta, in_sta, car_groups, 5, progress_label)
    for car_group in car_groups:
        data[car_group].append(prices[car_group])
        
    prices = get_prices_for_every_car_group(rac, date, out_sta, in_sta, car_groups, 14, progress_label)
    for car_group in car_groups:
        data[car_group].append(prices[car_group])
        
    prices = get_prices_for_every_car_group(rac, date, out_sta, in_sta, car_groups, 21, progress_label)
    for car_group in car_groups:
        data[car_group].append(prices[car_group])
   
    final_data = []
    
    final_data.append({
        "col1": "LOR",
        "col2": data[car_groups[0]][0]["Rent Days"],
        "col3": data[car_groups[0]][1]["Rent Days"],
        "col4": data[car_groups[0]][2]["Rent Days"],
        "col5": data[car_groups[0]][3]["Rent Days"],
        "col6": data[car_groups[0]][4]["Rent Days"]
    })
    for car in car_groups:
        final_data.append({
            "col1": car,
            "col2": data[car][0]["Price"],
            "col3": data[car][1]["Price"],
            "col4": data[car][2]["Price"],
            "col5": data[car][3]["Price"],
            "col6": data[car][4]["Price"]
        })
    
    filename = Path(f"./Price/Updated_Data.csv")
    print(f"Writing data to {filename}")
    
    with open(filename, "w") as file:
        for item in final_data:
            file.write(f"{item['col1']},{item['col2']},{item['col3']},{item['col4']},{item['col5']},{item['col6']}\n")
            
    filename = Path(f"./Price/Date.txt")
    with open(filename, "w") as file:
        file.write(date)
        
         
def get_price(car_group, date, out_sta, in_sta, length):
    return xe502_cont(car_group, date, out_sta, in_sta, length)
    
def get_prices_for_x_days_for_the_whole_month(rac, car_group, month, out_sta, in_sta, length):
    
    if rac == "A":
        session_id = "A"
    else:
        session_id = "B"
    
    return_code = call_hllapi(1, session_id, 0)[3]
    if return_code != 0:
        print('Failed to connect to session')
        exit()
    
    xe502(rac)
    for i in range(1, month_to_days_in_month[month]):
        if out_sta == "TR7" and datetime.datetime({int(year)}, months_to_num[month], i).weekday() != 5 and datetime.datetime(int(year), months_to_num[month], i).weekday() != 6:
            price, rent_days, rate = get_price(car_group, f"{i:02}{month.upper()}{year2D}/1000", out_sta, in_sta, length)
            print(f"Price for a {rent_days}-day rental with car group {car_group} - {i:02}{month.upper()}{year2D} is {price} NOK")
        else:
            price, rent_days, rate = get_price(car_group, f"{i:02}{month.upper()}{year2D}/1000", out_sta, in_sta, length)
            print(f"Price for a {rent_days}-day rental with car group {car_group} - {i:02}{month.upper()}{year2D} is {price} NOK")

    disconnect_from_session(session_id)

def get_prices_for_every_car_group(rac, date, out_sta, in_sta, car_groups, length, progress_label=None):
    
    data = {}
    
    if rac == "A":
        session_id = "A"
    else:
        session_id = "B"
        
    return_code = call_hllapi(1, session_id, 0)[3]
    if return_code != 0:
        print('Failed to connect to session')
        exit()
    
    xe502(rac)
    for car_group in car_groups:
        price, rent_days, rate = get_price(car_group, date, out_sta, in_sta, length)

        data[car_group] = {
            "Price": price,
            "Date": date,
            "Rent Days": rent_days,
            "Rate": rate
        }
        
        progress_label["text"] = f"{f'{(int(progress_label["text"][:2])+1):02}'}/{Total_data_to_collect}"
        progress_label.update()
        
        # print(f"{abs(rent_days)}-day rental - {date} - car group {car_group} is {price} NOK - RATE {rate}")
    
    disconnect_from_session(session_id)
    
    return data
