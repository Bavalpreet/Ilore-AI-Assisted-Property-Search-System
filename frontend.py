
import streamlit as st
import openai
import json
import os
import pandas as pd
import re
from sentence_transformers import SentenceTransformer
import pinecone
from pinecone import Pinecone, ServerlessSpec, PodSpec


openai.api_key = <open_ai_key>

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    return response.choices[0].message.content

def get_entity(text):
    listofparameters = ['province', 'city', 'location', 'bedroom', 'washroom', 'garage', 'price', 'area', 'basement', 'house_type', 'status']

    description_of_parameters = {
        'province': "This will give the province name mentioned in the query",
        'city': "This will give the city name mentioned in the query. Correct the city spelling if not already correct",
        'location': "Complete address of the city",
        'bedroom': "No of bedrooms",
        'washroom': "No of washrooms",
        'garage': "Possible No of vehicles parked",
        'price': '''This will give price of the property The model should output the extracted range of values as individual integer values, separated by commas. For example, if the input is "area: 670,000 to 820,000", the output should be "670,000, 820,000"''',
        'area': '''This will give Area of the property mentioned in squarefeet or sqft units The model should output the extracted range of values as individual integer values, separated by commas. For example, if the input is "area: 670,000 to 820,000", the output should be "670,000, 820,000"''',
        'basement': "Basement available or not",
        'house_type': "Type of the house, such as apartment, basement apartment, condo, 2 storey, 3 storey, Detached, Row/Townhouse or basement, etc",
        'status': "They will give whether they want to buy the property/ for sale or lease/rent."
    }

    prompt = f"""
    Extract the entity with correct spelling from the given text delimited by triple backticks ```{text}``` defined as list of parameters defined in triple backticks ```{listofparameters}```  \
    and for their context can refer to the  description of parameter dictionary again defined in triple backticks ```{description_of_parameters}. Make sure \
    Provide them in JSON format with the entities as keys and the extracted entity as values, if there is no values extracted for any key assign empty string to it.
    """

    llmresponse = get_completion(prompt)
    start_index = llmresponse.find("{")
    end_index = llmresponse.rfind("}") + 1
    json_output = llmresponse[start_index:end_index]
    return json_output

def get_descriptions(result):
    descriptions = []
    for item in result:
        for match in item:
            description = str(match[1]).replace("dict_values(['", "").replace("'])", "")
            descriptions.append(description)
    return descriptions

def main():
    st.title("Ilore property: Your dream home awaits")

    if 'data' not in st.session_state:
        st.session_state.data = {
            "province": "",
            "city": "",
            "location": "",
            "bedroom": "",
            "washroom": "",
            "garage": "",
            "price": "",
            "area": "",
            "basement": "",
            "house_type": "",
            "status": ""
        }

    if 'count' not in st.session_state:
        st.session_state.count = True

    if 'model' not in st.session_state:
        st.session_state.model = SentenceTransformer('distilbert-base-nli-mean-tokens')

    if 'pc' not in st.session_state:
        st.session_state.pc = Pinecone(api_key=<pinecone_api_key>)

    search_query = st.text_input("Search your property")

    if search_query:
        # Extract entities from the search query
        extracted_entities = json.loads(get_entity(search_query))

        # Fill JSON data with extracted entities
        for key, value in extracted_entities.items():
            if key in st.session_state.data:
                st.session_state.data[key] = value


    if st.button("Find Property"):
        missing_fields = [key for key, value in st.session_state.data.items() if value in [None, ""] and key in ["price", "city", "house_type"]]
        if missing_fields and st.session_state.count:
            st.write(f"Please enter {', '.join(missing_fields)}")
            st.session_state.count = False
        else:
            st.session_state.count = True
            descriptions = [search_query]
            embeddings = st.session_state.model.encode(descriptions).tolist()

            index = st.session_state.pc.Index("hs")
            result = []
            temp = []

            results = index.query(vector=embeddings,top_k=5,include_metadata=True)
            #st.write(results)

            property_list = []
            for i, match in enumerate(results['matches'], start=1):
                metadata = match['metadata']
                address = metadata['address']
                description = metadata['description']
                photo_url = metadata['photo']

                if st.session_state.data["city"].lower() == metadata["city"].lower():
                    property_list.append({
                        "address": address,
                        "description": description,
                        "photo_url": photo_url
                    })
            if property_list:
                for i, property_data in enumerate(property_list, start=1):
                    st.write(f"{i}. Address: {property_data['address']}")
                    st.write(f"Description: {property_data['description']}")
                    st.image(property_data['photo_url'], caption='Property Photo', use_column_width=True)
            else:
                st.write("No property found in this city")

            st.session_state.data = {
              "province": "",
              "city": "",
              "location": "",
              "bedroom": "",
              "washroom": "",
              "garage": "",
              "price": "",
              "area": "",
              "basement": "",
              "house_type": "",
              "status": ""
            }
if __name__ == "__main__":
    main()
