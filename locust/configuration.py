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

    def update_json_config(self, new_config_data_added, json_path, options, list_column, config_text, **kwargs):
        """
        Write JSON file configuration with all data
        """
        data = kwargs.get("data_each_iter", literal_eval(config_text))
        if(options != "replace"):
            json_target = jsonpath_rw_ext.match(json_path, data)
            if isinstance(json_target[0], dict):
                if len(list_column)==1:
                    json_target[0][list_column[0]] = new_config_data_added
                    json_final = json_target[0]
                else:
                    response = {'success':False, 'data':{'json_data':json.dumps(data)}, 'message':'JSON and CSV data type not match'}
            else:
                for json_target_value in json_target[0]:
                    new_config_data_added.append(json_target_value)
                json_final = new_config_data_added
        else:
            json_final = new_config_data_added
        jsonpath_expr = parse(json_path)
        matches = jsonpath_expr.find(data)

        if len(matches)==0:
            response = {'success':False, 'message':'JSON path not found.'}
        else:
            for match in matches:
                data = self.update_json(data, self.get_path(match), json_final)

            response = {'success':True, 'data':{'json_data':json.dumps(data)}, 'missing_key_message':''}
            
        return response

    def add_new_key(self, temppath, new_key_type, config_text):
        """
        Split the jsonpath and trigger create_path
        """
        data = literal_eval(config_text)
        splitpath = filter(None, temppath.split('.'))

        return json.dumps(self.create_path(data, splitpath, new_key_type, 1))

    def check_key(self, input_json, json_path):
        """
        Split path and trigger check_exist_path
        """
        splitpath = filter(None, json_path.split('.'))
        status, message = self.check_exist_path(input_json, splitpath, 1)
        return status, message

    def create_path(self, input_json, splitpath, type_new_key, index):
        """
        Recursively search for jsonpath in json and create not found jsonpath
            **there are several to do for checking json, such as :
                - check dictionary or list type and trigger next iteration
                - create path on json when jsonpath not found until last index
                - for the last index, the object will created depend on type_new_key 
        """
        initial_json = input_json
        if type(input_json) is dict and input_json:
            if splitpath[index] in input_json:
                input_json = input_json[splitpath[index]]
                if index<len(splitpath):
                    self.create_path(input_json, splitpath, type_new_key, index+1)
                else:
                    return
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
            else:
                input_json[splitpath[index]] = {}
                self.create_path(input_json[splitpath[index]], splitpath, type_new_key, index+1)
        
        elif type(input_json) is list and input_json:
            for entity in input_json:
                self.create_path(entity, splitpath, type_new_key, index)

        elif index < len(splitpath)-1:
            input_json[splitpath[index]] = {}
            self.create_path(input_json[splitpath[index]], splitpath, type_new_key, index+1)
        
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
                initial_json[splitpath[index]] = input_json
                return initial_json
    
    def check_exist_path(self, input_json, splitpath, index):
        """
        Recursively check jsonpath
        """ 
        if index > len(splitpath)-1:
            return True, "Path exist"
        elif type(input_json) is dict and input_json:
            if splitpath[index] in input_json:
                input_json = input_json[splitpath[index]]
                status, message = self.check_exist_path(input_json, splitpath, index+1)
            else:
                return False, splitpath[index]
        elif type(input_json) is list and input_json:
            for entity in input_json:
                status, message = self.check_exist_path(entity, splitpath, index)
                if not status:
                    break
        return status, message

    def compare_json_csv_count(self, input_json, splitpath, index, new_config_data_added):
        """
        Compare json and csv size
        """ 
        if index > len(splitpath)-2:
            if(len(new_config_data_added) != len(input_json)):
                return True
            else:
                return False

        elif type(input_json) is dict and input_json:
            if splitpath[index] in input_json:
                input_json = input_json[splitpath[index]]
                status = self.compare_json_csv_count(input_json, splitpath, index+1, new_config_data_added)

        elif type(input_json) is list and input_json:
            for entity in input_json:
                status = self.compare_json_csv_count(entity, splitpath, index, new_config_data_added)

        return status

    def convert_to_json(self, csv_stream, multiple_data_headers):
        """
        Convert csv data to json
        """
        if(multiple_data_headers and len(multiple_data_headers) > 0):
            tempStr = csv_stream.convert(multiple_data_headers)
            json_added = tempStr
        else:
            tempStr = csv_stream.convert([])
            if len(csv_stream.get_columns_name()) > 1:
                json_added = tempStr
            else:
                json_added = tempStr.get(csv_stream.get_columns_name()[0])
        
        return json_added

    def get_last_variable(self, jsonpath):
        """
        Get last variable from jsonpath
        """
        splitpath = filter(None, jsonpath.split('.'))
        return splitpath[-1]

    def update_json_each_row_depend_on_key(self, new_config_data_added, json_path, options, list_column, config_text, key_json, key_csv):
        """
        Write JSON file configuration each data json array and csv row depends on a key
        """ 
        temppath = json_path.split('.')
        if(len(temppath[len(temppath)-2]) > 0):
            response = {'success':False, 'error_type':'JSON not supported', 'message':'Your JSON Path not supported. Please change'}
        else:
            data = literal_eval(config_text)

            temppath = filter(None, temppath)
            data = literal_eval(config_text)
            input_method = "on_key"

            status, data = self.path_preparation(new_config_data_added, data, temppath, 1, options, list_column, config_text, input_method, key_json=key_json, key_csv=key_csv)
            json_data = data[0]
            missing_key = data[1]

            if len(data[1]) == 0:
                missing_key_message = ""
            elif len(data[1]) == len(new_config_data_added):
                missing_key_message = "All data failed to insert"
            else:
                missing_key_message = "Insert success but some data failed : " + ','.join(data[1])
            response = {'success':True, 'data':{'json_data':json_data, 'missing_key':missing_key}, 'missing_key_message':missing_key_message}
        
        return response
        
    def update_json_each_row_on_sequence(self,new_config_data_added, json_path, options, list_column, config_text):
        """
        Write JSON file configuration each data json array and csv row on sequence
        """ 
        temppath = json_path.split('.')
        if(len(temppath[len(temppath)-2]) > 0):
            response = {'success':False, 'error_type':'JSON not supported', 'message':'Your JSON Path not supported. Please change'}
            # return make_response(json.dumps({'success':False, 'message':'Your JSON Path not supported. Please change'}))
        else:
            temppath = filter(None, temppath)
            data = literal_eval(config_text)
            if self.compare_json_csv_count(data, temppath, 1, new_config_data_added):
                response = {'success':False, 'error_type':'data different', 'message':'The amount of data between JSON and CSV is different'}
            else:
                input_method = "sequence"
            
                status, data = self.path_preparation(new_config_data_added, data, temppath, 1, options, list_column, config_text, input_method)
                if status:
                    json_data = data[0]
                    missing_key = data[1]
                    response = {'success':status, 'data':{'json_data':json_data, 'missing_key':missing_key}, 'missing_key_message':''}
                else:
                    response = {'success':status, 'error_type':data['error_type'], 'message':data['message']}

        return response

    def path_preparation(self, new_config_data_added, data_json, splitpath, index, options, list_column, config_text, input_method, **kwargs):
        """
        Recursive method to find the path of JSONPath
        """
        initial_json = data_json
        if index == len(splitpath)-1:
            iteration_json_config = None
            if input_method == "sequence":
                status, response = True, self.input_row_sequence_method(new_config_data_added, splitpath, config_text, options, list_column)
            else:
                status, response = True, self.input_depend_on_key_method(new_config_data_added, splitpath, config_text, options, list_column, kwargs.get("key_json", ""), kwargs.get("key_csv", ""), data_json)

            return status, response

        elif type(data_json) is dict and  data_json:
            data_json = data_json[splitpath[index]]
            status, response = self.path_preparation(new_config_data_added, data_json, splitpath, index+1, options, list_column, config_text, input_method, key_json=kwargs.get("key_json", ""), key_csv=kwargs.get("key_csv", ""))
        
        elif type(data_json) is list and data_json:
            for entity in data_json:
                status, response = self.path_preparation(new_config_data_added, data_json, splitpath, index, options, list_column, config_text, input_method, key_json, key_csv)
                if not status:
                    break

        if status:
            return True, response
        else:
            return False, response

    def input_row_sequence_method(self, new_config_data_added, splitpath, config_text, options, list_column):
        """
        Process input csv data by sequence
        """
        for y in xrange(0,len(new_config_data_added)):
            json_path_iter = '.'.join(splitpath[:-1]) + "[" + str(y) + "]." + splitpath[-1]
            if y==0:
                data_each_iter = literal_eval(config_text)
            else:
                data_each_iter = literal_eval(iteration_json_config['data']['json_data'])
            input = []
            input.append(new_config_data_added[y])
            #Passing data_each_iter for every iteration. ex: iteration 1 will use data from iteration 0, iteration 2 will use data from iteration 1
            iteration_json_config = self.update_json_config(input, json_path_iter, options, list_column, config_text, data_each_iter=data_each_iter)
        return iteration_json_config['data']['json_data'], []

    def input_depend_on_key_method(self, new_config_data_added, splitpath, config_text, options, list_column, key_json, key_csv, data_json):
        """
        Process input csv data by csv key and json key
        """
        iteration_json_config = None
        missing_data_key_csv = []
        temp_index_search = []
        ori_options = options
        for y in xrange(0,len(new_config_data_added)):
            index_search = self.find_index(data_json, key_json, new_config_data_added[y][key_csv])
            if index_search in temp_index_search:
                options = "append"
            else:
                temp_index_search.append(index_search)
                options = ori_options
            if index_search < 0:
                missing_data_key_csv.append(new_config_data_added[y][key_csv])
            else:
                json_path_iter = '.'.join(splitpath[:-1]) + "[" + str(index_search) + "]." + splitpath[-1]
                data_each_iter = literal_eval(config_text) if y==0 else literal_eval(iteration_json_config['data']['json_data'])

                new_config_data_added[y].pop(key_csv)
                input = [new_config_data_added[y]]

                #Passing data_each_iter for every iteration. ex: iteration 1 will use data from iteration 0, iteration 2 will use data from iteration 1
                iteration_json_config = self.update_json_config(input, json_path_iter, options, list_column, config_text, data_each_iter=data_each_iter)
        return iteration_json_config['data']['json_data'], missing_data_key_csv

    @classmethod    
    def get_path(self, match):
        """
        Return an iterator based upon MATCH.PATH. Each item is a path component,
        start from outer most item.
        """
        if match.context is not None:
            for path_element in self.get_path(match.context):
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
            json[first] = self.update_json(json[first], path, value)
            return json
        except StopIteration:
            return value

    @classmethod
    def find_index(self, dicts, key, value):
        """
        To find index of key dictionary, given the value
        """
        for i, d in enumerate(dicts):
            if d[key] == value:
                return i
        else:
            return -1

    @classmethod
    def get_config_data(temppath):
        for x in xrange(1,len(temppath)-1):
            if(len(temppath[x]) > 0):
                data = data[temppath[x]]
        return data
