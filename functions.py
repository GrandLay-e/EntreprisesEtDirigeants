import requests
import json
from pprint import pprint


from django.db.models.expressions import result

from CONSTS import *
def get_requests_json(request:str) -> dict:
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

def get_person_infos() -> dict:
    pass

def get_all_pages(request : str) -> list:

    all_pages = []
    result = get_requests_json(request)
    nb_pages = result.get('total_pages')

    for i in range(1, nb_pages+1):
        complete_request = request + f"&page={i}"
        all_pages.extend(get_requests_json(complete_request).get('results'))
        
    return all_pages

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
                    # 'date_naissance' : str(dirigeant.get('date_de_naissance').split('-')[::-1]),
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
                             'date_fermeture']} \
                            | {'adresse' : company.get('siege').get('adresse'),
                               'dirigeants' : get_dirigeants(company)}