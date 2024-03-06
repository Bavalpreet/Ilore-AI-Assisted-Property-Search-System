import requests
class FetchDescription :

    def __init__(self, headers):
        self.headers = headers


    # funtion to get all the metadata of the GTA cities
    def get_cities_metadata(self):

        fulldetails = {}
        listurl = "https://housesigma.com/bkv2/api/search/address_v2/suggest"

        gta_cities = [
            "Toronto", "Ajax", "Aurora", "Brampton", "Brock", "Burlington",
            "Caledon", "Clarington", "East Gwillimbury", "Georgina", "Markham",
            "Mississauga", "Milton", "Newmarket", "Oakville", "Oshawa", "Pickering",
            "Richmond Hill", "Scugog", "Vaughan", "Whitchurch-Stouffville", "Uxbridge",
            "King", "Halton Hills", "Whitby"
        ]
        for city in gta_cities:
            payload = {
                "lang": "en_US",
                "province": "ON",
                "search_term": city
            }
            response = requests.get(listurl, params=payload, headers=self.headers)
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                city_data = response.json()
                fulldetails[city] = city_data
            else:
                print("Error:", response.status_code)

        return fulldetails


headers = {
        "Authorization": "Bearer 202401259ujl7r8cqoknievf8pj8qbg85u"
    }

fetch = FetchDescription(headers)

all_ids = fetch.get_cities_metadata()
print(all_ids)