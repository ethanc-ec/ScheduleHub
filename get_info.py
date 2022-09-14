import requests
from bs4 import BeautifulSoup

def finder(input_class: str, yearsem: str) -> dict:
    code = input_class.split(' ')
    if yearsem == 'future':
        time = '*'
    else:
        split_year = yearsem.split(' ')
        time = split_year[0] + '-' + split_year[1].upper()
    
    URL = f"https://www.bu.edu/phpbin/course-search/search.php?page=w0&pagesize=10&adv=1&nolog=&search_adv_all={code[0]}+{code[1]}+{code[2]}&yearsem_adv={time}&credits=*&pathway=&hub_match=all"
    # print(URL)
    
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    results = soup.find(id="body-tag")
    
    # For finding the hub credits
    hub = results.find_all('ul', class_="coursearch-result-hub-list")

    # Gets: [hub credits]
    hub_list = str(hub).replace('</li>', '').replace('</ul>]', '').split('<li>')[1:]
    
    # For finding the prereq, coreq, description and credit
    full = results.find('div', class_="coursearch-result-content-description")

    # Gets: [prereq, coreq, ?, description, numerical credit]
    full_list = full.text.splitlines()
    
    full_dict = {}
    
    for idx, val in enumerate(['unknown_1', 'prereq', 'unknown_2', 'coreq', 'unknown3', 'description', 'credit', 'hub credit']):
        if idx < 7 and full_list[idx]:
            full_dict[val] = full_list[idx]
        elif idx == 7:
            full_dict[val] = hub_list    
        else:
            full_dict[val] = None

    return cleaner(full_dict)

def cleaner(contents: dict) -> dict:
    while True:
        if '  ' in contents['description']:
            contents['description'] = contents['description'].replace('  ', ' ')
        else:
            break
    
    return contents
    
if __name__ == '__main__':
    class_code = 'CDS DS 120'
    yearsem = '2022 Fall'
    hub = finder(class_code, yearsem)
    
    for i in hub:
        print(i, hub[i])