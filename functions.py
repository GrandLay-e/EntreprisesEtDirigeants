from time import sleep
import requests
import json
from pprint import pprint
from CONSTS import *

def get_requests_json(request:str) -> dict:
    sleep(0.15) 
    result = requests.get(request + '&per_page=25')
    if result.status_code != 200:
        return {
            "error" : " Request error !"
        }
    return result.json()

def get_any_infos(search:str) -> dict:

    if len(search) < 3 :
        return {
            "error" : "The your requests mut content at least 3 caracters !"
        }
    result = get_requests_json(API_BASE_URL + search)

    if result['total_results'] == 0:
        return {
            "error" : "No result found for the given request ! "
        }
    return result

def get_infos_by_siren(siren:str) -> dict:
    if len(siren) != 9 or not siren.isdigit():
        return {
            "error" : "The given siren is invalid !"
        }
    result = get_requests_json(API_BASE_URL + siren)
    
    if result.get('total_results') == 0:
        return {
            "error" : "No result found for the given siren ! "
        }
    
    return result.get('results')[0]

def get_all_results(request : str) -> list:
    all_results = []
    result = get_requests_json(request)
    nb_pages = result.get('total_pages')

    print(nb_pages)
    try:
        for i in range(1, nb_pages+1):
            complete_request = request + f"&page={i}"
            all_results.extend(get_requests_json(complete_request).get('results'))
    except Exception as e:
        print("Erreur dans la fonction get_all_results", e)
        pass
    return all_results

def get_dirigeants(company : dict) -> list:
    dirigeants = company.get('dirigeants')
    if len(dirigeants) != 0:
        return filtred_dirigeants_data(dirigeants)        
    return dirigeants

def filtred_dirigeants_data(dirigeants:list[dict]) -> list:
    all_dirigeants = []
    for dirigeant in dirigeants:
        if dirigeant.get('type_dirigeant') == 'personne physique':
            date_naissance = str(dirigeant.get('date_de_naissance'))
            if date_naissance != None:
                date_naissance = '-'.join(date_naissance.split('-')[::-1])

            all_dirigeants.append(
                {
                    'type' : 'personne',
                    'nom' : dirigeant.get('nom'),
                    'prenom' : dirigeant.get('prenoms'),
                    'date_naissance' : date_naissance,
                    'qualite' : dirigeant.get('qualite')
                }
            )
        elif dirigeant.get('type_dirigeant') == 'personne morale':
            all_dirigeants.append(
                {
                    'type' : 'entreprise',
                    'raison_sociale' : dirigeant.get('denomination'),
                    'siren' : dirigeant.get('siren'),
                    'qualite' : dirigeant.get('qualite')
                }
            )
    
    return all_dirigeants

def filter_companys_data(company:dict)-> dict:
    return {key : value 
                  for key, value in company.items() 
                  if key in ['siren',
                            'nom_raison_sociale',
                            'date_creation',
                            'date_fermeture'
                            ]} |\
                            {'adresse' : company.get('siege').get('adresse'),
                            'dirigeants' : get_dirigeants(company)}

# def deep_research(request:str):
#     all_infos = {}
#     all_results = get_all_results(request)
#     for result in all_results:
#         filtred_result = filter_companys_data(result)
#         if filtred_result.get('dirigeants'):
#             for dirigeant in filtred_result.get('dirigeants'):
#                 if dirigeant.get('type') == 'entreprise':
#                     siren = filtred_result.get('dirigeants').get('siren')
#                     filtred_result.get('dirigeants').get('siren').update(
#                         deep_research(API_BASE_URL + siren)
#                     )
#             all_infos.update(filtred_result)
#     return all_infos

def deep_research(request: str, visited=None):
    if visited is None:
        visited = set()

    all_infos = {}
    all_results = get_all_results(request)

    for result in all_results:
        filtred_result = filter_companys_data(result)
        siren = filtred_result.get('siren')

        if siren in visited:
            continue

        visited.add(siren)

        dirigeants = filtred_result.get('dirigeants')

        if dirigeants:
            for dirigeant in dirigeants:
                if dirigeant.get('siren'):  # entreprise
                    child_siren = dirigeant.get('siren')
                    # print(child_siren)
                    dirigeant['details'] = deep_research(
                        API_BASE_URL + child_siren,
                        visited
                    )

        all_infos[siren] = filtred_result

    return all_infos

def write_to_json(json_content, json_file):
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_content, f, indent=4)