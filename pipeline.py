#import statements
import openai
import os
import json
import requests

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

openai.api_key  = os.getenv('OPENAI_API_KEY')


client = openai.OpenAI()

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    return response.choices[0].message.content

def get_parameters(text):
    """Extract entities from the given text."""
    listofparameters = ['province', 'city', 'location', 'bedroom', 'washroom', 'garage', 'price', 'area', 'basement']
    description_of_parameters = {
        'province': "This will give the province name mentioned in the query",
        'city': "This will give the city name mentioned in the query",
        'location': "Complete address of the city",
        'bedroom': "No of bedrooms",
        'washroom': "No of washrooms",
        'garage': "Possible No of vehicles parked",
        'price':'''This will give price of the property The model should output the extracted range of values as individual integer values, separated by commas. For example, if the input is "area: 670,000 to 820,000", the output should be "670,000, 820,000"''',
        'area':'''This will give Area of the property mentioned in squarefeet or sqft units The model should output the extracted range of values as individual integer values, separated by commas. For example, if the input is "area: 670,000 to 820,000", the output should be "670,000, 820,000"''',
        'basement': "Basement available or not",
        'house_type': "C. for condo apartment, D. for Detached, A. for Row/Townhouse"
    }
    prompt = f"""
    Extract the entity from the given text delimited by triple backticks ```{text}``` defined as list of parameters defined in triple backticks ```{listofparameters}```  \
    and for their context can refer to the  description of parameter dictionary again defined in triple backticks ```{description_of_parameters}. Make sure \
    Provide them in JSON format with the entities as keys and the extracted entity as values.
    """
    llmresponse = get_completion(prompt)
    response_dictionary = json.loads(llmresponse)
    return response_dictionary

def fetch_lat_lon(search_term):
    """Fetch latitude and longitude based on search term."""
    url = "https://housesigma.com/bkv2/api/search/address_v2/suggest"
    payload = {"lang": "en_US", "province": "ON", "search_term": search_term}
    headers = {'Authorization': 'Bearer 20240127frk5hls1ba07nsb8idfdg577qa'}
    response = requests.post(url, headers=headers, data=payload)
    response_dict = json.loads(response.text)
    place_list = response_dict.get('data', {}).get('place_list', [])
    if place_list:
        lon = place_list[0].get('lng')
        lat = place_list[0].get('lat')
    return lat, lon

def fetch_listing_ids(lat, lon, response_dictionary):
    """Fetch listing IDs based on location and other parameters."""
    url = "https://housesigma.com/bkv2/api/search/mapsearchv3/listing"
    payloadListing = {
        "lang": "en_US",
        "province": "ON",
        "basement": [],
        "open_house_date": 0,
        "listing_type": ["all"],
        "house_type": ["D."],
        "price": [0, 6000000],
        "front_feet": [0, 100],
        "square_footage": [0, 4000],
        "bedroom_range": [0, 3],
        "bathroom_min": 0,
        "garage_min": 0,
        "lat1": 43.21272347526204,
        "lon1": -79.20238080673137
    }
    payloadListing["lat1"] = lat
    payloadListing["lon1"] = lon
    payloadListing["bedroom_range"] = [response_dictionary['bedroom'], response_dictionary['bedroom']]
    payloadListing["square_footage"] = [0, response_dictionary['area']]
    payloadListing["price"] = [0, response_dictionary['price']]
    headers = {'Authorization': 'Bearer 20240127frk5hls1ba07nsb8idfdg577qa'}
    payloadListing = json.dumps(payloadListing)
    response = requests.post(url, headers=headers, data=payloadListing)
    data_dict = json.loads(response.text)
    all_ids = data_dict['data']['list'][0]['ids']
    return all_ids

def fetch_listing_details(all_ids):
    """Fetch detailed information for the listing IDs."""
    url = "https://housesigma.com/bkv2/api/listing/preview/many"
    payload = {'lang': 'en_US', 'province': 'ON', 'id_listing': all_ids}
    manydetail = json.dumps(payload)
    headers = {
        'Authorization': 'Bearer 20240127frk5hls1ba07nsb8idfdg577qa',
        'Content-Type': 'application/json'
                }
    response = requests.post(url, headers=headers, data=manydetail)
    manydetail_dict = json.loads(response.text)
    return manydetail_dict

# Input text
text = """
In search for a house with 2 garages, 2-bedroom, 1 bathroom in the range 670,000 to 820,000 which is in Brampton, Ontario.
"""

# Get entities from the llm
response_dictionary = get_parameters(text)

# Extracting the search term
# search_term = response_dictionary.get('location', response_dictionary['province'] + response_dictionary['city'])
if response_dictionary['location']:
    search_term = response_dictionary['location']
else:
    search_term = response_dictionary['city'] + ", "+response_dictionary['province']

# Fetch latitude and longitude
lat, lon = fetch_lat_lon(search_term)

# Fetch listing IDs
all_ids = fetch_listing_ids(lat, lon, response_dictionary)

# Fetch listing details
listing_details = fetch_listing_details(all_ids)
print(listing_details)
