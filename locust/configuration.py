import os, json, logging, jsonpath_rw_ext, jsonpath_rw
from jsonpath_rw import jsonpath, parse
from . import events
from ast import literal_eval
from flask import make_response

logger = logging.getLogger(__name__)
CONFIG_PATH = '/tests/settings/config.json'

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

    def add_new_key(self, parent_path, new_key_name, new_key_type, config_text):
        data = literal_eval(config_text)
        data_target = data
        temppath = parent_path.split('.')
        child_split = new_key_name.split('.')

        counts = {}
        branch = counts
        for part in child_split[1:]:
            if part == child_split[-1]:
                if new_key_type == "string":
                    branch = branch.setdefault(part, "")
                elif new_key_type == "object":
                    branch = branch.setdefault(part, {})
                else:
                    branch = branch.setdefault(part, [])
            else:
                branch = branch.setdefault(part, {})

        for x in xrange(1,len(temppath)):
            data_target = data_target[temppath[x]]

        for y in xrange(0,len(data_target)):
            data_target[y][child_split[0]] = counts
            path = parent_path + "[" + str(y) + "]"
            jsonpath_expr = parse(path)
            matches = jsonpath_expr.find(data)

            for match in matches:
                data = ClientConfiguration.update_json(data, ClientConfiguration.get_path(match), data_target[y])

        return data
        
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

