import ctypes
import time
from flask_cors import CORS, cross_origin
import flask
from car import Car
import json
import datetime
import requests

app = flask.Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Load the HLLAPI DLL
hllapi_dll = ctypes.windll.LoadLibrary(".\Backend\whlapi32.dll")

# Define the HLLAPI function prototype
hllapi = hllapi_dll.hllapi
hllapi.argtypes = [ctypes.POINTER(ctypes.c_short), ctypes.c_char_p, ctypes.POINTER(ctypes.c_short), ctypes.POINTER(ctypes.c_short)]

session_id = 'H'

@app.route('/api/get_cars')
@cross_origin()
def index():
    
    return_code = call_hllapi(1, session_id, 0)[3]
    if return_code != 0:
        print('Failed to connect to session')
        exit()
    
    print("Getting cars data...")
    
    cars = get_cars_data()

    # Disconnect from session 'A'
    disconnect_from_session(session_id)
    
    return cars

cursor_locations = {
    "x515_ACTION": 89,
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

def x515(location, date=""):
    
    if date:
        send_key_sequence(f'@R@0/FOR X515@E')
        
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
        send_key_sequence(f'@R@0/FOR X515@E')
        
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
    send_key_sequence(f'@T@T@T{date}@T@F@E')

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
    while not isEnd:
        image = call_hllapi(5, " "*1920, 0)[1]
        data = image.decode('ascii')
        lines = format_data(data)
        
        isEnd = True
        for line in lines[12:]:
            if ord(line[0]) != 32 and line[0:8] != "VERIFIED":
                customer = {}
                for key, value in columns.items():
                    if line[value[0]:value[1]] == " ":
                        customer[key] = line[value[0]+1:value[1]+1]
                    else:
                        customer[key] = line[value[0]:value[1]]
                    
                if customer["name"] == "END  OF  REPORT    ":
                    break
                
                if customer["name"] == "36-PRESS PA1 FOR NE":
                    isEnd = False
                    press_page_up()
                else:
                    customers.append(customer)
    
    return customers

def press_page_up():
    send_key_sequence(f'@x')

def get_number_of_customers_in_month(station: str, month: str, year: str, days_in_month=31):
    
    days = []
    x515(f"{station.upper()}", f"01{month.upper()}{year}")
    customers = get_customers()
    days.append(len(customers))
    
    for i in range(2, days_in_month+1):
        xe515_cont(f"{i:02}{month.upper()}{year}")
        customers = get_customers()
        days.append(len(customers))

    print(f"\n\nTotal customers in the month of {month.upper()} in the year {year}:")
    for day, customers in enumerate(days):
        print(f"Day {day+1}: {customers}")
    print("\n\n")

def get_number_of_car_groups_in_month(station: str, month: str, year: str, days_in_month=31):

    Days = {}
    
    # Initialize the dictionary
    for i in range(1, days_in_month+1):
        Days[f"{i:02}{month.upper()}{year}"] = {
            "B": 0,
            "C": 0,
            "D": 0,
            "E": 0,
            "H": 0,
            "I": 0,
            "K": 0,
            "M": 0,
            "N": 0,
        }
    
    x515(f"{station.upper()}", f"01{month.upper()}{year}")
    customers = get_customers()
    
    # Get the number of a particular car group in that day
    for customer in customers:
        if (customer["car_grp"] not in Days[f"01{month.upper()}{year}"]):
            Days[f"01{month.upper()}{year}"][customer["car_grp"]] = 1
        else:
            Days[f"01{month.upper()}{year}"][customer["car_grp"]] += 1
        
    for i in range(2, days_in_month+1):
        xe515_cont(f"{i:02}{month.upper()}{year}")
        customers = get_customers()
        
        for customer in customers:
            if (customer["car_grp"] not in Days[f"{i:02}{month.upper()}{year}"]):
                Days[f"{i:02}{month.upper()}{year}"][customer["car_grp"]] = 1
            else:
                Days[f"{i:02}{month.upper()}{year}"][customer["car_grp"]] += 1
     
    print(f"\n\nTotal car groups in the month of {month.upper()} in the year {year}:")
    for day, car_groups in Days.items():
        print(f"Day {day}: {car_groups}")
    print("\n\n")

def get_cursor_location():
    time.sleep(3)
    return call_hllapi(7, "", 0)

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

def sign_on(station, ped_number):
    x801(ped_number)
    x601(station)
    x515(station)

def get_cars_data():
    
    MVAs = read_MVAs()
    cars = []
    
    x313_setup()
    
    for mva in MVAs:
        newCar = get_car_details(mva)
        cars.append(newCar)

    return {"date": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"), "cars": [car.__dict__ for car in cars]}

app.run(port=5000, debug=True)