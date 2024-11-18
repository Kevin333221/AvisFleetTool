import os
from collections import defaultdict
from pathlib import Path
import xlsxwriter

data = None
with open('RapidAPI/result.json', 'r') as f:
    data = f.readlines()
    
data = eval(''.join(data))['data']
quotes = data['quotes']
vendors = defaultdict(list)
providers = defaultdict(dict)

# Create a dictionary of providers
for provider in data['providers']:
    providers[provider] = data['providers'][provider]['provider_name']

# Create a list of offers for each vendor
for quote in quotes:
    offer = {
        'sipp': quote['sipp'],
        'price': quote['price'],
        'car_name': quote['car_name'],
        'original_car_name': quote['original_car_name'],
        'provider': providers[quote['prv_id']]
    }
    vendors[quote['vndr']].append(offer)

# Sort vendor offers by sipp
for vendor, offers in vendors.items():
    vendors[vendor] = sorted(offers, key=lambda x: x['sipp'])

# Write offers to text files
for vendor, offers in vendors.items():
    filename = Path(f'RapidAPI/offers/{data["query"]["pu_dt"][:10]}--{data["query"]["do_dt"][:10]}/{vendor}.txt')
    filename.parent.mkdir(parents=True, exist_ok=True)
    prices = defaultdict(list)
    car_names = {}

    # Create a dictionary of prices and car names
    for offer in offers:
        prices[offer['sipp']].append((round(offer['price']), offer['provider']))
        car_names[offer['sipp']] = (offer['car_name'], offer['original_car_name'])

    with open(filename, 'w') as f:
        f.write(f"Rental dates from {data['query']['pu_dt'][:10]} {data['query']['pu_dt'][11:]} to {data['query']['do_dt'][:10]} {data['query']['do_dt'][11:]}\n")
        f.write(f"Vendor: {vendor}\n")
        for sipp, prices_list in prices.items():
            car_name, original_car_name = car_names[sipp]
            f.write("-----------------\n")
            f.write(f"SIPP: {sipp}\n")
            f.write(f"Car name 1: {car_name}\n")
            f.write(f"Car name 2: {original_car_name}\n")
            for i, price in enumerate(prices_list):
                f.write(f"Price {i+1}: {price}\n")
        f.write("\n")

# Write all offers to a text file
all_offers = Path(f'RapidAPI/offers/{data["query"]["pu_dt"][:10]}--{data["query"]["do_dt"][:10]}/all_offers.txt')
with open(all_offers, 'w') as f:
    f.write(f"Rental dates from {data['query']['pu_dt'][:10]} {data['query']['pu_dt'][11:]} to {data['query']['do_dt'][:10]} {data['query']['do_dt'][11:]}\n")
    for sipp in sorted(set(offer['sipp'] for offers in vendors.values() for offer in offers)):
        f.write("-----------------\n")
        f.write(f"SIPP: {sipp}\n")
        for offer in (offer for offers in vendors.values() for offer in offers if offer['sipp'] == sipp):
            car_name, original_car_name = offer['car_name'], offer['original_car_name']
            f.write(f"Car name 1: {car_name}\n")
            f.write(f"Car name 2: {original_car_name}\n")
            break
        f.write("Vendor".ljust(20))
        for vendor in vendors:
            f.write(f"{vendor}".ljust(20))
        f.write("\n")
        providers_set = set(offer['provider'] for offers in vendors.values() for offer in offers if offer['sipp'] == sipp)
        for provider in providers_set:
            f.write(f"{provider}".ljust(20))
            for vendor in vendors:
                price = next((offer['price'] for offer in vendors[vendor] if offer['sipp'] == sipp and offer['provider'] == provider), "")
                if price:
                    price = f"{price:.0f}"
                f.write(f"{price}".ljust(20))
            f.write("\n")
        f.write("\n")

# Write all offers to a text file
all_offers = Path(f'RapidAPI/offers/{data["query"]["pu_dt"][:10]}--{data["query"]["do_dt"][:10]}/all_offers_new.txt')
with open(all_offers, 'w') as f:
    f.write(f"Rental dates from {data['query']['pu_dt'][:10]} {data['query']['pu_dt'][11:]} to {data['query']['do_dt'][:10]} {data['query']['do_dt'][11:]}\n")      
    for sipp in sorted(set(offer['sipp'] for offers in vendors.values() for offer in offers)):
        f.write("-----------------\n")
        f.write(f"SIPP: {sipp}\n")
        for offer in (offer for offers in vendors.values() for offer in offers if offer['sipp'] == sipp):
            car_name, original_car_name = offer['car_name'], offer['original_car_name']
            f.write(f"Car name 1: {car_name}\n")
            f.write(f"Car name 2: {original_car_name}\n")
            break
        f.write("Provider".ljust(20))
        for provider in providers.values():
            f.write(f"{provider}".ljust(20))
        f.write("\n")
        for vendor in vendors:
            f.write(f"{vendor}".ljust(20))
            for provider in providers.values():
                price = next((offer['price'] for offer in vendors[vendor] if offer['sipp'] == sipp and offer['provider'] == provider), "")
                if price:
                    price = f"{price:.0f}"
                f.write(f"{price}".ljust(20))
            f.write("\n")
        f.write("\n")
        
# Write all offers to a xlsx file
all_offers_xlsx = Path(f'RapidAPI/offers/{data["query"]["pu_dt"][:10]}--{data["query"]["do_dt"][:10]}/all_offers_new.xlsx')
workbook = xlsxwriter.Workbook(all_offers_xlsx)

# Write each SIPP to a separate sheet
for sipp in sorted(set(offer['sipp'] for offers in vendors.values() for offer in offers)):
    worksheet = workbook.add_worksheet(sipp)
    worksheet.write(0, 0, f"Rental dates from {data['query']['pu_dt'][:10]} {data['query']['pu_dt'][11:]} to {data['query']['do_dt'][:10]} {data['query']['do_dt'][11:]}")

    row = 1
    worksheet.write(row, 0, "-----------------")
    row += 1
    worksheet.write(row, 0, f"SIPP: {sipp}")
    row += 1
    for offer in (offer for offers in vendors.values() for offer in offers if offer['sipp'] == sipp):
        car_name, original_car_name = offer['car_name'], offer['original_car_name']
        worksheet.write(row, 0, f"{car_name}")
        row += 1
        worksheet.write(row, 0, f"{original_car_name}")
        row += 1
        break
    worksheet.write(row, 0, "Provider")
    col = 1
    for provider in providers.values():
        worksheet.write(row, col, provider)
        col += 1
    row += 1
    for vendor in vendors:
        worksheet.write(row, 0, vendor)
        col = 1
        for provider in providers.values():
            price = next((offer['price'] for offer in vendors[vendor] if offer['sipp'] == sipp and offer['provider'] == provider), "")
            if price:
                price = f"{price:.1f}"
            worksheet.write(row, col, price)
            col += 1
        row += 1
    row += 1

workbook.close()