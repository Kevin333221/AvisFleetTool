import ctypes
import time
import json
import datetime
import itertools

# Load the HLLAPI DLL
hllapi_dll = ctypes.windll.LoadLibrary(r".\Backend\whlapi32.dll")

# Define the HLLAPI function prototype
hllapi = hllapi_dll.hllapi
hllapi.argtypes = [ctypes.POINTER(ctypes.c_short), ctypes.c_char_p, ctypes.POINTER(ctypes.c_short), ctypes.POINTER(ctypes.c_short)]
    
cursor_locations = {
    "CMD_LINE": 7,
    "x515_ACTION": 89,
    "x515_RPT": 98,
    "x515_PAGE_NUM": 474,
    "x601_ACTION": 91,
    "x801_ACTION": 171,
    
    "x313_ACTION": 170,
    "x313_MVA_NO": 330,
    "x313_REG_NO": 385,
    "x313_FLEET_CODE": 495,
    "x313_MAKE": 521,
    "x313_IGNIT_KEY": 546,
    "x313_CURR_LOC": 575,
    "x313_TRUNK_KEY": 626,
    "x313_LAST_MOVEMENT": 655,
    "x313_BODY_TYPE": 681,
    "x313_MILES": 735,
    "x313_CAR_GROUP": 761,
    "x313_LOCATION_OUT": 815,
    "x313_MOVEMENT": 895,
    "x313_DATE_OUT": 975,
    "x313_DATE_DUE": 1055,
    "x313_ACCESSORY": 1081,
    "x313_LOCATION_DUE": 1135,
    "x313_FUEL_TYPE": 1401,
    "x313_STATUS": 1615,
    "x313_HOLD_DATE": 1695,
    "x313_HOLD_REASON": 1775,
}

columns = {
    "name":     (0, 19),
    "arr_time": (20, 24),
    "flight_no":(25, 31),
    "car_grp":  (33, 34),
    "rate_code":(37, 41),
    "remarks":  (43, 65),
    "exp_lor":  (70, 73),
    "in_sta":   (74, 77)
}

months = {
    "JAN": 31,
    "FEB": 28,
    "MAR": 31,
    "APR": 30,
    "MAY": 31,
    "JUN": 30,
    "JUL": 31,
    "AUG": 31,
    "SEP": 30,
    "OCT": 31,
    "NOV": 30,
    "DEC": 31
}

num_to_months = {
    1: "JAN",
    2: "FEB",
    3: "MAR",
    4: "APR",
    5: "MAY",
    6: "JUN",
    7: "JUL",
    8: "AUG",
    9: "SEP",
    10: "OCT",
    11: "NOV",
    12: "DEC"
}

months_to_num = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12
}

stations_A = ["TOS", "TR7"]
stations_B = ["TOS", "T1Y"]

def read_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def merge_data(first, second, jsonCode):
    path = "python/data/"

    # Load the existing JSON data
    with open(path + f'{first}.json', 'r') as f:
        existing_data = json.load(f)

    # Load the new JSON data to merge
    with open(path + f'{second}.json', 'r') as f:
        new_data = json.load(f)

       # Iterate through the new data and merge it with the existing data
    for new_month_data in new_data:
        new_month = new_month_data['month']
        new_year = new_month_data['year']
        existing_month_index = next((i for i, existing_month in enumerate(existing_data) if existing_month['month'] == new_month and existing_month['year'] == new_year), None)

        if existing_month_index is not None:
            # If the month already exists in the existing data, update it
            existing_month_data = existing_data[existing_month_index]['data']
            for day, values in new_month_data['data'].items():
                if day in existing_month_data:
                    # Update existing day's values
                    for key, value in values.items():
                        if key != 'Total Customers':
                            existing_month_data[day][key] += value
                        else:
                            existing_month_data[day][key] += value
                else:
                    # Add new day's values
                    existing_month_data[day] = values
        else:
            # If the month doesn't exist in the existing data, append it
            existing_data.append(new_month_data)

    # Save the merged data to a new file
    with open(path + f'TOTAL_{jsonCode}.json', 'w') as f:
        json.dump(existing_data, f, indent=4)

def read_MVAs():
    MVAs = []
    with open("Backend/MVA.txt", "r") as file:
        lines = file.readlines()
        for line in lines:
            MVAs.append(line.strip())
    return MVAs

def call_hllapi(function_code, data, reserved):
    
    # Calculate the length of the data
    length = ctypes.c_short(len(data))
    
    # Convert the data to a byte string
    data = ctypes.c_char_p(data.encode('ascii'))
    
    # Convert the reserved value to a short
    reserved = ctypes.c_short(reserved)
    
    # Convert the function code to a short
    function_code = ctypes.c_short(function_code)

    # Call the HLLAPI function
    hllapi(ctypes.byref(function_code), data, ctypes.byref(length), ctypes.byref(reserved))

    # Return the function code, data, length and reserved values
    return function_code.value, data.value, length.value, reserved.value

def disconnect_from_session(session_id):
    return_code = call_hllapi(2, session_id, 0)
    return return_code

def send_key_sequence(keys):
    return_code = call_hllapi(3, keys, 0)
    return return_code

def x801(ped_number):
    
    send_key_sequence(f'@R@0/FOR X801@E')
    
    ready = False
    while not ready:
        ret = call_hllapi(7, "", 0)[2]
        if ret == cursor_locations["x801_ACTION"]:
            ready = True
            
    send_key_sequence(f'PDA@T{ped_number}@E')
    
    ready = False
    while not ready:
        ret = call_hllapi(7, "", 0)[2]
        if ret == cursor_locations["x801_ACTION"]:
            ready = True
            
    send_key_sequence(f'@0')

def x515(location, rac_code, date=""):
    
    if date:
        if rac_code == "A":
            send_key_sequence(f'@R@0/FOR X515@E')
        else:
            send_key_sequence(f'@R@0/FOR e515@E')
        
        ready = False
        while not ready:
            ret = call_hllapi(7, "", 0)[2]
            if ret == cursor_locations["x515_ACTION"]:
                ready = True
                
        if rac_code == "A":
            send_key_sequence(f'DSAT@T{location}@T {date}@E')
        else:
            send_key_sequence(f'DSAT@T{location}@T{date}@E')
        
        ready = False
        while not ready:
            ret = call_hllapi(7, "", 0)[2]
            if ret == cursor_locations["x515_ACTION"]:
                ready = True
                
        send_key_sequence(f'@0')
        
    else:
        if rac_code == "A":
            send_key_sequence(f'@R@0/FOR X515@E')
        else:
            send_key_sequence(f'@R@0/FOR e515@E')
        
        ready = False
        while not ready:
            ret = call_hllapi(7, "", 0)[2]
            if ret == cursor_locations["x515_ACTION"]:
                ready = True
        
        send_key_sequence(f'DSAT@T{location}@E')
        
        ready = False
        while not ready:
            ret = call_hllapi(7, "", 0)[2]
            if ret == cursor_locations["x515_ACTION"]:
                ready = True
                
        send_key_sequence(f'@0')

def e515(location, date=""):
    
    if date:
        send_key_sequence(f'@R@0/FOR e515@E')
        
        ready = False
        while not ready:
            ret = call_hllapi(7, "", 0)[2]
            if ret == cursor_locations["x515_ACTION"]:
                ready = True
                
        send_key_sequence(f'DSAT@T{location}@T {date}@E')
        
        ready = False
        while not ready:
            ret = call_hllapi(7, "", 0)[2]
            if ret == cursor_locations["x515_ACTION"]:
                ready = True
                
        send_key_sequence(f'@0')
        
    else:
        send_key_sequence(f'@R@0/FOR e515@E')
        
        ready = False
        while not ready:
            ret = call_hllapi(7, "", 0)[2]
            if ret == cursor_locations["x515_ACTION"]:
                ready = True
        
        send_key_sequence(f'DSAT@T{location}@E')
        
        ready = False
        while not ready:
            ret = call_hllapi(7, "", 0)[2]
            if ret == cursor_locations["x515_ACTION"]:
                ready = True
                
        send_key_sequence(f'@0')

def xe515_cont(date):
    send_key_sequence(f'@T@T@T@T{date}@T@F@E')
    ready = False
    while not ready:
        ret = call_hllapi(7, "", 0)[2]
        if ret == cursor_locations["x515_ACTION"]:
            ready = True

def x601(location):
    send_key_sequence(f'@R@0/FOR X601@E')
    ready = False
    while not ready:
        ret = call_hllapi(7, "", 0)[2]
        if ret == cursor_locations["x601_ACTION"]:
            ready = True
    send_key_sequence(f'NC@T{location}@E')
    
def format_data(data):
    lines = [""]

    counter = 0
    for idx, char in enumerate(data):
        if idx % 80 != 0:
            lines[counter] += char
        else:
            lines.append("")
            counter += 1

    return lines
    
def get_customers():
    
    customers = []
    isEnd = False
    customer_count = 0
    
    while not isEnd:
        isEnd = True
        
        image = call_hllapi(5, " "*1920, 0)[1]
        data = image.decode('ascii')
        lines = format_data(data)
        page = 1
        
        for line in lines[12:]:
            
            if line[0] == "3":
                press_page_up()
                page += 1
                
                # Search for the page number to be correct in order to move on
                ready = False
                while not ready:
                    ret = call_hllapi(6, f"PAGE 0{page}", 0)
                    if ret[3] == 0:
                        ready = True
                
                isEnd = False
            
            elif line[0:3] == "END":
                break
            
            elif ord(line[0]) != 32 and line[0:8] != "VERIFIED":
                
                # print(f"Adding customer {customer_count+1} to the list, page {page}")
                
                customer = {}
                for key, value in columns.items():
                    if line[value[0]:value[1]] == " ":
                        customer[key] = line[value[0]+1:value[1]+1]
                    else:
                        customer[key] = line[value[0]:value[1]]
                    
                customers.append(customer)
                customer_count += 1
    
    send_key_sequence(f"@0")
    return customers, customer_count

def press_page_up():
    send_key_sequence(f'@x')

def get_number_of_car_groups_in_month(station: str, month: str, year: str, rac_code: str):

    Days = {}
    days_in_month = months[month]
    
    # Initialize the dictionary
    for i in range(1, days_in_month+1):
        Days[f"{i:02}"] = {
            "A": 0,
            "B": 0,
            "C": 0,
            "D": 0,
            "E": 0,
            "F": 0,
            "G": 0,
            "H": 0,
            "I": 0,
            "K": 0,
            "M": 0,
            "N": 0,
            "Total Customers": 0,
        }
    
    
    x515(f"{station.upper()}", rac_code, f"01{month.upper()}{year}")
        
    customers, customer_count = get_customers()
    Days[f"01"]["Total Customers"] = customer_count
    
    # Get the number of a particular car group in that day
    for customer in customers:
        Days[f"01"][customer["car_grp"]] += 1
        
    for i in range(2, days_in_month+1):
        
        xe515_cont(f"{i:02}{month.upper()}{year}")
        customers, customer_count = get_customers()
        Days[f"{i:02}"]["Total Customers"] = customer_count
        
        for customer in customers:
            Days[f"{i:02}"][customer["car_grp"]] += 1
     
    data = {
        "month": month,
        "year": year,
        "data": Days
    }
     
    return data

def get_cursor_location():
    time.sleep(3)
    return call_hllapi(7, "", 0)

def place_cursor(location):
    call_hllapi(40, "", location)

def x313_setup():
    send_key_sequence(f'@R@0/FOR X313@E')
    
    ready = False
    while not ready:
        ret = call_hllapi(7, "", 0)[2]
        if ret == cursor_locations["x313_ACTION"]:
            ready = True
    
    send_key_sequence(f'@T')

def get_car_details(MVA: str):

    send_key_sequence(f'{MVA}@E')
     
    ready = False
    while not ready:
        ret = call_hllapi(7, "", 0)[2]
        if ret == cursor_locations["x313_MVA_NO"]:
            ready = True
    
    MVA           = call_hllapi(8, "88888888", cursor_locations["x313_MVA_NO"])[1].decode('ascii')
    REG           = call_hllapi(8, "7777777", cursor_locations["x313_REG_NO"])[1].decode('ascii')
    FLEET_CODE    = call_hllapi(8, "55555", cursor_locations["x313_FLEET_CODE"])[1].decode('ascii')
    MAKE          = call_hllapi(8, "88888888", cursor_locations["x313_MAKE"])[1].decode('ascii')
    IGNIT_KEY     = call_hllapi(8, "88888888", cursor_locations["x313_IGNIT_KEY"])[1].decode('ascii')
    CUR_LOC       = call_hllapi(8, "0000000000", cursor_locations["x313_CURR_LOC"])[1].decode('ascii').split("-")
    TRUNK         = call_hllapi(8, "7777777", cursor_locations["x313_TRUNK_KEY"])[1].decode('ascii')
    LAST_MOVEMENT = call_hllapi(8, "7777777", cursor_locations["x313_LAST_MOVEMENT"])[1].decode('ascii')
    BODY_TYPE     = call_hllapi(8, "333", cursor_locations["x313_BODY_TYPE"])[1].decode('ascii')
    MILES         = call_hllapi(8, "666666", cursor_locations["x313_MILES"])[1].decode('ascii').lstrip("0")
    CAR_GROUP     = call_hllapi(8, "4444", cursor_locations["x313_CAR_GROUP"])[1].decode('ascii')[-1]
    LOC_OUT       = call_hllapi(8, "0000000000", cursor_locations["x313_LOCATION_OUT"])[1].decode('ascii').split("-")
    MOVEMENT      = call_hllapi(8, "999999999", cursor_locations["x313_MOVEMENT"])[1].decode('ascii').strip()
    DATE_OUT      = call_hllapi(8, "7777777", cursor_locations["x313_DATE_OUT"])[1].decode('ascii').strip()
    DATE_DUE      = call_hllapi(8, "7777777", cursor_locations["x313_DATE_DUE"])[1].decode('ascii').strip()
    LOC_DUE       = call_hllapi(8, "0000000000", cursor_locations["x313_LOCATION_DUE"])[1].decode('ascii').split("-")
    ACCESSORIES   = call_hllapi(8, "00000000000000000000000000000", cursor_locations["x313_ACCESSORY"])[1].decode('ascii').split(" ")
    FUEL_TYPE     = call_hllapi(8, "1", cursor_locations["x313_FUEL_TYPE"])[1].decode('ascii')
    STATUS        = call_hllapi(8, "000000000000", cursor_locations["x313_STATUS"])[1].decode('ascii').strip()
    HOLD_DATE     = call_hllapi(8, "7777777", cursor_locations["x313_HOLD_DATE"])[1].decode('ascii').strip()
    HOLD_REASON   = call_hllapi(8, "00000000000000000000000000000", cursor_locations["x313_HOLD_REASON"])[1].decode('ascii').strip()
    
    # Filter out empty things
    ACCESSORIES = list(filter(None, ACCESSORIES))
    if LOC_OUT == ['          ']:
        LOC_OUT = ""
    if LOC_DUE == ['          ']:
        LOC_DUE = ""
    if CUR_LOC == ['          ']:
        CUR_LOC = ""
        
    if LOC_OUT == "":
        LOC_OUT = ["", ""]
    if LOC_DUE == "":
        LOC_DUE = ["", ""]
    if CUR_LOC == "":
        CUR_LOC = ["", ""]
        
    MOVEMENT = "E" + MOVEMENT
    
    newCar = Car(MVA)
    newCar.set_attributes(REG,
                          FLEET_CODE,
                          MAKE, 
                          IGNIT_KEY,
                          CUR_LOC,
                          TRUNK, 
                          LAST_MOVEMENT, 
                          BODY_TYPE, 
                          MILES, 
                          CAR_GROUP, 
                          LOC_OUT, 
                          MOVEMENT, 
                          DATE_OUT, 
                          DATE_DUE, 
                          LOC_DUE, 
                          ACCESSORIES, 
                          FUEL_TYPE, 
                          STATUS, 
                          HOLD_DATE, 
                          HOLD_REASON)
    
    return newCar

def sign_on(station, ped_number, rac_code):
    x801(ped_number)
    x601(station)
    x515(station, rac_code)

def get_cars_data():
    
    MVAs = read_MVAs()
    cars = []
    
    x313_setup()
    
    for mva in MVAs:
        newCar = get_car_details(mva)
        cars.append(newCar)

    return {"date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), "cars": [car.__dict__ for car in cars]}

def fetch_data_from_months(from_month, to_month, station: str, year, rac_code):
    
    months_data = []
    
    for i in range(months_to_num[from_month], months_to_num[to_month]+1):
        month_data = get_number_of_car_groups_in_month(station, num_to_months[i], year, rac_code)
        months_data.append(month_data)
        
    with open(f"python/data/{station.upper()}_{rac_code}.json", "w") as file:
        file.write(json.dumps(months_data))
    
def get_out_of_town_rentals_month(month, year, station, rac_code):
    
    x515(station, rac_code, f"01{month.upper()}{year}")
    
    days_in_month = months[month]
    customers, _ = get_customers()
    out_of_town_customers = []
    
    for customer in customers:
        if len(customer["in_sta"].strip()) != 0 and customer["in_sta"] != "TOS" and customer["in_sta"] != "TR7" and customer["in_sta"] != "T1Y":
            out_of_town_customers.append(customer)
    
    for i in range(2, days_in_month+1):
        
        xe515_cont(f"{i:02}{month.upper()}{year}")
        customers, _ = get_customers()
        
        for customer in customers:
            if len(customer["in_sta"].strip()) != 0 and customer["in_sta"] != "TOS" and customer["in_sta"] != "TR7" and customer["in_sta"] != "T1Y":
                new_customer = {
                    "date": f"{i:02}{month.upper()}{year}",
                    "length": customer["exp_lor"],
                    "in_sta": customer["in_sta"],
                    "out_sta": station,
                    "car_group": customer["car_grp"]
                }
                out_of_town_customers.append(new_customer)
    
    data = {
        "month": month,
        "year": year,
        "data": out_of_town_customers
    }

    return data
    
def get_AVIS_data(stations):
    
    session_id = 'H'
    return_code = call_hllapi(1, session_id, 0)[3]
    if return_code != 0:
        print('Failed to connect to session')
        exit()

    for station in stations:
        fetch_data_from_months("JUN", "AUG", station, "2024", "A")
        
    merge_data("TOS_A", "TR7_A", "A")

    # Disconnect from session 'A'
    disconnect_from_session(session_id)
    
def get_BUDGET_data(stations):
    
    session_id = 'B'
    return_code = call_hllapi(1, session_id, 0)[3]
    if return_code != 0:
        print('Failed to connect to session')
        exit()

    for station in stations:
        fetch_data_from_months("JUN", "AUG", station, "2024", "B")
        
    merge_data("TOS_B", "T1Y_B", "B")

    # Disconnect from session 'A'
    disconnect_from_session(session_id)
    
def get_total_data():
    get_AVIS_data(stations_A)
    get_BUDGET_data(stations_B)
    merge_data("TOTAL_A", "TOTAL_B", "TOTAL")

def get_out_of_town_rentals():
    
    session_id = 'H'
    return_code = call_hllapi(1, session_id, 0)[3]
    if return_code != 0:
        print('Failed to connect to session')
        exit()

    total_out_of_town_rentals = []
    
    for month in range(6, 7):
        data = get_out_of_town_rentals_month(num_to_months[month], "2024", "TOS", "A")
        total_out_of_town_rentals.append(data)

    for month in range(6, 7):
        data = get_out_of_town_rentals_month(num_to_months[month], "2024", "TR7", "A")
        total_out_of_town_rentals.append(data)
    
    # Merge and sort the data
    merged_data = {"data": []}
    for item in total_out_of_town_rentals:
        merged_data["data"] += item["data"]

    # Sort the merged data based on the "date" field
    merged_data["data"] = sorted(merged_data["data"], key=lambda x: x["date"])
    
    disconnect_from_session(session_id)
    
    session_id = 'B'
    return_code = call_hllapi(1, session_id, 0)[3]
    if return_code != 0:
        print('Failed to connect to session')
        exit()
    
    total_out_of_town_rentals = []
    
    for month in range(6, 7):
        data = get_out_of_town_rentals_month(num_to_months[month], "2024", "TOS", "B")
        total_out_of_town_rentals.append(data)
        
    for month in range(6, 7):
        data = get_out_of_town_rentals_month(num_to_months[month], "2024", "T1Y", "B")
        total_out_of_town_rentals.append(data)

    disconnect_from_session(session_id)
    
    # Merge and sort the data
    merged_data1 = {"data": []}
    for item in total_out_of_town_rentals:
        merged_data1["data"] += item["data"]
        
    # Sort the merged data based on the "date" field
    merged_data1["data"] = sorted(merged_data1["data"], key=lambda x: x["date"])
    
    # Merge the two datasets
    merged_data["data"] += merged_data1["data"]
    
    # Sort the merged data based on the "date" field
    merged_data["data"] = sorted(merged_data["data"], key=lambda x: x["date"])
    
    with open("python/data/OUT_OF_TOWN.json", "w") as file:
        file.write(json.dumps(merged_data))
    
get_out_of_town_rentals()

# get_total_data()