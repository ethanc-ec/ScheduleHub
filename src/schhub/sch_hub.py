import re
import requests
import json
import sys

from time import perf_counter
from pathlib import Path
from bs4 import BeautifulSoup

"""
Functions for scraping the information from the website
Can also grab from 'data_file.json'
"""

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
    
    print(URL, '\n')
    
    page = requests.get(URL)
    
    content = BeautifulSoup(page.content, 'html.parser')
    
    return content

def info_finder(input_class: str, yearsem: str, skip:str = False) -> dict:
    if in_data(input_class) and not skip:
        class_data = pull_data(input_class)
        return class_data
    
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
    
    data_writing = {
        input_class : cleaned
    }
    if not skip:
        write_data(data_writing)
    
    return cleaned

def hub_finder(input_class: str, yearsem: str = 'future') -> list:
    page_content = content_getter('info', input_class, yearsem)
    results = page_content.find(id="body-tag")
    
    # For finding the hub credits
    hub = results.find('ul', class_="coursearch-result-hub-list")
    
    hub_list = str(hub).split('<li>')[1:]
    
    for idx, val in enumerate(hub_list):
        hub_list[idx] = re.sub('<[^>]+>', '', val).strip()
            
    info_finder(input_class, yearsem)
            
    return hub_list
    

def section_finder(input_class: str, yearsem: str = 'future') -> list:
    """ returns a nested list with all the sections
        inputs: class code, year + semester
    """
    page_content = content_getter('section', input_class, yearsem)

    is_valid = page_content.find_all('div', class_="coursearch-course-container") 
    if "Course not found" in str(is_valid):
        return False


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


def hub_collector(filename, yearsem: str = 'future') -> dict:  
    with open(Path(__file__).parent / filename) as class_txt:
        class_txt = class_txt.read().splitlines()
        
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
        
        print('\nProgress: ')

        for i in class_txt:
            if in_data(i):
                class_data = pull_data(i)
                info = class_data['hub credit']
                        
            elif not i or i[0] == '#':
                continue
             
            else:
                info = hub_finder(i, yearsem)
                
            if info is None:
                continue
                        
            for j in info:
                try:
                    hub_dict[j][1] += 1
                except not KeyboardInterrupt:
                    if j == 'Scientific Inquiry II' or j == 'Social Inquiry II':
                        hub_dict['Scientific Inquiry II/Social Inquiry II'][1] += 1
            print(f'{i} done')

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


def print_all_hub() -> None:
    hub_dict = hub_collector('classes.txt')
    print('\nTotal Hub Credits: ')
    
    for hub in hub_dict:
        print(f'{hub}: {hub_dict[hub]}')

    return None



"""
Helper functions for the information grabbing section
"""

# Helper function for cleaner()
def filter_numerical(string: str) -> str:
    result = ''
    for char in string:
        if char in '1234567890':
            result += char
    return result


# For cleaning the information in the dictionary in info_finder()
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
     
     
# Helper function for content_getter(), cleans the user input
def clean_input(text: str) -> str:
    test = text.replace(' ', '')
    assert(len(test) == 8)
    
    clean = ''
    
    for i in test:
        clean += i
    
    return f'{clean[0:3]} {clean[3:5]} {clean[5:]}'.upper().split()





"""
JSON management functions
"""

def in_data(class_) -> bool:
    with open((Path(__file__).parent / 'data_file.json'), 'r') as data_file:
        try:
            data = json.load(data_file)
            return class_ in data
        
        except not KeyboardInterrupt:
            return False        
        
        
def write_data(new_data: dict[str, dict]) -> None:
    with open((Path(__file__).parent / 'data_file.json'), 'r') as data_file:
        try:
            old_data = json.load(data_file)
        except not KeyboardInterrupt:
            old_data = False
        
    with open((Path(__file__).parent / 'data_file.json'), 'w') as data_file:
        if old_data:
            new_data.update(old_data)
        data_file.seek(0)
        json.dump(new_data, data_file, indent = 4)
        
        
    return None


def pull_data(class_) -> dict:
    with open((Path(__file__).parent / 'data_file.json'), 'r') as data_file:
        data = json.load(data_file)
        
    return data[class_]


def pull_classes() -> list[str]:
    with open((Path(__file__).parent / 'data_file.json'), 'r') as data_file:
        data = json.load(data_file)
        
    return list(data.keys())


def update_data(data: dict[str, dict]) -> None:
    with open((Path(__file__).parent / 'data_file.json'), 'w') as data_file:
        json.dump(data, data_file, indent = 4)
        
    return None






"""
Terminal 'mode' based UI
"""

class ModeSelection:
    def __init__(self):
        self.hub_credits = None

    def mode_selection(self):
        while True:
            print('\nModes: \n')
            
            for idx, val in enumerate(['Course Info', 'Sections', 'Total Hub Credits', 'Show Hub Credits', \
                'Write to txt', 'Update Data', 'Exit']):
                
                print(f"{idx + 1}. {val}")
                            
            mode = input('\nSelect a mode: ').lower()
            
            if mode in ['1', 'course info']:
                self.mode_course_info()
            
            elif mode in ['2', 'sections']:
                self.mode_sections()
            
            elif mode in ['3', 'total hub credits']:
                self.mode_hub_credits()
            
            elif mode in ['4', 'show hub credits']:
                if not self.hub_credits:
                    print('No hub credits to show')
                    continue
                
                self.mode_show_hub_credits()
            
            elif mode in ['5', 'write to txt']:
                if not self.hub_credits:
                    print('No hub credits to write to txt')
                    continue
                
                self.mode_txt()
            
            elif mode in ['6', 'update data']:
                self.mode_update()
            
            elif mode in ['7', 'exit']:
                print('Exiting. . .')
                break
                
            else:
                print('Invalid input. Try again.')
            
        quit()
    
        
    def mode_course_info(self) -> None:
        course_yr = input('\nEnter course code and year/semester (e.g. cdsds210 2022 fall or cdsds210 future): ').split()
        
        start = perf_counter()
        
        if len(course_yr) == 1:
            course_yr.append('future')
        elif 'future' not in course_yr:
            course_yr = [course_yr[0],  f'{course_yr[1]} {course_yr[2]}']
            
        print(f'\nSearching: {course_yr[0]} for {course_yr[1]}\n')
        
        info = info_finder(course_yr[0], course_yr[1])
        
        print_info(info)
        
        stop = perf_counter()
        
        print(f"\nDone in: {stop - start:0.4f} seconds")
        
        return None


    def mode_sections(self) -> None:
        course_yr = input('\nEnter course code and year/semester (e.g. cdsds210 2022 fall or cdsds210 future): ').split()
        if len(course_yr) == 1:
            course_yr.append('future')
        if 'future' not in course_yr[1]:
            course_yr = [course_yr[0],  f'{course_yr[1]} {course_yr[2]}']
        print(f'\nSearching sections for {course_yr[0]} during {course_yr[1]}\n')
        
        sections = section_finder(course_yr[0], course_yr[1])
        
        if not sections:
            print('No sections found')
            return None
        
        print_section(sections)
        
        return None


    def mode_hub_credits(self) -> None:
        filename = input('\nEnter filename: ')
        if filename[-4:] != '.txt':
            filename += '.txt'
        
        start = perf_counter()
        self.hub_credits = hub_collector(filename)

        print('\nTotal Hub Credits: ')
        
        for hub in self.hub_credits:
            print(f'{hub}: {self.hub_credits[hub]}')
        
        stop = perf_counter()
        print(f"\nDone in: {stop - start:0.4f} seconds")

        return None


    def mode_show_hub_credits(self) -> None:
        print('\nTotal Hub Credits: ')
        
        for idx, hub in enumerate(self.hub_credits):
            if idx == 0:
                print(f'\n\nPhilosophical, Aesthetic, and Historical Interpretation\n')
                
            elif idx == 3:
                print(f'\n\nScientific and Social Inquiry\n')
                
            elif idx == 6:
                print(f'\n\nQuantitative Reasoning\n')
                    
            elif idx == 8:
                print('\n\nDiversity, Civic Engagement, and Global Citizenship\n')
                
            elif idx == 11:
                print('\n\nCommunication\n')
                
            elif idx == 16:
                print('\n\nIntellectual Toolkit\n')
                
            print(f'{hub}: {self.hub_credits[hub]}')
        
        return None


    def mode_txt(self) -> None:
        filename = input('\nEnter filename (no .txt): ')
        duplicate_count = 0
        
        while True:
            if duplicate_count == 0:
                full_filename = f'{filename}.txt'
                
            else:
                full_filename = f'{filename}({duplicate_count}).txt'
                
            if not Path(Path(__file__).parent / full_filename).is_file():
                
                with open(full_filename, 'w') as f:
                    f.write('Total Hub Credits:\n')
                    
                    for idx, hub in enumerate(self.hub_credits):
                        if idx == 0:
                            f.write(f'\nPhilosophical, Aesthetic, and Historical Interpretation\n')
                            
                        elif idx == 3:
                            f.write(f'\nScientific and Social Inquiry\n')
                            
                        elif idx == 6:
                            f.write(f'\nQuantitative Reasoning\n')
                                
                        elif idx == 8:
                            f.write('\nDiversity, Civic Engagement, and Global Citizenship\n')
                            
                        elif idx == 11:
                            f.write('\nCommunication\n')
                            
                        elif idx == 16:
                            f.write('\nIntellectual Toolkit\n')
                            
                        f.write(f'{hub}: {self.hub_credits[hub]}\n')
                break
            
            duplicate_count += 1
                
        return None


    def mode_update(self) -> None:
        
        start = perf_counter()
        
        with open((Path(__file__).parent / 'data_file.json'), 'r') as data_file:
            data = json.load(data_file)

        new_data = {}       
        for course in data.keys():
            new_data[course] = info_finder(course, 'future', True)
            print(f'Updated: {course}')
            
        update_data(new_data)
            
        stop = perf_counter()
        print(f"\nDone in: {stop - start:0.4f} seconds")
            
        return None






if __name__ == '__main__':
    temp = ModeSelection()
    temp.mode_selection()