from functions import *

# response = get_infos_by_siren('852165745')
response = get_all_pages(API_BASE_URL + 'louis vuitton')

for res in response:
    pprint(filter_companys_data(res))