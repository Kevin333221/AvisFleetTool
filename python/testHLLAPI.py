import ctypes
import time

# Load the HLLAPI DLL
hllapi_dll = ctypes.windll.LoadLibrary("C:/Users/Kevin/OneDrive/Dokumenter/AvisBudget/AvisFleetTool/AvisFleetTool/python/whlapi32.dll")

# Define the HLLAPI function prototype
hllapi = hllapi_dll.hllapi
hllapi.argtypes = [ctypes.POINTER(ctypes.c_short), ctypes.c_char_p, ctypes.POINTER(ctypes.c_short), ctypes.POINTER(ctypes.c_short)]

sleep_time = 1

columns = {
    "name": (0, 19),
    "arr_time": (20, 24),
    "flight_no": (25, 30),
    "car_grp": (33, 34),
    "rate_code": (37, 41),
    "remarks": (43, 65),
    "exp_lor": (70, 73),
    "in_sta": (74, 77)
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

# Connect to session 'A'
session_id = 'A'
return_code = connect_to_session(session_id)
if return_code != 0:
    print('Failed to connect to session')
    exit()

def x801(ped_number):
    send_key_sequence(f'@R@0/FOR X801@EPDA@T{ped_number}@E')
    time.sleep(sleep_time)

def x515(location, date=""):
    
    if date:
        send_key_sequence(f'@R@0/FOR X515@EDSAT@T{location}@T {date}@E')
    else:
        send_key_sequence(f'@R@0/FOR X515@EDSAT@T{location}@E')
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
    
def get_customers(data):
    lines = format_data(data)

    customers = []

    for line in lines[12:-1]:
        # Checkin if ord(line[0]) is not a space or the letter "V"
        if ord(line[0]) != 32 and ord(line[0]) != 86:
            customer = {}
            for key, value in columns.items():
                customer[key] = line[value[0]:value[1]]
            customers.append(customer)

    return customers

# x801("04941051")
x601("TR7")
x515("TR7", "26MAY2024")
_, image = call_hllapi2(5, " "*1920, 1920)
data = image.decode('ascii')

customers = get_customers(data)

if len(customers) == 0:
    print('No customers found')
else:
    for customer in customers:
        print(customer)

# Disconnect from session 'A'
return_code = disconnect_from_session(session_id)
if return_code != 0:
    print('Failed to disconnect from session')
    exit()