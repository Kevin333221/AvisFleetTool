import time
from config import *

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

def xe515(station, rac_code, date="", res=False):
        
    res_code = "AT" if not res else "RES"
        
    if date:
        if rac_code == "A":
            send_key_sequence(f'@R@0/FOR X515@E')
        else:
            send_key_sequence(f'@R@0/FOR e515@E')
        
        wait_for_ready("x515_ACTION")
        
        if rac_code == "A":
            if res_code == "RES":
                send_key_sequence(f'DS{res_code}{station}@T {date}@E')
            else:
                send_key_sequence(f'DS{res_code}@T{station}@T {date}@E')
        else:
            if res_code == "RES":
                send_key_sequence(f'DS{res_code}{station}@T{date}@E')
            else:
                send_key_sequence(f'DS{res_code}@T{station}@T{date}@E')
        
        wait_for_ready("x515_ACTION")
        send_key_sequence(f'@0')
        
    else:
        if rac_code == "A":
            send_key_sequence(f'@R@0/FOR X515@E')
        else:
            send_key_sequence(f'@R@0/FOR e515@E')
        
        wait_for_ready("x515_ACTION")
        
        if rac_code == "A":
            if res_code == "RES":
                send_key_sequence(f'DS{res_code}{station}@E')
            else:
                send_key_sequence(f'DS{res_code}@T{station}@E')
        else:
            if res_code == "RES":
                send_key_sequence(f'DS{res_code}{station}@E')
            else:
                send_key_sequence(f'DS{res_code}@T{station}@E')
        
        wait_for_ready("x515_ACTION")
                
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
    
    class Date:
        def __init__(self, date: str):
            self.day = int(date[0:2])
            self.month = date[2:5].upper()
            self.year = date[5:7]
            self.day_of_week = int(date[8:])
            self.raw = date
            
        def get_date(self):
            return f"{self.day:02}" + str(self.month) + str(self.year) + '/' + str(self.day_of_week)
        
    year = date[5:7]
    month = date[2:5].upper()
    in_date = Date(((f"{int(date[0:2])+length:02}") + month + year + "/" + date[8:]))
    lor = length
    
    # If the return date is in the next month
    if in_date.day > month_to_days_in_month[month]:
        in_day = in_date.day - month_to_days_in_month[month]
        numMonth = months_to_num[month]
        
        if numMonth + 1 > 12:
            in_date = Date(f"{in_day:02}" + num_to_months[1] + year + "/" + date[8:])
        else:
            in_date = Date(f"{in_day:02}" + num_to_months[(numMonth + 1)] + year + "/" + date[8:])
        
    # If the return date is in the next year
    if month == "DEC" and in_date.month == "JAN":
        year = str(int(year) + 1)
        in_date = Date(f"{in_date.day:02}" + str(in_date.month) + year + "/" + date[8:])
    
    send_key_sequence(f'RS@T{out_sta}@T@T{date}WI@T@T{car_group}@T@T{in_sta}@T@T{in_date.get_date()}@E')
    
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
    
    RATE = call_hllapi(8, "0000000000", cursor_locations["x502_RATE"])[1].decode('ascii').strip()
    if RATE[0:2] == "X-":
        RATE = RATE[2:]
    
    send_key_sequence(f'@0@T')
    return price, lor, RATE

def x502_see_reservation(reservation_number):
    send_key_sequence(f"DR")
    move_cursor(cursor_locations["x502_LICENSE"])
    send_key_sequence(f"@F")
    move_cursor(cursor_locations["x502_CUSTOMER_NAME"])
    send_key_sequence(f"R/{reservation_number}@F@E")
    wait_for_ready("x502_PAC")

def x502_get_reservation_info(rac):
    
    wait_for_ready("x502_PAC")
    WIZ = call_hllapi(8, "666666", cursor_locations["x502_WIZ"])[1].decode('ascii').strip()
    STATION_OUT = call_hllapi(8, "55555", cursor_locations["x502_STATION_OUT"])[1].decode('ascii').strip()
    CTR = call_hllapi(8, "22", cursor_locations["x502_CTR"])[1].decode('ascii').strip()
    DATE_OUT = call_hllapi(8, "000000000000", cursor_locations["x502_DATE_OUT"])[1].decode('ascii').strip()[:7]
    DAY_OUT = call_hllapi(8, "333", cursor_locations["x502_DATE_OUT"] + 15)[1].decode('ascii').strip()    
    FLIGHT_NO = call_hllapi(8, "666666", cursor_locations["x502_FLIGHT_NO"])[1].decode('ascii').strip()
    CUPON = call_hllapi(8, "7777777", cursor_locations["x502_CUPON"])[1].decode('ascii').strip()
    CAR_GROUP = call_hllapi(8, "999999999", cursor_locations["x502_CAR_GROUP"])[1].decode('ascii').strip()
    if CAR_GROUP[0] == "/":
        CAR_GROUP = CAR_GROUP[1:]
    DELIVERY = call_hllapi(8, "1", cursor_locations["x502_DELIVERY"])[1].decode('ascii').strip()
    STATION_IN = call_hllapi(8, "55555", cursor_locations["x502_STATION_IN"])[1].decode('ascii').strip()
    COLLECTION = call_hllapi(8, "1", cursor_locations["x502_COLLECTION"])[1].decode('ascii').strip()
    DATE_IN = call_hllapi(8, "000000000000", cursor_locations["x502_DATE_IN"])[1].decode('ascii').strip()[:7]
    DAY_IN = call_hllapi(8, "333", cursor_locations["x502_DATE_IN"] + 15)[1].decode('ascii').strip()
    CUSTOMER_NAME = call_hllapi(8, "000000000000000000000000000000", cursor_locations["x502_CUSTOMER_NAME"])[1].decode('ascii').strip()
    RATE = call_hllapi(8, "0000000000", cursor_locations["x502_RATE"])[1].decode('ascii').strip()
    if RATE[0:2] == "X-":
        RATE = RATE[2:]
    SAC = call_hllapi(8, "22", cursor_locations["x502_SAC"])[1].decode('ascii').strip()
    DATE_OF_BIRTH = call_hllapi(8, "7777777", cursor_locations["x502_DATE_OF_BIRTH"])[1].decode('ascii').strip()
    if len(DATE_OF_BIRTH) != 0:
        if int(DATE_OF_BIRTH[5:7]) > int(year2D) - 18:
            DATE_OF_BIRTH = DATE_OF_BIRTH[:5] + "19" + DATE_OF_BIRTH[5:]
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
    
    RES = ""
    PREPAYMENT = ""
    CURRENCY = ""
    CDW = ""
    TP = ""
    OWF = ""
    PRICE = ""
    BOOKET_AT = ""
    TOUR_RATE = 0
    IS_CANCELLED = False
    
    isEnd = False
    
    while not isEnd:
        
        # Takes a picture of the screen
        image = call_hllapi(5, " "*1920, 0)[1]
        data = image.decode('ascii')
        lines = format_data(data)
        isEnd = True
        
        for line in lines[1:]:
            curr_line = line[35:]
            
            if curr_line[0:3] == "RES":
                RES = curr_line[8:22].strip()
            
            if curr_line[0:5] == "CNCL/":
                IS_CANCELLED = True
            
            if curr_line[0:25] == "FIXED VALUE PP AMOUNT IS ":
                amount = curr_line[25:].strip().split()
                PREPAYMENT = amount[1]
                CURRENCY = amount[0]
                
            if curr_line[0:9] == "NWE  CDW=":
                CDW = curr_line[9:20].strip()

            if curr_line[21:25] == "TP =":
                TP = curr_line[25:].strip()
                
            if curr_line[18:26] == "CURRENCY":
                CURRENCY = curr_line[29:32].strip()
            
            if curr_line[0:11] == "ONE WAY FEE":
                OWF = curr_line[11:20].strip()

            if curr_line[0:9] == "TOUR RATE":
                TOUR_RATE = 1
        
            if curr_line[0:5] == "TOTL=":
                PRICE = curr_line[5:25].strip()
                
            if curr_line[0:7] == "CURRENT":
                BOOKET_AT = curr_line[15:22]
                
            if curr_line[0:8] == "ORIGINAL":
                BOOKET_AT = curr_line[15:22]
                
            if curr_line[35:43] == "N MORE..":
                isEnd = False
                send_key_sequence(f'@0')
                press_page_up()
                wait_for_ready("x502_PAC")
            
            if curr_line[35:43] == "N END...":
                isEnd = True
                break
    
    return {
        "RAC": rac,
        "BOOKET_AT": BOOKET_AT,
        "RES": RES,
        "IS_CANCELLED": IS_CANCELLED,
        "WIZARD_NR": WIZ,
        "STATION_OUT": STATION_OUT,
        # "CTR": CTR,
        "DATE_OUT": DATE_OUT,
        "DAY_OUT": DAY_OUT,
        "FLIGHT_NO": FLIGHT_NO,
        # "CUPON": CUPON,
        "CAR_GROUP": CAR_GROUP,
        # "DELIVERY": DELIVERY,
        "STATION_IN": STATION_IN,
        # "COLLECTION": COLLECTION,
        "DATE_IN": DATE_IN,
        "DAY_IN": DAY_IN,
        "CUSTOMER_NAME": CUSTOMER_NAME,
        "RATE": RATE,
        # "SAC": SAC,
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
        "ADDR COUNTRY": ADDR3[-2:],
        "LICENSE": LICENSE,
        "SOURCE": SOURCE,
        "CONTACT": CONTACT,
        "REMARKS": REMARKS,
        "AWD": AWD,
        "T/A": TA,
        "FREQUENT_TRAVEL_NUMBER": FREQUENT_TRAVEL_NUMBER,
        "PREPAYMENT": PREPAYMENT,
        "CURRENCY": CURRENCY,
        "PRICE": PRICE,
        "CDW": CDW,
        "TP": TP,
        "OWF": OWF,
        "TOUR RATE": TOUR_RATE,
        "RESERVATION COUNTRY": RES[10:12],
    }

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

def get_RA_info_x203():
    RA = call_hllapi(8, "999999999", cursor_locations["x203_RA"])[1].decode('ascii').strip()
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
    DELIVERY = call_hllapi(8, "88888888", cursor_locations["x203_DELIVERY"])[1].decode('ascii').strip()
    KILOMETER_IN = call_hllapi(8, "666666", cursor_locations["x203_KILOMETER_IN"])[1].decode('ascii').strip()
    STATION_IN = call_hllapi(8, "55555", cursor_locations["x203_STATION_IN"])[1].decode('ascii').strip()
    DATE_IN = call_hllapi(8, "000000000000", cursor_locations["x203_DATE_IN"])[1].decode('ascii')
    AUTH_IN = call_hllapi(8, "0000000000", cursor_locations["x203_AUTH_IN"])[1].decode('ascii').strip()
    BFL = call_hllapi(8, "88888888", cursor_locations["x203_BFL"])[1].decode('ascii').strip()
    COLLECTION = call_hllapi(8, "88888888", cursor_locations["x203_COLLECTION"])[1].decode('ascii').strip()
    AMOUNT_DUE = call_hllapi(8, "0000000000000", cursor_locations["x203_AMOUNT_DUE"])[1].decode('ascii').strip()
    AWD = call_hllapi(8, "999999999", cursor_locations["x203_AWD"])[1].decode('ascii').strip()
    ADJUSMENT = call_hllapi(8, "88888888", cursor_locations["x203_ADJUSTMENT"])[1].decode('ascii').strip()
    RATE = call_hllapi(8, "666666", cursor_locations["x203_RATE"])[1].decode('ascii').strip()
    OWFMISC = call_hllapi(8, "0000000000000000", cursor_locations["x203_OWF/MISC"])[1].decode('ascii').strip()
    DATE_OF_BIRTH = call_hllapi(8, "7777777", cursor_locations["x203_DATE_OF_BIRTH"])[1].decode('ascii').strip()
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
    }
    
    return record

def get_RA_info_x806():
    
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

def x313_setup():
    send_key_sequence(f'@R@0/FOR X313@E')
    wait_for_ready("x313_ACTION")
    send_key_sequence(f'@T')

def get_cursor_location():
    connect_to_session("A")
    time.sleep(3)
    print(call_hllapi(7, "", 0))
    disconnect_from_session("A")

def move_cursor(location):
    call_hllapi(40, "", location)

def press_page_up():
    send_key_sequence(f'@x')

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
   
def WZTOPN():
    send_key_sequence(f'@R@0/FOR WZTOPN@E')
    wait_for_ready("WZTTRC_ACTION")
    
def WZTOPN_cont(mva):
    send_key_sequence(f'DSOP{mva}@E')
    wait_for_ready("WZTTRC_ACTION")

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

def wait_for_ready(loc):
    ready = False
    while not ready:
        ret = call_hllapi(7, "", 0)[2]
        if ret == cursor_locations[loc]:
            ready = True

def manifest(date, station, rac):
    send_key_sequence(f"@R@0/FOR MANIFEST@E")
    wait_for_ready("MANIFEST_ACTION")
    
    send_key_sequence(f"DSRNT{station}@T{rac}@T{date}@E")
    wait_for_ready("MANIFEST_ACTION") 

def varmenu():
    send_key_sequence(f'@R@0/FOR VARMENU@E')
    wait_for_ready("VARMENU_ACTION")

def wzttrc():
    send_key_sequence(f'@R@0/FOR WZTTRC@E')
    wait_for_ready("WZTTRC_ACTION")
