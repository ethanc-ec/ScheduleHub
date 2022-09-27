import re
import requests

from bs4 import BeautifulSoup
from help_funcs import *


def content_getter(finder: str, input_class: str, yearsem: str = 'future') -> BeautifulSoup:
    code = clean_input(input_class)
    if yearsem.lower() == 'future':
        time = '*'
    else:
        split_year = yearsem.upper().split(' ')
        time = split_year[0] + '-' + split_year[1]
    
    if finder == 'info':
        URL = f"https://www.bu.edu/phpbin/course-search/search.php?page=w0&pagesize=10&adv=1&nolog=&search_adv_all={code[0]}+{code[1]}+{code[2]}&yearsem_adv={time}&credits=*&pathway=&hub_match=all&pagesize=10"
    
    elif finder == 'section':
        code_joined = ''.join(code).lower()
        URL = f"https://www.bu.edu/phpbin/course-search/section/?t={code_joined}&semester={time}&return=%2Fphpbin%2Fcourse-search%2Fsearch.php%3Fpage%3Dw0%26pagesize%3D10%26adv%3D1%26nolog%3D%26search_adv_all%3D{code[0]}%2B{code[1]}%2B{code[2]}%26yearsem_adv%3D{time}%26credits%3D%2A%26pathway%3D%26hub_match%3Dall"
    
    print(URL)
    
    page = requests.get(URL)
    content = BeautifulSoup(page.content, 'html.parser')
    
    return content


def info_finder(input_class: str, yearsem: str = 'future') -> dict:
    page_content = content_getter('info', input_class, yearsem)
    results = page_content.find(id="body-tag")
    
    # For finding the hub credits
    hub = results.find('ul', class_="coursearch-result-hub")
    
    hub_list = str(hub).replace('</li>', '').replace('</ul>]', '').split('<li>')[1:]
    
    # For finding the prereq, coreq, description and credit
    full = results.find('div', class_="coursearch-result-content-description")

    # Gets: [prereq, coreq,description, numerical credit]
    full_list = full.text.splitlines()

    full_dict = {
        'prereq' : full_list[1],
        'coreq' : full_list[3],
        'description' : full_list[5],
        'credit' : full_list[6],
        'hub credit' : hub_list[:]
    }
    
    cleaned = cleaner(full_dict)
    
    return cleaned
    

def section_finder(input_class: str, yearsem: str = 'future') -> dict:
    page_content = content_getter('section', input_class, yearsem)
    results = page_content.find(id="body-tag").find('tr', class_="first-row").find_next_siblings('tr')
    for idx, val in enumerate(results):
        results[idx] = re.sub('<[^>]+>', '', str(val))[1:]
    
    organized = organize_class(results)
    
    return organized
    
    

if __name__ == '__main__':
    class_code = 'cdsds100'
    yearsem = '2022 fall'
    
    print_hub, print_sections = True, True
    
    hub = info_finder(class_code, yearsem)
    if print_hub:
        for i in hub:
            if i != 'description':
                print(f'{i}(s): {hub[i]} \n')
            else:
                print(f'{i}: {hub[i]} \n')
    
    sections = section_finder(class_code, yearsem)
    if print_sections:
        print('All sections:')
        for i in sections:
            print(f'{i}\n')