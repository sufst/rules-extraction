import json
    
def write_to_json(data, file_path='parsed.json'):
    # todo - check validity of file_path (already has '.json'; if not, append)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)