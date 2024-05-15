import requests
import json

# URL to send the POST request to
post_req_url = "https://wabi-north-europe-h-primary-redirect.analysis.windows.net/export/xlsx"

# get_url = "https://app.powerbi.com/groups/987ebbab-ea7a-429d-b941-d33b5ef2efab/reports/95de02af-ceda-4ae9-90b7-ad63371ae6f2/ReportSection199bacc027a34301300a?experience=power-bi"

# req = requests.get(get_url)

# print(req.status_code)

# Authorization token
auth_token = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IkwxS2ZLRklfam5YYndXYzIyeFp4dzFzVUhIMCIsImtpZCI6IkwxS2ZLRklfam5YYndXYzIyeFp4dzFzVUhIMCJ9.eyJhdWQiOiJodHRwczovL2FuYWx5c2lzLndpbmRvd3MubmV0L3Bvd2VyYmkvYXBpIiwiaXNzIjoiaHR0cHM6Ly9zdHMud2luZG93cy5uZXQvOTdjMzI1ZDAtNGNjYi00M2YzLTg1OGMtYTBhYjA1NzQxOTg3LyIsImlhdCI6MTcxNTcyMDM5OCwibmJmIjoxNzE1NzIwMzk4LCJleHAiOjE3MTU3MjQ0NzcsImFjY3QiOjAsImFjciI6IjEiLCJhaW8iOiJBVlFBcS84V0FBQUFQNFoxYUJ1NzlpQi9hUDNHRW1CR05yT2N5M1YxS0d1UjF4ZVIvRlJMaThPRjRDSytJL3pESTRNOVZZYy90clhBeTZCVzBCWWMyM0RUQVoxNmZTd1F3b0laNEZTeWRNcXVxbWR0VXdSWElFbz0iLCJhbXIiOlsicHdkIiwibWZhIl0sImFwcGlkIjoiODcxYzAxMGYtNWU2MS00ZmIxLTgzYWMtOTg2MTBhN2U5MTEwIiwiYXBwaWRhY3IiOiIwIiwiZmFtaWx5X25hbWUiOiJCZXJnYW4iLCJnaXZlbl9uYW1lIjoiS2V2aW4gTWF0aGlhcyIsImlwYWRkciI6IjE5My42OS4zNS4yNDEiLCJuYW1lIjoiS2V2aW4gTWF0aGlhcyBCZXJnYW4iLCJvaWQiOiJiMTEwZDEwNC03NmE0LTQ5NzEtOThiNS0wOTM4ODhmN2NjOTEiLCJvbnByZW1fc2lkIjoiUy0xLTUtMjEtMTA4MzIyODk4NC0zMDgyNjk0MzE1LTI5MzY0NDA5LTIyNTEzNSIsInB1aWQiOiIxMDAzMjAwMDk5NkRERjM5IiwicmgiOiIwLkFVY0EwQ1hEbDh0TTgwT0ZqS0NyQlhRWmh3a0FBQUFBQUFBQXdBQUFBQUFBQUFBTkFlcy4iLCJzY3AiOiJ1c2VyX2ltcGVyc29uYXRpb24iLCJzaWduaW5fc3RhdGUiOlsia21zaSJdLCJzdWIiOiJOLU96SDF4T1g5bDN3TWFxZ1g5d1dsTnEzNVpzdGJlaTFJSG00NzhBYzN3IiwidGlkIjoiOTdjMzI1ZDAtNGNjYi00M2YzLTg1OGMtYTBhYjA1NzQxOTg3IiwidW5pcXVlX25hbWUiOiJZNTU4NzcxQGVtLmFiZy5jb20iLCJ1cG4iOiJZNTU4NzcxQGVtLmFiZy5jb20iLCJ1dGkiOiI3NkVLdlB3NmJFdWNLZnlONl9zMUFBIiwidmVyIjoiMS4wIiwid2lkcyI6WyJiNzlmYmY0ZC0zZWY5LTQ2ODktODE0My03NmIxOTRlODU1MDkiXX0.M-SQy9PWcIZ9sS_KMY0s480hhuEYFqVkfEjqvXNAPfFNluGI_tZ0xLRsDMh93u-j3GAzROOksjSOLYBVbrTNdB_87QaZd1thnE-cspCyVMIiwcbrckHQZpRXTgwLPSpwySYOTfE-6dHqyuzvCNoqhZ44LgsdefqoVJVL_mRL4qAd9NJHSDoO8ErT7UTARn0d5WEx3sHgK2Yl_ffAYp4Pr6IOXwaOfqJ48E0DHjnRAyVMuhFTxGWo2K-NldKvRNq4DXN7Ei5BTaaiJKO6dznv5WuKb5QIE9whoNgaUTZG9up2i4lRPM0w7flroVTcMDN9Cx4q5mAJyeOGwjZ5FQFQug"
# RequestID = "5d7f09a7-039d-0fc2-1c63-c54f6c3c5a74"
# ActivityID = "a396a89d-757f-4bf7-b930-0b737e2a6a82"

# Headers for the POST request
headers = {
    "Authorization": auth_token,
    "Content-Type": "application/json",
}

# Data is located in a local file called "postReqJson.json"
with open("./public/postReqJson.json", "r") as f:
    data = json.load(f)

# Send the POST request
response = requests.post(post_req_url, headers=headers, json=data)

# Print the status code of the response
print(response.status_code)

if (response.status_code != 200):
    print("Error: ", response.text)
    exit()

# Save the response as a file called "data.xlsx"
# Marking the data with the current date and time 
with open("./public/data.xlsx", "wb") as f:
    f.write(response.content)

print("File saved as data.xlsx")