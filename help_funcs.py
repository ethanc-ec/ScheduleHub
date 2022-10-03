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
    for i in contents:
        if any([contents[i] == '', contents[i] == [], contents[i] == ['Part of a Hub sequence']]):
            contents[i] = None
            
        elif isinstance(contents[i], str):
            contents[i] = contents[i].strip()

    return contents
     
     
def clean_input(text: str) -> str:
    test = text.replace(' ', '')
    assert(len(test) == 8)
    
    clean = ''
    
    for i in test:
        clean += i
    
    return f'{clean[0:3]} {clean[3:5]} {clean[5:]}'.upper().split()


def organize_class(list_of_classes: list) -> list:
    organized = [['section', 'professor', 'location', 'days', 'class_time']]
    for i in list_of_classes:
        temp = i.split()

        # section, professor, location
        spl_temp = f'{temp[0]}_{temp[1]}'
        section = spl_temp[:2]
        professor = spl_temp[2:-6]
        location = spl_temp[-6:] + temp[2][:3]
        
        days = temp[2][3:]
        
        class_time = temp[3] + temp[4] + temp[5][:2]
        
        infolist = [section, professor, location, days, class_time]
    
        organized.append(infolist)
    
    return organized