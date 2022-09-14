def filter_numerical(string: str) -> str:
    result = ''
    for char in string:
        if char in '1234567890':
            result += char
    return result

def cleaner(contents: dict) -> dict:
    
    # Description cleaner
    while True:
        if '  ' in contents['description']:
            contents['description'] = contents['description'].replace('  ', ' ')
        else:
            break
        
    # Credit cleaner
    contents['credit'] = filter_numerical(contents['credit'])

    
    return contents