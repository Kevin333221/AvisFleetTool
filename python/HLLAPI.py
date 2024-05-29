import ctypes
import time
import json
import math
import datetime
from config import *
from car import Car

# Load the HLLAPI DLL
hllapi_dll = ctypes.windll.LoadLibrary(r".\python\whlapi32.dll")

# Define the HLLAPI function prototype
hllapi = hllapi_dll.hllapi
hllapi.argtypes = [ctypes.POINTER(ctypes.c_short), ctypes.c_char_p, ctypes.POINTER(ctypes.c_short), ctypes.POINTER(ctypes.c_short)]

def wait_for_ready(loc):
    ready = False
    while not ready:
        ret = call_hllapi(7, "", 0)[2]
        if ret == cursor_locations[loc]:
            ready = True

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
    with open("python/data/MVA.txt", "r") as file:
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

def connect_to_session(session_id):
    return_code = call_hllapi(1, session_id, 0)[3]
    if return_code != 0:
        print('Failed to connect to session')
        exit()
        
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

def xe515(station, rac_code, date=""):
    
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
            send_key_sequence(f'DSAT@T{station}@T {date}@E')
        else:
            send_key_sequence(f'DSAT@T{station}@T{date}@E')
        
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
        
        send_key_sequence(f'DSAT@T{station}@E')
        
        ready = False
        while not ready:
            ret = call_hllapi(7, "", 0)[2]
            if ret == cursor_locations["x515_ACTION"]:
                ready = True
                
        send_key_sequence(f'@0')

def xe515_cont(date):
    send_key_sequence(f'@T@T@T@T{date}@T@F@E')
    wait_for_ready("x515_ACTION")

def xe515_cont_with_station(station, date):
    send_key_sequence(f'@T@T@T{station}@T{date}@T@F@E')
    wait_for_ready("x515_ACTION")

def xe502(rac):
    if rac == "A":
        send_key_sequence(f'@R@0/FOR X502@E')
    else:
        send_key_sequence(f'@R@0/FOR e502@E')
    wait_for_ready("x502_PAC")

def xe502_cont(car_group: str, date: str, out_sta: str, in_sta: str, length: int):
    
    in_date = (f"{int(date[0:2])+length:02}") + date[2:5].upper() + "24" + "/" + date[8:]
    
    if int(in_date[0:2]) > months[date[2:5].upper()]:
        in_date = (f"{months[date[2:5].upper()]:02}") + date[2:5].upper() + "24" + "/" + date[8:]
    
    send_key_sequence(f'RS@T{out_sta}@T@T{date}WI@T@T{car_group}@T@T{in_sta}@T@T{in_date}@E')
    
    ready = False
    while not ready:
        ret = call_hllapi(7, "", 0)[2]
        if ret == cursor_locations["x502_PAC"]:
            ready = True    
        
    send_key_sequence(f'@x')
    
    ready = False
    ret = 0
    while not ready:
        ret = call_hllapi(6, f"TOTL=", 0)
        if ret[3] == 0:
            ready = True
    
    price = call_hllapi(8, "0000000000000000000000", ret[2]+8)[1].decode('ascii').strip()
    
    send_key_sequence(f'@0@T')
    return price, int(in_date[0:2]) - int(date[0:2])

def x502_see_reservation(reservation_number):
    send_key_sequence(f"DR")
    move_cursor(cursor_locations["x502_CUSTOMER_NAME"])
    send_key_sequence(f"R/{reservation_number}@F@E")
    wait_for_ready("x502_PAC")

def x502_get_reservation_info():
    WIZ = call_hllapi(8, "666666", cursor_locations["x502_WIZ"])[1].decode('ascii').strip()
    STATION_OUT = call_hllapi(8, "55555", cursor_locations["x502_STATION_OUT"])[1].decode('ascii').strip()
    CTR = call_hllapi(8, "22", cursor_locations["x502_CTR"])[1].decode('ascii').strip()
    DATE_OUT = call_hllapi(8, "000000000000", cursor_locations["x502_DATE_OUT"])[1].decode('ascii').strip()
    DAY_OUT = call_hllapi(8, "333", cursor_locations["x502_DATE_OUT"] + 15)[1].decode('ascii').strip()    
    FLIGHT_NO = call_hllapi(8, "666666", cursor_locations["x502_FLIGHT_NO"])[1].decode('ascii').strip()
    CUPON = call_hllapi(8, "7777777", cursor_locations["x502_CUPON"])[1].decode('ascii').strip()
    CAR_GROUP = call_hllapi(8, "999999999", cursor_locations["x502_CAR_GROUP"])[1].decode('ascii').strip()
    DELIVERY = call_hllapi(8, "1", cursor_locations["x502_DELIVERY"])[1].decode('ascii').strip()
    STATION_IN = call_hllapi(8, "55555", cursor_locations["x502_STATION_IN"])[1].decode('ascii').strip()
    COLLECTION = call_hllapi(8, "1", cursor_locations["x502_COLLECTION"])[1].decode('ascii').strip()
    DATE_IN = call_hllapi(8, "000000000000", cursor_locations["x502_DATE_IN"])[1].decode('ascii').strip()
    DAY_IN = call_hllapi(8, "333", cursor_locations["x502_DATE_IN"] + 15)[1].decode('ascii').strip()
    CUSTOMER_NAME = call_hllapi(8, "000000000000000000000000000000", cursor_locations["x502_CUSTOMER_NAME"])[1].decode('ascii').strip()
    RATE = call_hllapi(8, "0000000000", cursor_locations["x502_RATE"])[1].decode('ascii').strip()
    SAC = call_hllapi(8, "22", cursor_locations["x502_SAC"])[1].decode('ascii').strip()
    DATE_OF_BIRTH = call_hllapi(8, "7777777", cursor_locations["x502_DATE_OF_BIRTH"])[1].decode('ascii').strip()
    INSURANCE_CODES = call_hllapi(8, "4444", cursor_locations["x502_INSURANCE_CODES"])[1].decode('ascii').strip()
    CCI = call_hllapi(8, "000000000000000", cursor_locations["x502_CCI"])[1].decode('ascii').strip()
    CID = call_hllapi(8, "000000000000000000000000", cursor_locations["x502_CID"])[1].decode('ascii').strip()
    METH_PAY = call_hllapi(8, "22", cursor_locations["x502_METH_PAY"])[1].decode('ascii').strip()
    CEX = call_hllapi(8, "55555", cursor_locations["x502_EXPIRATION_DATE"])[1].decode('ascii').strip()
    NC = call_hllapi(8, "000000000000000000000000000000", cursor_locations["x502_N/C"])[1].decode('ascii').strip()
    ADDR1 = call_hllapi(8, "000000000000000000000000000000", cursor_locations["x502_ADDR1"])[1].decode('ascii').strip()
    ADDR2 = call_hllapi(8, "000000000000000000000000000000", cursor_locations["x502_ADDR2"])[1].decode('ascii').strip()
    ADDR3 = call_hllapi(8, "000000000000000000000000000000", cursor_locations["x502_ADDR3"])[1].decode('ascii').strip()
    LICENSE = call_hllapi(8, "00000000000000000000000000", cursor_locations["x502_LICENSE"])[1].decode('ascii').strip()
    SOURCE = call_hllapi(8, "0000000000000000000000", cursor_locations["x502_SOURCE"])[1].decode('ascii').strip()
    CONTACT = call_hllapi(8, "000000000000000000000000000000", cursor_locations["x502_CONTACT"])[1].decode('ascii').strip()
    REMARKS = call_hllapi(8, "0000000000000000000000000", cursor_locations["x502_REMARKS"])[1].decode('ascii').strip()
    AWD = call_hllapi(8, "999999999", cursor_locations["x502_AWD"])[1].decode('ascii').strip()
    TA = call_hllapi(8, "0000000000", cursor_locations["x502_T/A"])[1].decode('ascii').strip()
    FREQUENT_TRAVEL_NUMBER = call_hllapi(8, "0000000000000000000000000", cursor_locations["x502_FREQUENT_TRAVEL_NUMBER"])[1].decode('ascii').strip()
    
    
    RES = "Not Found"
    ready = False
    while not ready:
        ret = call_hllapi(6, f"RES NO. ", 0)
        if ret[3] == 0:
            RES = call_hllapi(8, "00000000000000", ret[2]+8)[1].decode('ascii').strip()
            ready = True
    
    return {
        "RES": RES,
        "WIZARD_NR": WIZ,
        "STATION_OUT": STATION_OUT,
        "CTR": CTR,
        "DATE_OUT": DATE_OUT,
        "DAY_OUT": DAY_OUT,
        "FLIGHT_NO": FLIGHT_NO,
        "CUPON": CUPON,
        "CAR_GROUP": CAR_GROUP,
        "DELIVERY": DELIVERY,
        "STATION_IN": STATION_IN,
        "COLLECTION": COLLECTION,
        "DATE_IN": DATE_IN,
        "DAY_IN": DAY_IN,
        "CUSTOMER_NAME": CUSTOMER_NAME,
        "RATE": RATE,
        "SAC": SAC,
        "DATE_OF_BIRTH": DATE_OF_BIRTH,
        "INSURANCE_CODES": INSURANCE_CODES,
        "CCI": CCI,
        "CID": CID,
        "METH_PAY": METH_PAY,
        "CEX": CEX,
        "N/C": NC,
        "ADDR1": ADDR1,
        "ADDR2": ADDR2,
        "ADDR3": ADDR3,
        "LICENSE": LICENSE,
        "SOURCE": SOURCE,
        "CONTACT": CONTACT,
        "REMARKS": REMARKS,
        "AWD": AWD,
        "T/A": TA,
        "FREQUENT_TRAVEL_NUMBER": FREQUENT_TRAVEL_NUMBER
    }

def xe601(location, rac):
    
    if rac == "A":
        send_key_sequence(f'@R@0/FOR X601@E')
    else:
        send_key_sequence(f'@R@0/FOR e601@E')
        
    ready = False
    while not ready:
        ret = call_hllapi(7, "", 0)[2]
        if ret == cursor_locations["x601_ACTION"]:
            ready = True
            
    send_key_sequence(f'NC@T{location}@E')
    
    ready = False
    while not ready:
        ret = call_hllapi(7, "", 0)[2]
        if ret == cursor_locations["x601_ACTION"]:
            ready = True
        
    send_key_sequence(f'@0')
    
def wztdoc(rac, station, rpt_type="RO", date=""):
    
    send_key_sequence(f'@R@0/FOR WZTDOC@E')
    wait_for_ready("WZTDOC_ACTION")
    
    if date:
        send_key_sequence(f"DS{rpt_type}{station}@T{rac}{date}@E")
    else:
        send_key_sequence(f"DS{rpt_type}{station}@T{rac}@E")
    
    wait_for_ready("WZTDOC_ACTION")
    time.sleep(0.5)

def wztdoc_cont(date):
    move_cursor(142)
    send_key_sequence(f"{date}@E")
    wait_for_ready("WZTDOC_ACTION")

def get_wztdoc_data(date, station):
    records = []
    isEnd = False
    
    while not isEnd:
        isEnd = True
        
        image = call_hllapi(5, " "*1920, 0)[1]
        data = image.decode('ascii')
        lines = format_data(data)
        
        page = 1
        for line in lines[9:]:
            
            if line[0:3] == "31-":
                press_page_up()
                page += 1
                
                # Search for the page number to be correct in order to move on
                ready = False
                while not ready:
                    ret = call_hllapi(6, f"PAGE:   {page}", 0)
                    if ret[3] == 0:
                        ready = True
            
                isEnd = False
            
            elif line[0:3] == "30-" or line[0:3] == "19-":
                break
            
            elif ord(line[0]) != 32 and line[0:5] != "TOTAL":
                record = {}
                record["Date"] = date
                record["RA"] = line[0:9]
                mva = line[17:25]
                if mva[0] == " ":
                    mva = "0" + mva[1:]
                record["MVA"] = mva
                name = line[26:56].strip().split(",")
                record["Checkout Location"] = station
                record["Customer_Lastname"] = name[0]
                record["Customer_Firstname"] = name[1]
                record["Checkout_Time"] = line[57:61]
                records.append(record)
                
    send_key_sequence(f"@0")
    return records

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
    page = 1
    
    while not isEnd:
        isEnd = True
        
        image = call_hllapi(5, " "*1920, 0)[1]
        data = image.decode('ascii')
        lines = format_data(data)
        
        for line in lines[12:]:
            
            if line[0] == "3":
                page += 1
                press_page_up()
                
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
    
    
    xe515(f"{station.upper()}", rac_code, f"01{month.upper()}{year}")
        
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
    connect_to_session("A")
    time.sleep(3)
    print(call_hllapi(7, "", 0))
    disconnect_from_session("A")

def move_cursor(location):
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
    
    if rac_code == "A":
        session_id = 'A'
    else:
        session_id = 'B'
        
    return_code = call_hllapi(1, session_id, 0)[3]
    if return_code != 0:
        print('Failed to connect to session')
        exit()
    
    x801(ped_number)
    xe601(station, rac_code)
    xe515(station, rac_code)
    
    disconnect_from_session(session_id)

def get_cars_data():
    
    MVAs = read_MVAs()
    cars = []
    
    session_id = 'A'
    return_code = call_hllapi(1, session_id, 0)[3]
    if return_code != 0:
        print('Failed to connect to session')
        exit()
    
    x313_setup()
    
    for mva in MVAs:
        newCar = get_car_details(mva)
        cars.append(newCar)

    disconnect_from_session(session_id)

    return {"date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), "cars": [car.__dict__ for car in cars]}

def fetch_data_from_months(from_month, to_month, station: str, year, rac_code):
    
    months_data = []
    
    for i in range(months_to_num[from_month], months_to_num[to_month]+1):
        month_data = get_number_of_car_groups_in_month(station, num_to_months[i], year, rac_code)
        months_data.append(month_data)
        
    with open(f"python/data/{station.upper()}_{rac_code}.json", "w") as file:
        file.write(json.dumps(months_data))
    
def get_out_of_town_rentals_month(month, year, station, rac_code):
    
    xe515(station, rac_code, f"01{month.upper()}{year}")
    
    days_in_month = months[month]
    out_of_town_customers = []
    
    for i in range(1, days_in_month+1):
        
        xe515_cont(f"{i:02}{month.upper()}{year}")
        customers, _ = get_customers()
        
        for customer in customers:
            if len(customer["in_sta"].strip()) != 0 and customer["in_sta"] not in stations_A and customer["in_sta"] not in stations_B:
                new_customer = {
                    "date": f"{i:02}{month.upper()}",
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
    
    for station in stations:
        fetch_data_from_months("JUN", "AUG", station, year, "A")
        
    merge_data("TOS_A", "TR7_A", "A")
    
def get_BUDGET_data(stations):

    for station in stations:
        fetch_data_from_months("JUN", "AUG", station, year, "B")
        
    merge_data("TOS_B", "T1Y_B", "B")
    
def get_total_data():
    
    session_id = 'A'
    return_code = call_hllapi(1, session_id, 0)[3]
    if return_code != 0:
        print('Failed to connect to session')
        exit()
        
    get_AVIS_data(stations_A)
    
    disconnect_from_session(session_id)
    
    session_id = 'B'
    return_code = call_hllapi(1, session_id, 0)[3]
    if return_code != 0:
        print('Failed to connect to session')
        exit()
        
    get_BUDGET_data(stations_B)
    
    disconnect_from_session(session_id)
    
    merge_data("TOTAL_A", "TOTAL_B", "TOTAL")

def get_out_of_town_rentals(month):
      
    session_id = 'A'
    connect_to_session(session_id)

    total_out_of_town_rentals = []
    
    for m in range(6, months_to_num[month]+1):
        for station in stations_A:
            data = get_out_of_town_rentals_month(num_to_months[m], year, station, "A")
            total_out_of_town_rentals.append(data)

    # Merge and sort the data
    merged_data = {"data": []}
    for item in total_out_of_town_rentals:
        merged_data["data"] += item["data"]
    
    with open(f"python/data/Enveisleier_AVIS_{month}.json", "w") as file:
        file.write(json.dumps(merged_data))
    
    disconnect_from_session(session_id)
    
    session_id = 'B'
    connect_to_session(session_id)
    
    total_out_of_town_rentals = []
    
    for m in range(6, months_to_num[month]+1):
        for station in stations_B:
            data = get_out_of_town_rentals_month(num_to_months[m], year, station, "B")
            total_out_of_town_rentals.append(data)

    disconnect_from_session(session_id)
    
    # Merge and sort the data
    merged_data1 = {"data": []}
    for item in total_out_of_town_rentals:
        merged_data1["data"] += item["data"]

    with open(f"python/data/Enveisleier_BUDGET_{month}.json", "w") as file:
        file.write(json.dumps(merged_data1))        

    # Merge and sort the data
    total_merged_data = {"data": []}
    total_merged_data["data"] = merged_data["data"] + merged_data1["data"]
        
    # Function to convert date format
    def parse_date(date_str):
        return datetime.datetime.strptime(date_str, "%d%b")

    total_merged_data["data"] = sorted(total_merged_data["data"], key=lambda x: parse_date(x["date"]))
    
    with open(f"python/data/Enveisleier_{month}.json", "w") as file:
        file.write(json.dumps(total_merged_data))
        
    # Write the data to a txt file
    with open(f"python/data/Enveisleier_{month}.txt", "w") as file:
        for item in total_merged_data["data"]:
            file.write(f"{item['date']} - {item['out_sta']} to {item['in_sta']} - {item['length']} - {item['car_group']}\n")
    
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
    for i in range(1, months[month]):
        if out_sta == "TR7" and datetime.datetime({int(year)}, months_to_num[month], i).weekday() != 5 and datetime.datetime(int(year), months_to_num[month], i).weekday() != 6:
            price, rent_days = get_price(car_group, f"{i:02}{month.upper()}{year2D}/1000", out_sta, in_sta, length)
            print(f"Price for a {rent_days}-day rental with car group {car_group} - {i:02}{month.upper()}{year2D} is {price} NOK")
        else:
            price, rent_days = get_price(car_group, f"{i:02}{month.upper()}{year2D}/1000", out_sta, in_sta, length)
            print(f"Price for a {rent_days}-day rental with car group {car_group} - {i:02}{month.upper()}{year2D} is {price} NOK")

    disconnect_from_session(session_id)

def get_prices_for_every_car_group(rac, date, out_sta, in_sta, car_groups, length):
        
    
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
        price, rent_days = get_price(car_group, date, out_sta, in_sta, length)
        print(f"{rent_days}-day rental - {date} - car group {car_group} is {price} NOK")
    
    disconnect_from_session(session_id)

def get_all_customers_from_month(station, rac, month, year):
    
    xe515(station, rac, f"01{month.upper()}{year}")
    customers = []
    for i in range(1, months[month]+1):
        xe515_cont(f"{i:02}{month.upper()}{year}")
        customer, _ = get_customers()
        
        for c in customer:
            
            if station != "TO0" or station != "TO7":
                c["car_type"] = "Person"
            else:
                c["car_type"] = "Van"
                
            c["rac"] = rac
            c["out_station"] = station
            c["out_date"] = f"{i:02}"
            c["month"] = month
            c["year"] = year
            customers.append(c)
    
    return customers

def get_all_customers_from_given_months(fleet_code, months):
    
    session_id = "A"
    connect_to_session(session_id)
        
    xe601(fleet_code, "A")

    total_customers = []

    for station in stations_A:
        for month in months:
            customers = get_all_customers_from_month(station, "A", month, year)
            total_customers += customers

    disconnect_from_session(session_id)

    session_id = "B"
    return_code = call_hllapi(1, session_id, 0)[3]
    if return_code != 0:
        print('Failed to connect to session')
        exit()

    xe601(fleet_code, "B")

    for station in stations_B:
        for month in months:
            customers = get_all_customers_from_month(station, "B", month, year)
            total_customers += customers

    disconnect_from_session(session_id)

    with open(f"python/data/TOTAL_JUN_AUG.json", "w") as file:
        file.write(json.dumps(total_customers))

def save_on_rent_and_available_cars(available_cars, on_rent_cars, day, month):
    with open("python/data/available_cars.json", "r") as file:
        data = json.load(file)
        
    data.append({
        "date": f"{day:02} {num_to_months[month].upper()}",
        "available_cars": available_cars,
        "on_rent_cars": len(on_rent_cars)
    })
    
    with open("python/data/available_cars.json", "w") as file:
        file.write(json.dumps(data))

def get_amount_of_cars_in_month(desired_date, starting_amount):
    
    def update_cars_on_rent(c_on_rent, c_available):
        new_cars_on_rent = []
        for c in c_on_rent:
            if c == 0:
                c_available += 1
            else:
                new_cars_on_rent.append(c-1)
        return new_cars_on_rent, c_available
    
    # Initialize the available cars array
    with open("python/data/available_cars.json", "w") as file:
        file.write(json.dumps([]))
    
    cars_on_rent = []
    cars_currently_available = starting_amount
    
    todays_day = int(f"{datetime.datetime.now().day:02}")
    todays_month = datetime.datetime.now().month
    
    desired_day = int(desired_date[0:2])
    desired_month = months_to_num[desired_date[2:5].upper()]
    
    session_id = "A"
    connect_to_session(session_id)
    xe515("TOS", "A", f"{todays_day}{num_to_months[todays_month]}{year}")
    disconnect_from_session(session_id)
    
    session_id = "B"
    connect_to_session(session_id)
    xe515("TOS", "B", f"{todays_day}{num_to_months[todays_month]}{year}")
    disconnect_from_session(session_id)
    
    # Current Month
    for i in range(todays_day, months[num_to_months[todays_month]]+1):
        
        session_id = "A"
        connect_to_session(session_id)
        cars_on_rent, cars_currently_available = update_cars_on_rent(cars_on_rent, cars_currently_available)
        
        # AVIS
        for station in stations_A:
            xe515_cont_with_station(station, f"{i:02}{num_to_months[todays_month].upper()}{year}")
            
            customers, _ = get_customers()
            for customer in customers:
                cars_currently_available -= 1
                if customer["in_sta"] != "TOS" and customer["in_sta"] != "TR7" and customer["in_sta"] != "T1Y" and customer["in_sta"] != "   ":
                    pass
                else:
                    cars_on_rent.append(int(customer["exp_lor"])-1)
        
        disconnect_from_session(session_id)
        
        session_id = "B"
        call_hllapi(1, session_id, 0)[3]
            
        # BUDGET
        for station in stations_B:
            xe515_cont_with_station(station, f"{i:02}{num_to_months[todays_month].upper()}{year}")
            
            customers, _ = get_customers()
            for customer in customers:
                cars_currently_available -= 1
                if customer["in_sta"] != "TOS" and customer["in_sta"] != "TR7" and customer["in_sta"] != "T1Y" and customer["in_sta"] != "   ":
                    pass
                else:
                    cars_on_rent.append(int(customer["exp_lor"])-1)
        
        disconnect_from_session(session_id)
        
        save_on_rent_and_available_cars(cars_currently_available, cars_on_rent, i, todays_month)
    
    # Next Months
    for i in range(todays_month+1, desired_month+1):
        for j in range(1, months[num_to_months[i]]+1):
            
            if i == desired_month and j == desired_day + 1:
                break
            
            session_id = "A"
            connect_to_session(session_id)
            
            cars_on_rent, cars_currently_available = update_cars_on_rent(cars_on_rent, cars_currently_available)
            
            # AVIS
            for station in stations_A:
                xe515_cont_with_station(station, f"{j:02}{num_to_months[i].upper()}2024")
                
                customers, _ = get_customers()
                for customer in customers:
                    cars_currently_available -= 1
                    if customer["in_sta"] != "TOS" and customer["in_sta"] != "TR7" and customer["in_sta"] != "T1Y" and customer["in_sta"] != "   ":
                        pass
                    else:
                        cars_on_rent.append(int(customer["exp_lor"])-1)
            
            disconnect_from_session(session_id)
            
            session_id = "B"
            call_hllapi(1, session_id, 0)[3]
                
            # BUDGET
            for station in stations_B:
                xe515_cont_with_station(station, f"{j:02}{num_to_months[i].upper()}2024")
                
                customers, _ = get_customers()
                for customer in customers:
                    cars_currently_available -= 1
                    if customer["in_sta"] != "TOS" and customer["in_sta"] != "TR7" and customer["in_sta"] != "T1Y" and customer["in_sta"] != "   ":
                        pass
                    else:
                        cars_on_rent.append(int(customer["exp_lor"])-1)
            
            disconnect_from_session(session_id)
            
            save_on_rent_and_available_cars(cars_currently_available, cars_on_rent, j, i)

def get_previous_RAs(rac, station, num_of_days):
    
    months_back = 0
    day = datetime.datetime.now().day
    month = f"{num_to_months[(datetime.datetime.now().month-months_back) % 12]}"
    
    wztdoc(rac, station, "RO", f"{day-1}{month.upper()}{year}")
    
    data = []
    
    for i in range(num_of_days):
        day -= 1
        
        if day < 1:
            months_back += 1
            day = int(f"{months[num_to_months[(datetime.datetime.now().month-months_back) % 12]]:02}")
        
        month = f"{num_to_months[(datetime.datetime.now().month-months_back) % 12]}"
        
        wztdoc_cont(f"{day:02}{month.upper()}{year}")
        data.append(get_wztdoc_data(f"{day:02}{month.upper()}{year}", station))
    
    return data

def find_all_one_way_rentals_to_TOS_and_T1Y_for_all_of_Norway(month, in_stations):
    
    session_id = "A"
    connect_to_session(session_id)
        
    back_rentals = []
    
    for station in all_budget_stations:
        xe515(station, "B", f"01{month.upper()}{year}")
        days_in_month = months[month]
        
        for i in range(1, days_in_month+1):
            xe515_cont(f"{i:02}{month.upper()}{year}")
            customers, _ = get_customers()
            
            for customer in customers:
                if customer["in_sta"] in in_stations:
                    new_customer = {
                        "date": f"{i:02}{month.upper()}",
                        "length": customer["exp_lor"],
                        "in_sta": customer["in_sta"],
                        "out_sta": station,
                        "car_group": customer["car_grp"]
                    }
                    back_rentals.append(new_customer)
    
    back_rentals.sort(key=lambda x: x["date"])
    
    with open(f"python/data/OneWayRentals_BUDGET_{month}.json", "w") as file:
        file.write(json.dumps(back_rentals))
        
    disconnect_from_session(session_id)

def x606():
    send_key_sequence(f'@R@0/FOR X606@E')
    wait_for_ready("x606_ACTION")
    send_key_sequence(f'DS')

def x606_cont(mva):
    send_key_sequence(f"{mva}@E")
    wait_for_ready("x606_ACTION")
    send_key_sequence(f'@T')

def x203():
    send_key_sequence(f'@R@0/FOR X203@E')
    wait_for_ready("x203_RA")
    
def x203_cont(RA):
    move_cursor(cursor_locations["x203_AUTH_OUT"])
    send_key_sequence(f'@F')
    move_cursor(cursor_locations["x203_RA"])
    send_key_sequence(f'{RA}@E')
    wait_for_ready("x203_RA")

def is_valid_ra(RA):
    x203_cont(RA)
    RA_FOUND = True
    tries = 25
    while RA_FOUND and tries > 0:
        ret = call_hllapi(6, f"RENTAL AGREEMENT WAS NOT FOUND", 0)
        if ret[3] == 0:
            RA_FOUND = False
        tries -= 1
    return RA_FOUND

def _get_RA_info_x203():
    RA = call_hllapi(8, "999999999", cursor_locations["x203_RA"])[1].decode('ascii').strip()
    # ACT = call_hllapi(8, "333", cursor_locations["x203_ACT"])[1].decode('ascii').strip()
    # AGENT_ID = call_hllapi(8, "55555", cursor_locations["x203_AGENT_ID"])[1].decode('ascii').strip()
    # PIN = call_hllapi(8, "55555", cursor_locations["x203_PIN"])[1].decode('ascii').strip()
    MVA = call_hllapi(8, "88888888", cursor_locations["x203_MVA"])[1].decode('ascii').strip()
    CCI = call_hllapi(8, "000000000000000", cursor_locations["x203_CCI"])[1].decode('ascii').strip()
    CUSTOMER_NAME = call_hllapi(8, "000000000000000000000000000000", cursor_locations["x203_CUSTOMER_NAME"])[1].decode('ascii').strip()
    SOURCE = call_hllapi(8, "000000000000000000000000", cursor_locations["x203_SOURCE"])[1].decode('ascii').strip()
    CUPON = call_hllapi(8, "7777777", cursor_locations["x203_CUPON"])[1].decode('ascii').strip()
    NC = call_hllapi(8, "000000000000000000000000000000", cursor_locations["x203_N/C"])[1].decode('ascii').strip()
    CONTACT = call_hllapi(8, "0000000000000000000000000000000", cursor_locations["x203_CONTACT"])[1].decode('ascii').strip()
    METH_PAY = call_hllapi(8, "22", cursor_locations["x203_METH_PAY"])[1].decode('ascii').strip()
    ADDR1 = call_hllapi(8, "000000000000000000000000000000", cursor_locations["x203_ADDR1"])[1].decode('ascii').strip()
    REMARKS = call_hllapi(8, "0000000000000000000000000", cursor_locations["x203_REMARKS"])[1].decode('ascii').strip()
    INSURANCE_CODES = call_hllapi(8, "4444", cursor_locations["x203_INSURANCE_CODES"])[1].decode('ascii').strip()
    ADDR2 = call_hllapi(8, "000000000000000000000000000000", cursor_locations["x203_ADDR2"])[1].decode('ascii').strip()
    LICENSE = call_hllapi(8, "00000000000000000000000000", cursor_locations["x203_LICENSE"])[1].decode('ascii').strip()
    DC = call_hllapi(8, "4444", cursor_locations["x203_D/C"])[1].decode('ascii').strip()
    ADDR3 = call_hllapi(8, "000000000000000000000000000000", cursor_locations["x203_ADDR3"])[1].decode('ascii').strip()
    CID = call_hllapi(8, "00000000000000000000000000", cursor_locations["x203_CID"])[1].decode('ascii').strip()
    TAX = call_hllapi(8, "666666", cursor_locations["x203_TAX"])[1].decode('ascii').strip()
    KILOMETER_OUT = call_hllapi(8, "666666", cursor_locations["x203_KILOMETER_OUT"])[1].decode('ascii').strip()
    STATION_OUT = call_hllapi(8, "55555", cursor_locations["x203_STATION_OUT"])[1].decode('ascii').strip()
    DATE_OUT = call_hllapi(8, "000000000000", cursor_locations["x203_DATE_OUT"])[1].decode('ascii').strip()
    AUTH_OUT = call_hllapi(8, "0000000000", cursor_locations["x203_AUTH_OUT"])[1].decode('ascii').strip()
    FUEL_OUT = call_hllapi(8, "22", cursor_locations["x203_FUEL_OUT"])[1].decode('ascii').strip()
    # REA = call_hllapi(8, "22", cursor_locations["x203_REA"])[1].decode('ascii').strip()
    DELIVERY = call_hllapi(8, "88888888", cursor_locations["x203_DELIVERY"])[1].decode('ascii').strip()
    KILOMETER_IN = call_hllapi(8, "666666", cursor_locations["x203_KILOMETER_IN"])[1].decode('ascii').strip()
    STATION_IN = call_hllapi(8, "55555", cursor_locations["x203_STATION_IN"])[1].decode('ascii').strip()
    DATE_IN = call_hllapi(8, "000000000000", cursor_locations["x203_DATE_IN"])[1].decode('ascii')
    AUTH_IN = call_hllapi(8, "0000000000", cursor_locations["x203_AUTH_IN"])[1].decode('ascii').strip()
    BFL = call_hllapi(8, "88888888", cursor_locations["x203_BFL"])[1].decode('ascii').strip()
    COLLECTION = call_hllapi(8, "88888888", cursor_locations["x203_COLLECTION"])[1].decode('ascii').strip()
    AMOUNT_DUE = call_hllapi(8, "0000000000000", cursor_locations["x203_AMOUNT_DUE"])[1].decode('ascii').strip()
    # FO = call_hllapi(8, "0000000000000", cursor_locations["x203_F/O"])[1].decode('ascii').strip()
    AWD = call_hllapi(8, "999999999", cursor_locations["x203_AWD"])[1].decode('ascii').strip()
    # UPGRADE = call_hllapi(8, "55555", cursor_locations["x203_GRP/$$"])[1].decode('ascii').strip()
    ADJUSMENT = call_hllapi(8, "88888888", cursor_locations["x203_ADJUSTMENT"])[1].decode('ascii').strip()
    RATE = call_hllapi(8, "666666", cursor_locations["x203_RATE"])[1].decode('ascii').strip()
    OWFMISC = call_hllapi(8, "0000000000000000", cursor_locations["x203_OWF/MISC"])[1].decode('ascii').strip()
    DATE_OF_BIRTH = call_hllapi(8, "7777777", cursor_locations["x203_DATE_OF_BIRTH"])[1].decode('ascii').strip()
    # NEW_MVA = call_hllapi(8, "88888888", cursor_locations["x203_NEW_MVA"])[1].decode('ascii').strip()
    FREQUENT_TRAVEL_NUMBER = call_hllapi(8, "0000000000000000000000000", cursor_locations["x203_FREQUENT_TRAVEL_NUMBER"])[1].decode('ascii').strip()
    TER = call_hllapi(8, "999999999", cursor_locations["x203_TER"])[1].decode('ascii').strip()
    PASSPORT_NUMBER = call_hllapi(8, "000000000000000", cursor_locations["x203_PASSPORT_NUMBER"])[1].decode('ascii').strip()
    
    AGENT_ID = call_hllapi(8, "55555", cursor_locations["x203_AGENT_ID"])[1].decode('ascii').strip()
    MODEL = call_hllapi(8, "4444", cursor_locations["x203_MODEL"])[1].decode('ascii').strip()
    CAR_GROUP = call_hllapi(8, "1", cursor_locations["x203_CAR_GROUP"])[1].decode('ascii').strip()
    CAR_OWNER = call_hllapi(8, "55555", cursor_locations["x203_CAR_OWNER"])[1].decode('ascii').strip()
    REG_NO = call_hllapi(8, "55555", cursor_locations["x203_REG_NO"])[1].decode('ascii').strip()
    
    record = {
        "RA_TYPE": "X203",
        "RA": RA,
        # "ACT": ACT,
        # "AGENT_ID": AGENT_ID,
        # "PIN": PIN,
        "MVA": MVA,
        "REG": REG_NO,
        "MODEL": MODEL,
        "CAR_GROUP": CAR_GROUP,
        "CAR_OWNER": CAR_OWNER,
        
        "CUSTOMER_NAME": CUSTOMER_NAME,
        "DATE_OF_BIRTH": DATE_OF_BIRTH,
        "ADDR1": ADDR1,
        "ADDR2": ADDR2,
        "ADDR3": ADDR3,
        "CONTACT": CONTACT,
        "LICENSE": LICENSE,
        "PASSPORT_NUMBER": PASSPORT_NUMBER,
        "N/C": NC,
        
        "STATION_OUT": STATION_OUT,
        "DATE_OUT": DATE_OUT,
        "KILOMETER_OUT": KILOMETER_OUT,
        "FUEL_OUT": FUEL_OUT,
        
        "STATION_IN": STATION_IN,
        "DATE_IN": DATE_IN,
        "KILOMETER_IN": KILOMETER_IN,
        "BFL": BFL,
        
        "AUTH_IN": AUTH_IN,
        "AUTH_OUT": AUTH_OUT,
        
        "AMOUNT_DUE": AMOUNT_DUE,
        "INSURANCE_CODES": INSURANCE_CODES,
        "REMARKS": REMARKS,
        "RATE": RATE,
        "CID": CID,
        "METH_PAY": METH_PAY,
        "AWD": AWD,
        "CCI": CCI,
        
        "AGENT_ID": AGENT_ID,
        "SOURCE": SOURCE,
        "CUPON": CUPON,
        "D/C": DC,
        "TAX": TAX,
        "DELIVERY": DELIVERY,
        "COLLECTION": COLLECTION,
        "ADJUSMENT": ADJUSMENT,
        "OWF/MISC": OWFMISC,
        "FREQUENT_TRAVEL_NUMBER": FREQUENT_TRAVEL_NUMBER,
        "TER": TER,
        # "REA": REA,
        # "F/O": FO,
        # "NEW_MVA": NEW_MVA,
        # "GRP/$$": UPGRADE,
    }
    
    return record

def _get_RA_info_x806():
    
    RA = call_hllapi(8, "88888888", cursor_locations["x806_RA"])[1].decode('ascii').strip()
    ACT = call_hllapi(8, "333", cursor_locations["x806_ACT"])[1].decode('ascii').strip()
    AGENT_ID = call_hllapi(8, "55555", cursor_locations["x806_AGENT_ID"])[1].decode('ascii').strip()
    MVA = call_hllapi(8, "88888888", cursor_locations["x806_MVA"])[1].decode('ascii').strip()
    CCI = call_hllapi(8, "000000000000000", cursor_locations["x806_CCI"])[1].decode('ascii').strip()
    DIV = call_hllapi(8, "1", cursor_locations["x806_DIV"])[1].decode('ascii').strip()
    CUSTOMER_NAME = call_hllapi(8, "000000000000000000000000000000", cursor_locations["x806_CUSTOMER_NAME"])[1].decode('ascii').strip()
    SOURCE = call_hllapi(8, "000000000000000000000000", cursor_locations["x806_SOURCE"])[1].decode('ascii').strip()
    CUPON = call_hllapi(8, "7777777", cursor_locations["x806_CUPON"])[1].decode('ascii').strip()
    NC = call_hllapi(8, "000000000000000000000000000000", cursor_locations["x806_N/C"])[1].decode('ascii').strip()
    CONTACT = call_hllapi(8, "0000000000000000000000000000000", cursor_locations["x806_CONTACT"])[1].decode('ascii').strip()
    METH_PAY = call_hllapi(8, "22", cursor_locations["x806_METH_PAY"])[1].decode('ascii').strip()
    ADDR1 = call_hllapi(8, "000000000000000000000000000000", cursor_locations["x806_ADDR1"])[1].decode('ascii').strip()
    REMARKS = call_hllapi(8, "0000000000000000000000000", cursor_locations["x806_REMARKS"])[1].decode('ascii').strip()
    INSURANCE_CODES = call_hllapi(8, "4444", cursor_locations["x806_INSURANCE_CODES"])[1].decode('ascii').strip()
    ADDR2 = call_hllapi(8, "000000000000000000000000000000", cursor_locations["x806_ADDR2"])[1].decode('ascii').strip()
    LICENSE = call_hllapi(8, "00000000000000000000000000", cursor_locations["x806_LICENSE"])[1].decode('ascii').strip()
    DC = call_hllapi(8, "4444", cursor_locations["x806_D/C"])[1].decode('ascii').strip()
    ADDR3 = call_hllapi(8, "000000000000000000000000000000", cursor_locations["x806_ADDR3"])[1].decode('ascii').strip()
    CID = call_hllapi(8, "00000000000000000000000000", cursor_locations["x806_CID"])[1].decode('ascii').strip()
    TAX = call_hllapi(8, "666666", cursor_locations["x806_TAX"])[1].decode('ascii').strip()
    KILOMETER_OUT = call_hllapi(8, "666666", cursor_locations["x806_KILOMETER_OUT"])[1].decode('ascii').strip()
    STATION_OUT = call_hllapi(8, "55555", cursor_locations["x806_STATION_OUT"])[1].decode('ascii').strip()
    DATE_OUT = call_hllapi(8, "000000000000", cursor_locations["x806_DATE_OUT"])[1].decode('ascii').strip()
    AUTH_OUT = call_hllapi(8, "0000000000", cursor_locations["x806_AUTH_OUT"])[1].decode('ascii').strip()
    FUEL_OUT = call_hllapi(8, "22", cursor_locations["x806_FUEL_OUT"])[1].decode('ascii').strip()
    REA = call_hllapi(8, "22", cursor_locations["x806_REA"])[1].decode('ascii').strip()
    DELIVERY = call_hllapi(8, "88888888", cursor_locations["x806_DELIVERY"])[1].decode('ascii').strip()
    KILOMETER_IN = call_hllapi(8, "666666", cursor_locations["x806_KILOMETER_IN"])[1].decode('ascii').strip()
    STATION_IN = call_hllapi(8, "55555", cursor_locations["x806_STATION_IN"])[1].decode('ascii').strip()
    DATE_IN = call_hllapi(8, "000000000000", cursor_locations["x806_DATE_IN"])[1].decode('ascii')
    AUTH_IN = call_hllapi(8, "0000000000", cursor_locations["x806_AUTH_IN"])[1].decode('ascii').strip()
    BFL = call_hllapi(8, "88888888", cursor_locations["x806_BFL"])[1].decode('ascii').strip()
    COLLECTION = call_hllapi(8, "88888888", cursor_locations["x806_COLLECTION"])[1].decode('ascii').strip()
    AMOUNT_DUE = call_hllapi(8, "0000000000000", cursor_locations["x806_AMOUNT_DUE"])[1].decode('ascii').strip()
    FO = call_hllapi(8, "0000000000000", cursor_locations["x806_F/O"])[1].decode('ascii').strip()
    AWD = call_hllapi(8, "999999999", cursor_locations["x806_AWD"])[1].decode('ascii').strip()
    ADJUSMENT = call_hllapi(8, "88888888", cursor_locations["x806_ADJUSTMENT"])[1].decode('ascii').strip()
    RATE = call_hllapi(8, "666666", cursor_locations["x806_RATE"])[1].decode('ascii').strip()
    OWFMISC = call_hllapi(8, "0000000000000000", cursor_locations["x806_OWF/MISC"])[1].decode('ascii').strip()
    DATE_OF_BIRTH = call_hllapi(8, "7777777", cursor_locations["x806_DATE_OF_BIRTH"])[1].decode('ascii').strip()
    NEW_MVA = call_hllapi(8, "88888888", cursor_locations["x806_NEW_MVA"])[1].decode('ascii').strip()
    FREQUENT_TRAVEL_NUMBER = call_hllapi(8, "0000000000000000000000000", cursor_locations["x806_FREQUENT_TRAVEL_NUMBER"])[1].decode('ascii').strip()
    TER = call_hllapi(8, "999999999", cursor_locations["x806_TER"])[1].decode('ascii').strip()
    PASSPORT_NUMBER = call_hllapi(8, "000000000000000", cursor_locations["x806_PASSPORT_NUMBER"])[1].decode('ascii').strip()
    
    record = {
        "RA_TYPE": "X806",
        "RA": RA,
        "ACT": ACT,
        "AGENT_ID": AGENT_ID,
        "MVA": MVA,
        "CCI": CCI,
        "DIV": DIV,
        "CUSTOMER_NAME": CUSTOMER_NAME,
        "SOURCE": SOURCE,
        "CUPON": CUPON,
        "N/C": NC,
        "CONTACT": CONTACT,
        "METH_PAY": METH_PAY,
        "ADDR1": ADDR1,
        "REMARKS": REMARKS,
        "INSURANCE_CODES": INSURANCE_CODES,
        "ADDR2": ADDR2,
        "LICENSE": LICENSE,
        "D/C": DC,
        "ADDR3": ADDR3,
        "CID": CID,
        "TAX": TAX,
        "KILOMETER_OUT": KILOMETER_OUT,
        "STATION_OUT": STATION_OUT,
        "DATE_OUT": DATE_OUT,
        "AUTH_OUT": AUTH_OUT,
        "FUEL_OUT": FUEL_OUT,
        "REA": REA,
        "DELIVERY": DELIVERY,
        "KILOMETER_IN": KILOMETER_IN,
        "STATION_IN": STATION_IN,
        "DATE_IN": DATE_IN,
        "AUTH_IN": AUTH_IN,
        "BFL": BFL,
        "COLLECTION": COLLECTION,
        "AMOUNT_DUE": AMOUNT_DUE,
        "F/O": FO,
        "AWD": AWD,
        "ADJUSMENT": ADJUSMENT,
        "RATE": RATE,
        "OWF/MISC": OWFMISC,
        "DATE_OF_BIRTH": DATE_OF_BIRTH,
        "NEW_MVA": NEW_MVA,
        "FREQUENT_TRAVEL_NUMBER": FREQUENT_TRAVEL_NUMBER,
        "TER": TER,
        "PASSPORT_NUMBER": PASSPORT_NUMBER
    }
    
    return record

def x806():
    send_key_sequence(f'@R@0/FOR X806@E')
    wait_for_ready("x806_RA")

def x806_cont(ra):
    wait_for_ready("x806_RA")
    send_key_sequence(f"{ra}@E")
    wait_for_ready("x806_RA")

def get_car_info_x606():
    MVA = call_hllapi(8, "88888888", cursor_locations["x606_MVA"])[1].decode('ascii')
    VIN = call_hllapi(8, "00000000000000000", cursor_locations["x606_VIN"])[1].decode('ascii')
    REG = call_hllapi(8, "999999999", cursor_locations["x606_REG"])[1].decode('ascii')[2:]
    MAKE = call_hllapi(8, "4444", cursor_locations["x606_MAKE"])[1].decode('ascii')
    BODY_TYPE = call_hllapi(8, "333", cursor_locations["x606_BODY_TYPE"])[1].decode('ascii')
    MILES = call_hllapi(8, "666666", cursor_locations["x606_MILES"])[1].decode('ascii').lstrip("0")
    COLOR = call_hllapi(8, "333" , cursor_locations["x606_COLOR"])[1].decode('ascii')
    IGNIT_KEY = call_hllapi(8, "88888888", cursor_locations["x606_IGNIT_KEY"])[1].decode('ascii')
    TRUNK_KEY = call_hllapi(8, "88888888", cursor_locations["x606_TRUNK_KEY"])[1].decode('ascii').strip()
    ACCESSORIES = call_hllapi(8, "00100100100100100100100100100", cursor_locations["x606_ACCESSORIES"])[1].decode('ascii').split(" ")
    LOCATION = call_hllapi(8, "7777777", cursor_locations["x606_LOCATION"])[1].decode('ascii').split(" ")
    DEL_DATE = call_hllapi(8, "7777777", cursor_locations["x606_DEL_DATE"])[1].decode('ascii')
    REG_DATE = call_hllapi(8, "7777777", cursor_locations["x606_REG_DATE"])[1].decode('ascii')
    MODEL_YEAR = call_hllapi(8, "22", cursor_locations["x606_MODEL_YEAR"])[1].decode('ascii')
    REMARKS = call_hllapi(8, "00000000000000000000", cursor_locations["x606_REMARKS"])[1].decode('ascii')
    OWNER = call_hllapi(8, "55555", cursor_locations["x606_OWNER"])[1].decode('ascii')
    ACCESSORIES = list(filter(None, ACCESSORIES))
    
    newCar = {
        "MVA": MVA,
        "VIN": VIN,
        "REG": REG,
        "MAKE": MAKE,
        "BODY_TYPE": BODY_TYPE,
        "MILES": MILES,
        "COLOR": COLOR,
        "IGNIT_KEY": IGNIT_KEY,
        "TRUNK_KEY": TRUNK_KEY,
        "ACCESSORIES": ACCESSORIES,
        "LOCATION": LOCATION,
        "DEL_DATE": DEL_DATE,
        "REG_DATE": REG_DATE,
        "MODEL_YEAR": MODEL_YEAR,
        "REMARKS": REMARKS,
        "OWNER": OWNER
    }
    
    return newCar

def get_all_x606_cars():
    session_id = "A"
    connect_to_session(session_id)

    MVAs = read_MVAs()
    x606()
    cars = []

    for mva in MVAs:
        x606_cont(mva)
        car = get_car_info_x606()
        cars.append(car)

    with open("python/data/x606_64442_CARS.json", "w") as file:
        file.write(json.dumps(cars))

    disconnect_from_session(session_id)

def get_previous_RA_info(rac, station, length):
    days = get_previous_RAs(rac, station, length)
    
    all_RAs = []
    x806_RAs = []

    if len(days) == 0:
        return all_RAs
    
    x203()
    for day in days:
        for customer in day:
            x203_cont(customer["RA"])
            valid = is_valid_ra(customer["RA"])
            if valid:
                record = _get_RA_info_x203()
                all_RAs.append(record)
            else:
                x806_RAs.append(customer["RA"])
                
    # if len(x806_RAs) == 0:
    #     return all_RAs
    
    # x806()
    # for ra in x806_RAs:
    #     x806_cont(ra)
    #     record = _get_RA_info_x806()
    #     all_RAs.append(record)
    
    return all_RAs

def wzttrc():
    send_key_sequence(f'@R@0/FOR WZTTRC@E')
    wait_for_ready("WZTTRC_ACTION")

def get_wzttrc_data(MVA):
    records = []
    isEnd = False
    page = 1
    
    while not isEnd:
        isEnd = True
        
        image = call_hllapi(5, " "*1920, 0)[1]
        data = image.decode('ascii')
        lines = format_data(data)
        reg = call_hllapi(8, "7777777", cursor_locations["WZTTRC_REG_NO"])[1].decode('ascii')
        model = call_hllapi(8, "88888888", cursor_locations["WZTTRC_MODEL"])[1].decode('ascii')
        
        prev_MOVEMENT = ("", "")
        for line in lines[9:]:
            
            if line[40] == "3":
                page += 1
                press_page_up()
                
                # Search for the page number to be correct in order to move on
                ready = False
                while not ready:
                    ret = call_hllapi(6, f"PAGE:   {page}", 0)
                    if ret[3] == 0:
                        ready = True
                    ret = call_hllapi(6, f"PAGE:  {page}", 0)
                    if ret[3] == 0:
                        ready = True

                isEnd = False
            
            elif line[40] == ".":
                break
            
            elif ord(line[1]) != 32:
                
                if prev_MOVEMENT[0] == "CHECK-OUT":
                    check_in_movement = prev_MOVEMENT[1]
                else:
                    check_in_movement = line[51:61].strip()
                
                record = {
                    "MVA": MVA,
                    "REG": reg,
                    "MODEL": model,
                    "MOVEMENT_TYPE": line[0:10].strip(),
                    "LOCATION": line[13:17].strip(),
                    "DATE": line[20:29].strip(),
                    "TIME": line[34:39],
                    "MILES": line[43:49].strip(),
                    "MOVEMENT": check_in_movement,
                    "RAC": line[65:66],
                    "REMARKS": line[68:73].strip()
                }
                prev_MOVEMENT = (record["MOVEMENT_TYPE"], record["MOVEMENT"])
                records.append(record)
                
    return records, math.ceil(len(records)/2)

def get_wzttrc_report(MVAs, date):
    
    wzttrc()
    
    day = int(date[:2])
    month = date[2:5]
    year = date[5:]
     
    for mva in MVAs:
        send_key_sequence(f'DSTR{mva}{day:02}{month.upper()}{year}@E')
        
        data, total_CO_CI = get_wzttrc_data(mva)
        for record in data:
            print(record)

def varmenu():
    send_key_sequence(f'@R@0/FOR VARMENU@E')
    wait_for_ready("VARMENU_ACTION")

def get_varmenu_report(station, rac):
    
    send_key_sequence(f'DSSM{station}@T{rac}@E')
    wait_for_ready("VARMENU_ACTION")
    
    data = []
    image = call_hllapi(5, " "*1920, 0)[1]
    data = image.decode('ascii')
    lines = format_data(data)
    
    OWNED = lines[8][6:12].strip()
    FOREIGN = lines[8][21:26].strip()
    UNAVAILABLE = lines[8][39:44].strip()
    OUT_OF_SERVICE = lines[8][60:65].strip()
    ON_RENT = lines[8][75:79].strip()
    OVERDUE = lines[9][8:14].strip()
    PARTIAL = lines[9][22:30].strip()
    
    DAYS_IN_THE_WEEK    = [lines[11][i*10:i*10 + 10].strip() for i in range(1, 8)]
    DATES               = [lines[12][i*10:i*10 + 10].strip() for i in range(1, 8)]
    ON_HAND             = [lines[13][i*10:i*10 + 10].strip() for i in range(1, 8)]
    DUE_IN              = [lines[14][i*10:i*10 + 10].strip() for i in range(1, 8)]
    RES_DI              = [lines[15][i*10:i*10 + 10].strip() for i in range(1, 8)]
    STN_INV             = [lines[16][i*10:i*10 + 10].strip() for i in range(1, 8)]
    VEH_RSVD            = [lines[17][i*10:i*10 + 10].strip() for i in range(1, 8)]
    AVAILABLE           = [lines[18][i*10:i*10 + 10].strip() for i in range(1, 8)]
    CAR_GROUP_AVAILABILITY = {
        lines[20][i*5 + 1:i*5 + 6].strip(): lines[21][i*5 + 1:i*5 + 6].strip() for i in range(0, 16)
    }
    
    DAYS = []
    
    for i in range(len(DAYS_IN_THE_WEEK)):
        record = {
            "DAYS_IN_THE_WEEK": DAYS_IN_THE_WEEK[i],
            "DATES": DATES[i],
            "ON_HAND": ON_HAND[i],
            "DUE_IN": DUE_IN[i],
            "RES_DI": RES_DI[i],
            "STN_INV": STN_INV[i],
            "VEH_RSVD": VEH_RSVD[i],
            "AVAILABLE": AVAILABLE[i]
        }
        DAYS.append(record)
    
    record = {
        "OWNED": OWNED,
        "FOREIGN": FOREIGN,
        "UNAVAILABLE": UNAVAILABLE,
        "OUT_OF_SERVICE": OUT_OF_SERVICE,
        "ON_RENT": ON_RENT,
        "OVERDUE": OVERDUE,
        "PARTIAL": PARTIAL,
        "DAYS": DAYS,
        "CAR_GROUP_AVAILABILITY": CAR_GROUP_AVAILABILITY
    }
    
    station = {
        "STATION": station,
        "REPORT": record
    }
    
    return station
    
def get_all_varmenu_data_from_NOFF1():
    NOFF1_A_Varmenu_data = []
    for stations in NOFF1_A:
        varmenu()
        report = get_varmenu_report(stations, "A")
        NOFF1_A_Varmenu_data.append(report)
        
    with open("python/data/NOFF1_A_Varmenu_data.json", "w") as file:
        file.write(json.dumps(NOFF1_A_Varmenu_data))
        
def get_all_previous_NOFF1_A_RAs(num_of_days):    
    NOFF1_A_PREVIOUS_RAs = []
    
    for stations in NOFF1_A:
        ras = get_previous_RA_info("A", stations, num_of_days)
        if len(ras) > 0:
            for ra in ras:
                NOFF1_A_PREVIOUS_RAs.append(ra)
        
    with open("python/data/NOFF1_A_PREVIOUS_RAs_V2.json", "w") as file:
        file.write(json.dumps(NOFF1_A_PREVIOUS_RAs))

# get_prices_for_x_days_for_the_whole_month("A", "E", "JUN", "TOS", "TOS", 1)
# get_all_customers_from_given_months("64442", ["JUN", "JUL", "AUG"])
# get_amount_of_cars_in_month("31JUN", 191)
# get_previous_RAs("A", "BDU", 7)
# find_all_one_way_rentals_to_TOS_and_T1Y_for_all_of_Norway("SEP", ["TOS", "T1Y"])
# get_all_x606_cars()
# get_prices_for_every_car_group("A", "28MAY24/1200", "TOS", "TOS", ["B", "C", "D", "E", "H", "I", "K", "M", "N"], 1)

connect_to_session("A")

# get_out_of_town_rentals("JUL")
# get_all_varmenu_data_from_NOFF1()
get_all_previous_NOFF1_A_RAs(3)

# get_wzttrc_report([
#     "21131375","21131703","21131891","21131950",
#     "21132042","21132355","21132370"
# ], "01JAN2022")

disconnect_from_session("A")