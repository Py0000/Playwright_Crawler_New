import json
import os

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
    def read_from_json_zipped_file(file_in_zipped_path):
        data = json.load(file_in_zipped_path)
        return data
    
    @staticmethod
    def save_as_txt_output(output_path, data):
        with open(output_path, 'w') as f:
            for entry in data:
                f.write(f"{entry}\n")

    @staticmethod
    def save_as_json_output(output_path, data):
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=4)
    

    @staticmethod
    def extract_file_path_from_zipped(zip_file, ref_type, file_object):
        relative_path = os.path.join(ref_type, file_object)
        file_path = next((zipinfo.filename for zipinfo in zip_file.infolist() if relative_path in zipinfo.filename), None)
        return file_path

    
    
