def create_exist_path(input_json, splitpath, type_new_key, index):

        if type(input_json) is dict and input_json:
            if splitpath[index] in input_json:
                input_json = getJSON(splitpath[index], input_json)
                create_exist_path(input_json, splitpath, type_new_key, index+1)
            else:
                input_json[splitpath[index]] = {}
                create_exist_path(getJSON(splitpath[index], input_json), splitpath, type_new_key, index+1)
        
        elif type(input_json) is list and input_json:
            for entity in input_json:
                create_exist_path(entity, splitpath, type_new_key, index)

        elif index < len(splitpath)-1:
            input_json[splitpath[index]] = {}
            create_exist_path(getJSON(splitpath[index], input_json), splitpath, type_new_key, index+1)
        
        elif index == len(splitpath)-1:
            if type_new_key == "string":
                input_json[splitpath[index]] = ""
            elif type_new_key == "object":
                input_json[splitpath[index]] = {}
            else:
                input_json[splitpath[index]] = []
            return

        if index == 1:
            if splitpath[index] in input_json:
                return input_json
            else:
                return {splitpath[index]:input_json}

def getJSON(key, json):
    if (key == "$"): return json
    return json[key]


def main():
    json = {
        "erlangga" : {}
    }
    splitpath = ["$","erlangga","alamat"]
    type_new_key = "string"
    json = create_exist_path(json, splitpath, type_new_key, 1)
    print(json)

main()