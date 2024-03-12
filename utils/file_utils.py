import json

class FileUtils:

    @staticmethod
    def read_from_txt_file(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        return content
    

    @staticmethod
    def read_from_json_file(file_path):
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
        return data
    

    @staticmethod
    def save_as_json_output(output_path, data):
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=4)
    
    
