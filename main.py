import time

from graph_functions import *
import os

output_dir = "outputs"
response = {}
start = time.time()

try:
    arguments = get_argv_elements()
    graph_format = 'svg' 
    if len(arguments.keys()) == 2:
            graph_format = arguments['output']
    search_option = list(arguments.keys())[0]

    if search_option == 'error':
        print(arguments)
    elif search_option == 'help':
        print(display_documentation())
    else:
        try:
            response = deep_research(API_BASE_URL + arguments[search_option])
            if len(response) == 0:
                print("No data found for the given SIREN.")
                exit()
            dot = define_dot()
            output_dir = f"outputs/{arguments[search_option]}"
            os.makedirs(output_dir, exist_ok=True)
            add_nodes_and_edges(dot, response)
            dot.render(f"{output_dir}/graph", format=graph_format, cleanup=True)
            write_to_json(response, f"{output_dir}/response.json")
            end = time.time()
            print(f"Execution time: {end - start:.2f} seconds")
        except Exception as e:
            print(e)
            write_to_json(response, f"{output_dir}/not_completed.json")
        write_to_json(response, f"{output_dir}/response.json")
except KeyboardInterrupt:
    print("quitte")
    print(response)
    write_to_json(response, f"{output_dir}/not_completed.json")
except Exception as e:
    print(e)
    write_to_json(response, f"{output_dir}/not_completed.json")