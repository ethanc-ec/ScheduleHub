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
    
    # Removing the 'Prereq:' or 'Coreq:' from the respective entries
    if 'Prereq:' in contents['prereq']:
        contents['prereq'] = contents['prereq'].replace('Prereq:', '')
    if 'Coreq:' in contents['coreq']:
        contents['coreq'] = contents['coreq'].replace('Coreq:', '')
    
    
    # Switiching empty strins and arrays to None type, also removes extra whitespace
    for idx, val in enumerate(contents):
        if any([contents[val] == '', contents[val] == [], contents[val] == ['Part of a Hub sequence']]):
            contents[val] = None
            
        elif isinstance(contents[val], str):
            contents[val] = contents[val].strip()

    return contents
     
def clean_input(text: str) -> str:
    test = text.replace(' ', '')
    assert(len(test) == 8)
    
    clean = ''
    
    for i in test:
        clean += i
    
    return f'{clean[0:3]} {clean[3:5]} {clean[5:]}'.upper().split()
    
