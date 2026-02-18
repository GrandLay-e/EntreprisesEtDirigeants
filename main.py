from functions import *

try:
    response = {}
    arguments = get_argv_elements()
    key = list(arguments.keys())[0]
    if key == 'error':
        print(arguments)
    elif key == 'help':
        print(display_documentation())
    else:
        try:
            response = deep_research(API_BASE_URL + arguments[key])
        except Exception as e:
            print(e)
            write_to_json(response, "not_completed.json")
        write_to_json(response, f"{arguments[key]}.json")
        pprint(response)
except KeyboardInterrupt:
    print("quitte")
    print(response)
    write_to_json(response, "not_completed.json")
except Exception as e:
    print(response)
    write_to_json(response, "not_completed.json")