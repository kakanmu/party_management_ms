import json

def get_all_countries():
    with open('party_base/countries.json', 'r') as myfile:
        data = myfile.read()
    country_data = json.loads(data)
    return country_data


def get_states_of_country(id):
    with open('party_base/states.json', 'r') as state_file:
        data = state_file.read()
    states_data = json.loads(data)
    country_states = states_data['countries'][id-1]['states']
    return country_states


def get_industries():
    with open('party_base/industries.json', 'r') as industry_file:
        data = industry_file.read()
    industry_data = json.loads(data)
    return industry_data