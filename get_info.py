import requests
from bs4 import BeautifulSoup

def finder(input_class, yearsem):
    code = input_class.split(' ')
    if yearsem == 'future':
        time = '*'
    else:
        split_year = yearsem.split(' ')
        time = split_year[0] + '-' + split_year[1].upper()
    
    URL = f"https://www.bu.edu/phpbin/course-search/search.php?page=w0&pagesize=10&adv=1&nolog=&search_adv_all={code[0]}+{code[1]}+{code[2]}&yearsem_adv={time}&credits=*&pathway=&hub_match=all"
    
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    results = soup.find(id="body-tag")
    
    # For finding the hub credits
    hub = results.find_all('ul', class_="coursearch-result-hub-list")

    hub_list = str(hub).replace('</li>', '').replace('</ul>]', '').split('<li>')[1:]
    # Gets: [hub credits]
    
    # For finding the prereq, coreq, description and credit
    other = results.find_all('div', class_="coursearch-result-content-description")

    other_list = str(other).replace('</p>', ' ').splitlines()[1:-1]
    # Gets: [prereq, coreq, ?, description, numerical credit]
    
    for idx, val in enumerate(other_list):
        if val == '<p> ':
            other_list.remove(val)
        
    # [prereq, coreq, description, numerical credit, hub credits]
    full_list = [hub_list]
    
    
    print(full_list, \
        other_list)
    
    
    
    info_list = [hub_list]
    
    return info_list
    
if __name__ == '__main__':
    class_code = 'CDS DS 100'
    yearsem = '2022 Fall'
    hub = finder(class_code, yearsem)
    
    for i in hub:
        print(i)