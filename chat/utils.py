import hashlib

def generate_chat_name(id1:str, id2:str):
    sorted_strings = sorted([str(id1), str(id2)])
    combined = ''.join(sorted_strings)
    unique_code = hashlib.sha256(combined.encode('utf-8')).hexdigest()
    return unique_code



