import re
from types import NoneType
import requests

from pathlib import Path
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
    
    # print(URL, '\n')
    
    page = requests.get(URL)
    content = BeautifulSoup(page.content, 'html.parser')
    
    return content


def info_finder(input_class: str, yearsem: str = 'future') -> dict:
    page_content = content_getter('info', input_class, yearsem)
    results = page_content.find(id="body-tag")
    
    # For finding the hub credits
    hub = results.find('ul', class_="coursearch-result-hub-list")
    
    hub_list = str(hub).split('<li>')[1:]
    
    for idx, val in enumerate(hub_list):
        hub_list[idx] = re.sub('<[^>]+>', '', val).strip()
    
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
    

def section_finder(input_class: str, yearsem: str = 'future') -> list[list]:
    page_content = content_getter('section', input_class, yearsem)

    results = page_content.find(id="body-tag").select_one('table')
    results_sep = str(results).split('</tr>')[1:-1]
    
    single_entries = []
    
    for i in results_sep:
        single_entries.append(i.split('</td>')[:-1])
    
    for section in single_entries:
        for idx, val in enumerate(section):
            section[idx] = re.sub('<[^>]+>', '', val).strip()
            
            if section[idx] == '':
                section[idx] = 'N/A'

    # each entry in single_entries is a list of the following:
    # section, open seats, instructor, type, location, schedule, dates, notes
    
    return single_entries


# global dictionalry for hub credits, don't know if this is a good idea
global hub_dict 
hub_dict = {
    "Philosophical Inquiry and Life’s Meanings" : [1, 0],
    "Aesthetic Exploration" : [1, 0],
    "Historical Consciousness" : [1, 0],

    "Scientific Inquiry I" : [1, 0],
    "Social Inquiry I" : [1, 0],
    "Scientific Inquiry II/Social Inquiry II" : [1, 0],
    
    "Quantitative Reasoning I" : [1, 0],
    "Quantitative Reasoning II" : [1, 0],

    "The Individual in Community" : [1, 0],
    "Global Citizenship and Intercultural Literacy" : [2, 0],
    "Ethical Reasoning" : [1, 0],

    "First-Year Writing Seminar" : [1, 0],
    "Writing, Research, and Inquiry" : [1, 0],
    "Writing-Intensive Course" : [2, 0],
    "Oral and/or Signed Communication" : [1, 0],
    "Digital/Multimedia Expression" : [1, 0],

    "Critical Thinking" : [2, 0],
    "Research and Information Literacy" : [2, 0],
    "Teamwork/Collaboration" : [2, 0],
    "Creativity/Innovation" : [2, 0]
}


def hub_collector(filename, yearsem: str = 'future') -> dict:  
    with open(Path(__file__).parent / filename) as class_txt:
        class_txt = class_txt.read().splitlines()
        
        hub_dict_base = {
            "Philosophical Inquiry and Life’s Meanings" : [1, 0],
            "Aesthetic Exploration" : [1, 0],
            "Historical Consciousness" : [1, 0],

            "Scientific Inquiry I" : [1, 0],
            "Social Inquiry I" : [1, 0],
            "Scientific Inquiry II/Social Inquiry II" : [1, 0],
            
            "Quantitative Reasoning I" : [1, 0],
            "Quantitative Reasoning II" : [1, 0],

            "The Individual in Community" : [1, 0],
            "Global Citizenship and Intercultural Literacy" : [2, 0],
            "Ethical Reasoning" : [1, 0],

            "First-Year Writing Seminar" : [1, 0],
            "Writing, Research, and Inquiry" : [1, 0],
            "Writing-Intensive Course" : [2, 0],
            "Oral and/or Signed Communication" : [1, 0],
            "Digital/Multimedia Expression" : [1, 0],

            "Critical Thinking" : [2, 0],
            "Research and Information Literacy" : [2, 0],
            "Teamwork/Collaboration" : [2, 0],
            "Creativity/Innovation" : [2, 0]
        }
        
        print('\nProgress: ')
        for i in class_txt:
            info = info_finder(i, yearsem)
            if isinstance(info['hub credit'], NoneType):
                break
            
            for j in info['hub credit']:
                try:
                    hub_dict_base[j][1] += 1
                except:
                    if j == 'Scientific Inquiry II' or j == 'Social Inquiry II':
                        hub_dict_base['Scientific Inquiry II/Social Inquiry II'][1] += 1
                        continue
            
            print(f'{i} done')
            
    global hub_dict
    
    if hub_dict_base != hub_dict:
        hub_dict = hub_dict_base.copy()

    return hub_dict


def print_info(info_dict):
    for key in info_dict:  
        if key != 'description':
            print(f'{key}(s): {info_dict[key]} \n')
        else:
            print(f'{key}: {info_dict[key]} \n')
            
    return None

def print_section(section_list):
    print('All sections: \n[section, open seats, instructor, type, location, schedule, dates, notes]\n')
    
    for i in section_list:
        print(f'{i}\n') 
        
    return None 

def print_all_hub():
    global hub_dict
    print('\nTotal Hub Credits: ')
    
    for hub in hub_dict:
        print(f'{hub}: {hub_dict[hub]}')
    

if __name__ == '__main__':
    class_code = 'cdsds210'
    yearsem = '2022 fall'
    
    print(info_finder('cgsrh104', 'future'))
    
    