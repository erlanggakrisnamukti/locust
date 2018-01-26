import os, json, logging, jsonpath_rw_ext, jsonpath_rw
from jsonpath_rw import jsonpath, parse
from . import events
from ast import literal_eval
from flask import make_response

logger = logging.getLogger(__name__)
<<<<<<< b1e43ce7c5ecd3b11d5158c949df85f04c9dc55b
CONFIG_PATH = '/tests/settings/config.json'
=======
config_path = '/tests/settings/config.json'
recur_json = None

def read_file():
    """
    Will read the file and return it as a string with tree view.
    """
    try:
        with open((os.environ['PYTHONPATH'].split(os.pathsep))[-1] + config_path, "r") as data_file:
            data = data_file.read()
    except Exception as err:
        logger.info(err)
        data = "{}"
    return data

def write_file(string_json):
    """
    The `string_json` will overwrite existing configuration. 
    If the previous configuration doesn't exist, then it will create the file.
    """
    status, message = None, None
    try:
        with open((os.environ['PYTHONPATH'].split(os.pathsep))[-1] + config_path, "w") as data_file:
            data_file.write(string_json)
            status = True
            message = 'Configuration has been saved'
            events.master_new_configuration.fire(new_config=string_json)
    except Exception as err:
        logger.info(err)
        status = False
        message = "Can't save the configuration :" + err
    return status, message
>>>>>>> 2601-changes-UI validation jsonpath

class ClientConfiguration:
    """
    This class is a handler for data configuration with JSON data structure.
    """

    config_data = None

    def read_json(self):
        """
        Will get the data of configuration as JSON. 
        It reads configuration file once.
        """
        if self.config_data is None:
            try:
                with open((os.environ['PYTHONPATH'].split(os.pathsep))[-1] + CONFIG_PATH, "r") as data_file:
                    self.config_data = json.load(data_file)
            except Exception as err:
                logger.info(err)
                self.config_data = json.load({})
        return self.config_data

    def update_json_config(self, data_json, json_added, json_path, options, list_column, config_text):
        """
        Write JSON file configuration
        """
        data = data_json

        if(options != "replace"):
            json_target = jsonpath_rw_ext.match(json_path, data)
            if isinstance(json_target[0], dict):
                if len(list_column)==1:
                    json_target[0][list_column[0]] = json_added
                    json_final = json_target[0]
                else:
                    return False, json.dumps(data, indent=4)
            else:
                for json_target_value in json_target[0]:
                    json_added.append(json_target_value)
                json_final = json_added
        else:
            json_final = json_added
        jsonpath_expr = parse(json_path)

        matches = jsonpath_expr.find(data)
        
        if len(matches)==0:
            return make_response(json.dumps({'success':False, 'message':'JSON path not found.'}))
        
        for match in matches:
            data = ClientConfiguration.update_json(data, ClientConfiguration.get_path(match), json_final)
        
        return make_response(json.dumps({'success':True, 'data':json.dumps(data, indent=4)}))

    def add_new_key(self, temppath, new_key_type, config_text):
        
        data = literal_eval(config_text)
        splitpath = filter(None, temppath.split('.'))

        return self.create_exist_path(data, splitpath, new_key_type, 1)

    def create_exist_path(self, input_json, splitpath, type_new_key, index):
        if type(input_json) is dict and input_json:
            if splitpath[index] in input_json:
                input_json = input_json[splitpath[index]]
                self.create_exist_path(input_json, splitpath, type_new_key, index+1)
            else:
                input_json[splitpath[index]] = {}
                self.create_exist_path(input_json[splitpath[index]], splitpath, type_new_key, index+1)
        
        elif type(input_json) is list and input_json:
            print("a")
            for entity in input_json:
                self.create_exist_path(entity, splitpath, type_new_key, index)

        elif index < len(splitpath)-1:
            input_json[splitpath[index]] = {}
            self.create_exist_path(input_json[splitpath[index]], splitpath, type_new_key, index+1)
        
        elif index == len(splitpath)-1:
            if type_new_key == "number":
                input_json[splitpath[index]] = 0
            elif type_new_key == "object":
                input_json[splitpath[index]] = {}
            elif type_new_key == "array":
                input_json[splitpath[index]] = []
            else:
                input_json[splitpath[index]] = ""
            return

        if index == 1:
            if splitpath[index] in input_json:
                return input_json
            else:
                return {splitpath[index]:input_json}
    
    def check_path_exist(data_json, json_path):
        jsonpath_expr = parse(json_path)
        matches = jsonpath_expr.find(data_json)

        if len(matches)==0:
            return False
        else:
            return True

        
    @classmethod    
    def get_path(self, match):
        """
        Return an iterator based upon MATCH.PATH. Each item is a path component,
        start from outer most item.
        """
        if match.context is not None:
            for path_element in ClientConfiguration.get_path(match.context):
                yield path_element
            yield str(match.path)

    @classmethod
    def update_json(self, json, path, value):
        """
        Update JSON dictionary PATH with VALUE. Return updated JSON
        """
        try:
            first = next(path)

            # check if item is an array
            if (first.startswith('[') and first.endswith(']')) or (first.startswith('{') and first.endswith('}')):
                try:
                    first = int(first[1:-1])
                except ValueError:
                    pass
            json[first] = ClientConfiguration.update_json(json[first], path, value)
            return json
        except StopIteration:
            return value

