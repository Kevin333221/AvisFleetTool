import requests

url = "https://sky-scrapper.p.rapidapi.com/api/v1/cars/searchCars"

pickup_date = "2025-01-13"
pickup_time = "10:00"
dropoff_date = "2025-01-20"
dropoff_time = "10:00"

querystring = {
    "pickUpEntityId":"128668512",
    "dropOffEntityId":"128668512",
    "pickUpDate": pickup_date,
    "pickUpTime": pickup_time,
    "dropOffDate": dropoff_date,
    "dropOffTime": dropoff_time,
    "currency":"NOK",
    "countryCode":"NO",
    "market":"en-NO"
}

headers = {
	"x-rapidapi-key": "fc569e7265msh80d1ee7f3ecf11ep185a32jsn66ffd51fce97",
	"x-rapidapi-host": "sky-scrapper.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)
data = response.json()

with open('RapidAPI/result.json', 'w') as f:
    f.write(str(data))
    
# Run the "print_offers.py" script
import os
os.system('python RapidAPI/print_offers.py')