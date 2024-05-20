
class Car:   
    def __init__(self, mva):
        self.mva: str = mva
        self.registration_number: str = None
        self.fleet_code: str = None
        self.make: str = None
        self.ignit_key: str = None
        self.trunk_key: str = None
        self.last_movement: str = None
        self.body_type: str = None
        self.miles: str = None
        self.car_group: str = None
        self.current_location: list = None
        self.location_out: list = None
        self.movement: str = None
        self.date_out: str = None
        self.date_due: str = None
        self.location_due: list = None
        self.accessories: list = None
        self.fuel_type: str = None
        self.status: str = None
        self.hold_date: str = None
        self.hold_reason: str = None
    
    def set_attributes(self, registration_number, fleet_code, make, ignit_key, current_location, trunk_key, last_movement, body_type, miles, car_group, location_out, movement, date_out, date_due, location_due, accessories, fuel_type, status, hold_date, hold_reason):
        self.registration_number: str = registration_number
        self.fleet_code = fleet_code
        self.make: str = make
        self.ignit_key: str = ignit_key
        self.current_location: list = current_location
        self.trunk_key: str = trunk_key
        self.last_movement: str = last_movement
        self.body_type: str = body_type
        self.miles: str = miles
        self.car_group: str = car_group
        
        self.location_out: list = location_out
        self.movement: str = movement
        self.date_out: str = date_out
        self.date_due: str = date_due
        self.location_due: list = location_due
        
        self.accessories: list = accessories
        self.fuel_type: str = fuel_type
        self.status: str = status
        self.hold_date: str = hold_date
        self.hold_reason: str = hold_reason
        
    def __str__(self):
        return f"{self.mva} - {self.registration_number}"
    
    def __repr__(self):
        return f"{self.mva} - {self.registration_number}"