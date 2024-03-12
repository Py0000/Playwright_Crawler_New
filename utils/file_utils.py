
class FileUtils:

    @staticmethod
    def read_from_txt_file(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
        return content
