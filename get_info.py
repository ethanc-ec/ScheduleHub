import requests
from bs4 import BeautifulSoup
from addons import cleaner

def finder(input_class: str, yearsem: str) -> dict:
    code = input_class.upper().split(' ')
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

    for idx, val in enumerate(full_list):
        if not val:
            full_list[idx] = None
    
    full_dict = {
        'prereq' : full_list[1],
        'coreq' : full_list[3],
        'description' : full_list[5],
        'credit' : full_list[6],
        'hub credit' : hub_list[:]
    }

    return cleaner(full_dict)
    

if __name__ == '__main__':
    class_code = 'qst sm 132'
    yearsem = '2022 Fall'
    hub = finder(class_code, yearsem)
    
    for i in hub:
        print(i, hub[i])