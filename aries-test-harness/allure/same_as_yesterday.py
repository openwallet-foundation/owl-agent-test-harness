import os
import json
import sys


if __name__ == "__main__":
    kgr_results = {}
    with open("./The-KGR-file.json", 'r') as tkf:
        json_kgr_results = tkf.read()
        kgr_results = json.loads(json_kgr_results)

    overall_results = True
    new_kgr_results = {}
    for filename in os.listdir("./allure-results/"):
        if filename.endswith(".json"):
            with open(os.path.join("./allure-results/", filename), 'r') as f: # open in readonly mode
                json_results = f.read()
                results = json.loads(json_results)
                fullName = results["fullName"] + ":" + results["name"]
                if "parameters" in results:
                    result_params = {}
                    for param in results["parameters"]:
                        result_params[param["name"]] = param["value"]
                    fullName = fullName + "(" + json.dumps(result_params, sort_keys=True) + ")"
                status = results["status"]
                new_kgr_results[fullName] = status
                if fullName in kgr_results.keys():
                    if not kgr_results[fullName] == status:
                        print("Result differs for:", fullName)
                        overall_results = False
                else:
                    print("KGR missing for:", fullName)
                    overall_results = False

    with open("./New-KGR-File.json", 'w') as tnkf:
        json_kgr_results = json.dumps(new_kgr_results)
        tnkf.write(json_kgr_results)

    if overall_results:
        print("Same as yesterday")
        sys.exit(0)
    else:
        print("Different from yesterday")
        sys.exit(1)
