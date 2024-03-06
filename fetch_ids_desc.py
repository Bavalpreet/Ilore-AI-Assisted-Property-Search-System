import requests
import json
import pandas as pd


class FetchDescription:

    def __init__(self, headers, ids):
        self.headers = headers
        self.ids = ids

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

        return fulldetails, gta_cities

    def get_description(self):

        ids = []
        description1 = []
        description2 = []
        formatted_id_descriptions = {}
        url = "https://housesigma.com/bkv2/api/listing/info/detail_v2"

        # Getting the ids with its corresponding descriptions
        for gta_id_list in self.ids:
            ids.append(gta_id_list)

            payload = {"lang": "en_US",
                       "province": "ON",
                       "id_address": "",
                       "id_listing": gta_id_list,
                       "event_source": "",
                       "signature": "12629da4579fe635518e06ef7f053191",
                       "ts": "1709347825"
                       }

            response = requests.get(url, params=payload, headers=self.headers)

            if response.status_code == 200:
                data = response.json()

            else:
                print("Error:", response.status_code)

            # Getting description1 and description 2 differently
            for key, value in data.items():
                if isinstance(value, dict) and 'key_facts' in value:
                    key_facts = value['key_facts']

                    if 'description1' in key_facts:
                        description1.append(key_facts['description1'])

                    if 'description2' in key_facts:
                        description2.append(key_facts['description2'])

                    if description1 is not None and description2 is not None:
                        break

            for i, id in enumerate(ids):
                descriptions = {
                    "description1": description1[i],
                    "description2": description2[i]
                }
                formatted_id_descriptions[id] = descriptions

        json_formatted_id_descriptions = json.dumps(formatted_id_descriptions)
        return json_formatted_id_descriptions


headers = {
    "Authorization": "Bearer 202401259ujl7r8cqoknievf8pj8qbg85u"
}

fetch = FetchDescription(headers, [])

city_meta, all_cities = fetch.get_cities_metadata()
# print(all_ids)

gta_location_ids = []
for city in all_cities:
    for val in city_meta[city]['data']['house_list']:
        gta_location_ids.append(val['id_listing'])

fetch_description = FetchDescription(headers, gta_location_ids)

json_formatted_id_descriptions = fetch_description.get_description()

data_dict = json.loads(json_formatted_id_descriptions)
descriptions_df = pd.DataFrame.from_dict(data_dict, orient='index')
# descriptions_df.head(10)
descriptions_df.to_csv("Description_dataset.csv")
