import requests
from bs4 import BeautifulSoup
import json

from time import sleep
from sys import argv
from pprint import pprint
from urllib.parse import urljoin

from classes import *
from CONSTS import *

def get_requests_json(request:str) -> dict:
    print(f"Requesting : {request}")
    sleep(0.15) 
    result = requests.get(request + '&per_page=25')
    if result.status_code != 200:
        return {
            "error" : " Request error !"
        }
    return result.json()

def get_any_infos(search:str) -> dict:
    if len(search) < 3:
        return {"error": "Search query must be at least 3 characters!"}
    
    result = get_requests_json(API_BASE_URL + search)
    
    if "error" in result:
        return result
    
    if result.get('total_results', 0) == 0:
        return {"error": "No result found for the given request!"}
    
    return result

def get_infos_by_siren(siren:str) -> dict:
    if len(siren) != 9 or not siren.isdigit():
        return {"error": "SIREN must be a 9-digit number!"}
    
    result = get_requests_json(API_BASE_URL + siren)
    
    if "error" in result:
        return result
    
    if result.get('total_results', 0) == 0:
        return {"error": "No result found for the given SIREN!"}
    
    results = result.get('results', [])
    return results[0] if results else {"error": "No data returned"}

def get_all_results(request: str) -> list:
    all_results = []
    result = get_requests_json(request)
    
    if "error" in result:
        return []
    
    nb_pages = result.get('total_pages', 1)
    
    for i in range(1, nb_pages + 1):
        complete_request = request + f"&page={i}"
        page_result = get_requests_json(complete_request)
        if "error" not in page_result:
            page_results = page_result.get('results', [])
            if page_results:
                all_results.extend(page_results)
    
    return all_results

def get_dirigeants(company: dict) -> list:
    dirigeants = company.get('dirigeants', [])
    return filtred_dirigeants_data(dirigeants) if dirigeants else []

def filtred_dirigeants_data(dirigeants: list[dict]) -> list:
    all_dirigeants = []
    for dirigeant in dirigeants:
        type_dir = dirigeant.get('type_dirigeant')
        
        if type_dir == 'personne physique':
            date_raw = dirigeant.get('date_de_naissance')
            date_naissance = '-'.join(date_raw.split('-')[::-1]) if date_raw else None
            
            all_dirigeants.append({
                'nom': dirigeant.get('nom'),
                'prenom': dirigeant.get('prenoms'),  # Fixed: was 'prenoms'
                'date_naissance': date_naissance,
                'qualite': dirigeant.get('qualite')
            })
        elif type_dir == 'personne morale':
            all_dirigeants.append({
                'siren': dirigeant.get('siren'),
                'qualite': dirigeant.get('qualite')
            })
    
    return all_dirigeants

def filter_companys_data(company: dict) -> dict:
    siege = company.get('siege', {})
    
    # Safely extract siege data with null checking
    adresse = siege.get('adresse') if isinstance(siege, dict) else None
    activite_code = siege.get('activite_principale') if isinstance(siege, dict) else None
    activite = get_principal_activity(activite_code) if activite_code else "Unknown"
    
    base_data = {key: value for key, value in company.items() 
                 if key in ['siren', 'nom_raison_sociale', 'date_creation', 'date_fermeture']}
    
    return {
        **base_data,
        'adresse': adresse,
        'dirigeants': get_dirigeants(company),
        'activite_principale': activite
    }

def construct_personne(dirigeant:dict) -> Personne:
    return Personne(
        nom=dirigeant.get('nom'),
        prenom=dirigeant.get('prenom'),
        datNaissance=dirigeant.get('date_naissance'),
        qualite=dirigeant.get('qualite')
    )

def construct_organisation(company:dict) -> Organisation:
    return Organisation(
        siren=company.get('siren'),
        raisonSociale=company.get('nom_raison_sociale'),
        dateCreation=company.get('date_creation'),
        dateFermeture=company.get('date_fermeture'),
        adresse=company.get('adresse'),
        activite=company.get('activite_principale'),
    )

def find_organisation_by_siren(siren:str, organisations:set[Organisation]) -> Organisation:
    for organisation in organisations:
        if organisation.siren == siren:
            return organisation
    return None

def serialize_objects(objs:list) -> list:
    return [obj.to_dict() if hasattr(obj, "to_dict") else str(obj) for obj in objs]

def deep_research(request: str, visited=None, organisations_by_siren=None):
    """Recursively research organisations and their leaders."""
    if visited is None:
        visited = set()
    if organisations_by_siren is None:
        organisations_by_siren = {}
    
    # Extract SIREN from URL safely
    try:
        siren = request.split('=')[-1].split('&')[0]
    except Exception:
        return []
    
    # Check if already visited BEFORE making API call
    if siren in visited:
        existing_org = organisations_by_siren.get(siren)
        return [existing_org] if existing_org else []
    
    # Mark as visited before processing
    visited.add(siren)
    
    # Fetch data from API
    all_results = get_all_results(API_BASE_URL + siren)
    if not all_results:
        return []
    
    all_infos = []
    
    for result in all_results:
        try:
            current_company = filter_companys_data(result)
            organisation = construct_organisation(current_company)
            result_siren = organisation.siren
            
            # Store organization
            organisations_by_siren[result_siren] = organisation
            
            # Process leaders
            dirigeants = current_company.get('dirigeants', [])
            for dirigeant in dirigeants:
                if dirigeant.get('siren'):  # Organisation leader
                    child_orgs = deep_research(
                        API_BASE_URL + dirigeant['siren'],
                        visited,
                        organisations_by_siren
                    )
                    organisation.dirigeants.extend(child_orgs)
                else:  # Person leader
                    organisation.dirigeants.append(construct_personne(dirigeant))
            
            all_infos.append(organisation)
        
        except Exception as e:
            print(f"Error processing organisation: {str(e)}")
            continue
    
    return all_infos

def write_to_json(json_content, json_file):
    if len(json_content) == 0:
        return
    with open(json_file, 'w', encoding='utf-8') as f:
        # pass
        json.dump(serialize_objects(json_content), f, ensure_ascii=False, indent=4)

def get_argv_elements():
    arguments = argv[1:]
    
    if not arguments:
        return {'error': 'No arguments provided. Use -h or --help for usage.'}
    
    if len(arguments) > 2 and arguments[0] not in ['-r', '--research']:
        return {'error': 'Too many arguments. Expected 1-2 arguments.'}
    
    if arguments[0] in ['-s', '--siren']:
        if len(arguments) < 2:
            return {'error': 'SIREN value required after -s or --siren'}
        if len(arguments[1]) != 9 or not arguments[1].isdigit():
            return {'error': 'SIREN must be a 9-digit number'}
        return {'siren': arguments[1]}
    
    elif arguments[0] in ['-r', '--research']:
        if len(arguments) < 2:
            return {'error': 'Search query required after -r or --research'}
        return {'search': ' '.join(arguments[1:])}
    
    elif arguments[0] in ['-h', '--help']:
        if len(arguments) > 1:
            return {'error': 'No arguments should follow -h or --help'}
        return {'help': 1}
    
    else:
        return {'error': f'Unknown argument: {arguments[0]}. Use -h for help.'}

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

def get_principal_activity(code: str) -> str:
    if not code:
        return "No activity code provided"
    
    try:
        request = urljoin(INSEE_CODE_URL, code)
        response = requests.get(request, timeout=5)
        
        if response.status_code != 200:
            return f"Activity lookup failed (HTTP {response.status_code})"
        
        soup = BeautifulSoup(response.text, 'html.parser')
        title_element = soup.select_one('h2.titre-principal')
        
        if not title_element:
            return "Activity code not found"
        
        title_text = title_element.getText().strip()
        parts = title_text.split(':')
        return parts[1].strip() if len(parts) > 1 else title_text
    
    except Exception as e:
        return f"Activity lookup error: {str(e)}"