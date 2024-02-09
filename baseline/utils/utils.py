
def get_api_key(api_key_file):
    with open(api_key_file, 'r') as file:
        api_key = file.readline().strip()
    
    return api_key

