import requests

def wmata_bus_incidents(api_key):
    url = "https://api.wmata.com/Incidents.svc/json/BusIncidents"
    headers = {
        'api_key': api_key
    }

    try:
        response = requests.get(url, headers=headers)
        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: API returned status code {response.status_code}")
            return False

    except Exception as e:
        print(f"Error connecting to WMATA API: {str(e)}")
        return False

def wmata_rail_incidents(api_key):
    url = "http://api.wmata.com/Incidents.svc/json/Incidents"
    headers = {
        'api_key': api_key
    }

    try:
        response = requests.get(url, headers = headers)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            return {"RailIncidents": data.get("RailIncidents", [])}
        else:
            print(f"Error: API returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"Error connecting to WMATA Rail API: {str(e)}")
        return False

if __name__ == "__main__":
    from dotenv import load_dotenv
    import os

    load_dotenv()
    api_key = os.getenv("WMATA_API_KEY")

    if not api_key:
        print("WMATA_API_KEY not found in environment.")
    else:
        result = wmata_bus_incidents(api_key)
        if result:
            print("API connection successful!")
            print(f"Found {len(result.get('BusIncidents', []))} bus incidents")
        else:
            print("Failed to retrieve data from WMATA API")
