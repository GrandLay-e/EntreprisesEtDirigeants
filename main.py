from functions import *

recherche = input("Qu'est-ce que vous cherchez ? : ")
response = deep_research(API_BASE_URL + recherche)
write_to_json(response, f"{recherche}.json")

