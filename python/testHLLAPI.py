import ctypes
import time

# Load the HLLAPI DLL
hllapi_dll = ctypes.windll.LoadLibrary(".\python\whlapi32.dll")

# Define the HLLAPI function prototype
hllapi = hllapi_dll.hllapi
hllapi.argtypes = [ctypes.POINTER(ctypes.c_short), ctypes.c_char_p, ctypes.POINTER(ctypes.c_short), ctypes.POINTER(ctypes.c_short)]

sleep_time = 1
session_id = 'A'

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

def call_hllapi(function_code, data):
    
    length = ctypes.c_short(len(data))
    return_code = ctypes.c_short(0)
    function_code = ctypes.c_short(function_code)
    data = ctypes.c_char_p(data.encode('ascii'))
    hllapi(ctypes.byref(function_code), data, ctypes.byref(length), ctypes.byref(return_code))

    return return_code.value

def call_hllapi2(function_code, data, length):
    length = ctypes.c_short(length)
    return_code = ctypes.c_short(0)
    function_code = ctypes.c_short(function_code)
    data = ctypes.create_string_buffer(data.encode('ascii'), length.value)

    hllapi(ctypes.byref(function_code), data, ctypes.byref(length), ctypes.byref(return_code))

    return return_code.value, data.value

def connect_to_session(session_id):
    return_code = call_hllapi(1, session_id)
    return return_code

def disconnect_from_session(session_id):
    return_code = call_hllapi(2, session_id)
    return return_code

def send_key_sequence(keys):
    return_code = call_hllapi(3, keys)
    return return_code

def x801(ped_number):
    send_key_sequence(f'@R@0/FOR X801@EPDA@T{ped_number}@E')
    time.sleep(sleep_time)

def x515(location, date=""):
    
    if date:
        send_key_sequence(f'@R@0/FOR X515@EDSAT@T{location}@T {date}@E')
    else:
        send_key_sequence(f'@R@0/FOR X515@EDSAT@T{location}@E')
    time.sleep(sleep_time)

def x515_cont(date):
    send_key_sequence(f'@T@T@T{date}@T@F@E')
    time.sleep(sleep_time)

def x601(location):
    send_key_sequence(f'@R@0/FOR X601@ENC@T{location}@E')
    time.sleep(sleep_time)
    
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
        _, image = call_hllapi2(5, " "*1920, 1920)
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
    time.sleep(sleep_time)

def get_number_of_customers_in_month(station: str, month: str, year: str, days_in_month=31):
    
    days = []
    x515(f"{station.upper()}", f"01{month.upper()}{year}")
    customers = get_customers()
    days.append(len(customers))
    
    for i in range(2, days_in_month+1):
        x515_cont(f"{i:02}{month.upper()}{year}")
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
        x515_cont(f"{i:02}{month.upper()}{year}")
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

def sign_on(station, ped_number):
    x801(ped_number)
    x601(station)
    x515(station)

return_code = connect_to_session(session_id)
if return_code != 0:
    print('Failed to connect to session')
    exit()
    
    
    

# sign_on("TOS", "04941052")
# get_number_of_customers_in_month("TOS", "AUG", "2024")
# get_number_of_car_groups_in_month("TOS", "AUG", "2024")



# Disconnect from session 'A'
disconnect_from_session(session_id)