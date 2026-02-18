import requests
from bs4 import BeautifulSoup
import json

from time import sleep
from sys import argv
from pprint import pprint
from urllib.parse import urljoin

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

    try:
        for i in range(1, nb_pages+1):
            complete_request = request + f"&page={i}"
            all_results.extend(get_requests_json(complete_request).get('results'))
    except Exception as e:
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
                    # 'type' : 'personne',
                    'nom' : dirigeant.get('nom'),
                    'prenom' : dirigeant.get('prenoms'),
                    'date_naissance' : date_naissance,
                    'qualite' : dirigeant.get('qualite')
                }
            )
        elif dirigeant.get('type_dirigeant') == 'personne morale':
            all_dirigeants.append(
                {
                    # 'type' : 'entreprise',
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
                            'dirigeants' : get_dirigeants(company),
                            'activite_principale' : get_principal_activity(company.get('siege').get('activite_principale'))}

def deep_research(request: str, visited=None):
    print(request)
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
                    dirigeant['details'] = deep_research(
                        API_BASE_URL + child_siren,
                        visited
                    )

        all_infos[siren] = filtred_result

    return all_infos

def write_to_json(json_content, json_file):
    if len(json_content) == 0:
        return
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_content, f, ensure_ascii=False, indent=4)

def get_argv_elements():
    arguments = argv[1:]
    if len(arguments) > 2 \
        and (arguments[0] != '-r' and arguments[0] != '--research'):
        return {'error' : 'too many arguments sent, two required ! '}
    if arguments[0] == '-s' or arguments[0] == '--siren':
        if len(arguments[1]) != 9 or not arguments[1].isdigit():
            return {"error" : "The given siren is invalid !"}
        return {'siren' : arguments[1]}
    elif arguments[0] == '-r' or arguments[0] == '--research' :
        return {'search' : ' '.join(arguments[1:])}
    elif arguments[0] == '-h' or arguments[0] == '--help':
        if len(arguments) > 1:
             return {'error' : 'too many arguments sent, two required ! '}
        return {'help' : 1}
    else:
        return {'error' : 'invalid input !'}

def display_documentation():
    return f"""
    Welcome.

    To use this application, execute it with one of the following parameters:

    -s, --siren <9-digit number>
            Search using a valid SIREN number (e.g., 123456789).

    -r, --research <query>
            Perform a research query with the specified text.

    -h, --help
            Display this help message.

    """

def get_principal_activity(code:str) -> str:
    request = urljoin(INSEE_CODE_URL, code)
    response = requests.get(request)
    if response.status_code != 200:
        return "Request error !"
    else:
        soup = BeautifulSoup(response.text, 'html.parser')
        principal_title = soup.select_one('h2.titre-principal').getText().split(':')[1]
        return principal_title        