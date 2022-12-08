import re
import json
import requests

from tqdm import tqdm
from pathlib import Path
from bs4 import BeautifulSoup

from time import perf_counter

from functools import lru_cache
from multiprocessing import Pool
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

"""
Functions for scraping the information from the website
Can also grab from 'data_file.json'
"""


def content_getter(finder: str, input_class: str, yearsem: str = 'future', sess: requests.Session = False) -> BeautifulSoup:
    """ returns the content of the page as a BeautifulSoup object
        inputs: finder, class code, year + semester
    """
    code = clean_input(input_class)

    if yearsem.lower() == 'future':
        time = '*'

    else:
        split_year = yearsem.upper().split(' ')
        time = split_year[0] + '-' + split_year[1]

    if finder == 'info':
        URL = "https://www.bu.edu/phpbin/course-search/search.php?page=w0&pagesize=10&adv=1&nolog=&search_adv_all=" \
            + f"{code[0]}+{code[1]}+{code[2]}&yearsem_adv={time}&credits=*&pathway=&hub_match=all&pagesize=10"

    elif finder == 'section':
        code_joined = ''.join(code).lower()
        URL = f"https://www.bu.edu/phpbin/course-search/section/?t={code_joined}&semester={time}&return=%2Fphpbin" \
            + f"%2Fcourse-search%2Fsearch.php%3Fpage%3Dw0%26pagesize%3D10%26adv%3D1%26nolog%3D%26search_adv_all%3D{code[0]}%2B{code[1]}%2B{code[2]}" \
            + f"%26yearsem_adv%3D{time}%26credits%3D%2A%26pathway%3D%26hub_match%3Dall"

    if sess:
        page = sess.get(URL)
    else:
        page = requests.get(URL)

    content = BeautifulSoup(page.content, 'html.parser')

    return content


def info_finder(input_class: str, yearsem: str, skip: str = False, sess: requests.Session = False) -> dict:
    if in_data(input_class) and not skip:
        class_data = pull_data(input_class)
        return class_data

    page_content = content_getter('info', input_class, yearsem, sess)
    results = page_content.find(id="body-tag")

    # For finding the hub credits
    hub = results.find('ul', class_="coursearch-result-hub-list")

    hub_list = str(hub).split('<li>')[1:]

    for idx, val in enumerate(hub_list):
        hub_list[idx] = re.sub('<[^>]+>', '', val).strip()

    if hub_list:
        if 'pathway' in hub_list[-1].lower():
            hub_list[-1] = hub_list[-1].split('BU')[0]

    # For finding the prereq, coreq, description and credit
    full = results.find('div', class_="coursearch-result-content-description")

    if full is None:
        return False

    # Gets: [prereq, coreq,description, numerical credit]
    full_list = full.text.splitlines()

    full_dict = {
        'prereq': full_list[1],
        'coreq': full_list[3],
        'description': full_list[5],
        'credit': full_list[6],
        'hub credit': hub_list[:]
    }

    cleaned = cleaner(full_dict)

    data_writing = {
        input_class: cleaned
    }

    if not skip:
        merge_data(data_writing)

    return cleaned


def hub_finder(input_class: str, yearsem: str = 'future') -> list:
    page_content = content_getter('info', input_class, yearsem)
    results = page_content.find(id="body-tag")

    # For finding the hub credits
    hub = results.find('ul', class_="coursearch-result-hub-list")

    hub_list = str(hub).split('<li>')[1:]

    for idx, val in enumerate(hub_list):
        hub_list[idx] = re.sub('<[^>]+>', '', val).strip()

    if hub_list:
        if 'pathway' in hub_list[-1].lower():
            hub_list[-1] = hub_list[-1].split('BU')[0]

    return hub_list


def section_finder(input_class: str, yearsem: str = 'future') -> list:
    """ returns a nested list with all the sections
        inputs: class code, year + semester
    """
    try:
        page_content = content_getter('section', input_class, yearsem)
    except AssertionError:
        return None

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


@lru_cache
def hub_collector(filename: str) -> dict:
    with open((Path(__file__).parent.parent / f'data/{filename}')) as class_txt:
        class_txt = class_txt.read().splitlines()

    hub_dict = {
        "Philosophical Inquiry and Life's Meanings": [1, 0],
        "Aesthetic Exploration": [1, 0],
        "Historical Consciousness": [1, 0],

        "Scientific Inquiry I": [1, 0],
        "Social Inquiry I": [1, 0],
        "Scientific Inquiry II/Social Inquiry II": [1, 0],

        "Quantitative Reasoning I": [1, 0],
        "Quantitative Reasoning II": [1, 0],

        "The Individual in Community": [1, 0],
        "Global Citizenship and Intercultural Literacy": [2, 0],
        "Ethical Reasoning": [1, 0],

        "First-Year Writing Seminar": [1, 0],
        "Writing, Research, and Inquiry": [1, 0],
        "Writing-Intensive Course": [2, 0],
        "Oral and/or Signed Communication": [1, 0],
        "Digital/Multimedia Expression": [1, 0],

        "Critical Thinking": [2, 0],
        "Research and Information Literacy": [2, 0],
        "Teamwork/Collaboration": [2, 0],
        "Creativity/Innovation": [2, 0]
    }

    class_txt = [i for i in class_txt if '#' not in i]

    print('\nCollecting hub credits...')

    with ThreadPoolExecutor() as executor:
        info = list(tqdm(executor.map(hc_assistant, class_txt), total=len(class_txt), desc='Hub Info Progress', ncols=100))

    for val in info:
        if not val:
            continue
        for credit in val:
            if credit == 'Scientific Inquiry II' or credit == 'Social Inquiry II':
                hub_dict['Scientific Inquiry II/Social Inquiry II'][1] += 1
            else:
                hub_dict[credit][1] += 1

    return hub_dict


def hc_assistant(class_code: str) -> dict:
    if in_data(class_code):
        class_data = pull_data(class_code)
        info = class_data['hub credit']

    elif not class_code or class_code == '#':
        return False

    else:
        info = hub_finder(class_code, 'future')

    if info is None:
        return False

    return info


def print_info(info_dict: dict) -> None:
    for key in info_dict:
        if key != 'description':
            print(f'{key}(s): {info_dict[key]} \n')
        else:
            print(f'{key}: {info_dict[key]} \n')

    return None


def print_section(section_list: list) -> None:
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
def clean_input(text: str) -> list:
    test = text.replace(' ', '')
    assert (len(test) == 8)

    clean = ''

    for i in test:
        clean += i

    return f'{clean[0:3]} {clean[3:5]} {clean[5:]}'.upper().split()


"""
JSON management functions
"""


def in_data(class_: str) -> bool:
    try:
        with open((Path(__file__).parent.parent / 'data/data_file.json'), 'r') as data_file:
            data = json.load(data_file)
            return class_ in data

    except FileNotFoundError:
        return False


def merge_data(new_data: dict) -> None:
    """ returns None
        inputs: a dictionary with class name as key and a dictionary of class info as value
    """
    try:
        with open((Path(__file__).parent.parent / 'data/data_file.json'), 'r') as data_file:
            old_data = json.load(data_file)

    except FileNotFoundError:
        old_data = False

    with open((Path(__file__).parent.parent / 'data/data_file.json'), 'w') as data_file:
        if old_data:
            new_data.update(old_data)
        data_file.seek(0)
        json.dump(new_data, data_file, indent=4)

    return None


def pull_data(class_: str) -> dict:
    with open((Path(__file__).parent.parent / 'data/data_file.json'), 'r') as data_file:
        data = json.load(data_file)

    return data[class_]


def pull_classes() -> list:
    """ returns all classes in list[str]
        inputs: None
    """
    with open((Path(__file__).parent.parent / 'data/data_file.json'), 'r') as data_file:
        data = json.load(data_file)

    return list(data.keys())


def dump_data(data: dict) -> None:
    """ returns None
        inputs: a dictionary with class name as key and a dictionary of class info as value
    """
    with open((Path(__file__).parent.parent / 'data/data_file.json'), 'w') as data_file:
        json.dump(data, data_file, indent=4)

    return None


@lru_cache()
def update_data() -> None:
    classes = pull_classes()

    with open((Path(__file__).parent.parent / 'data/data_file.json'), 'r') as data_file:
        json_file = json.load(data_file)

    executor = ProcessPoolExecutor()
    info_list = list(tqdm(executor.map(ud_assistant, classes), total=len(classes), desc='Update Progress', ncols=100))

    for _, val in enumerate(info_list):
        json_file[val[0]] = val[1]

    with open((Path(__file__).parent.parent / 'data/data_file.json'), 'w') as data_file:
        json.dump(json_file, data_file, indent=4)

    return None


def ud_assistant(class_code: str) -> tuple:
    return [class_code, info_finder(class_code, 'future', True)]


"""
Terminal 'mode' based UI
"""


class ModeSelection:
    def __init__(self):
        self.hub_credits = None
        self.sess = None

    def show_commands(self):
        selection_dict = {
            '-c': 'Course Info',
            '-s': 'Sections',
            '-t': 'Total Hub Credits',
            '-sh': 'Show Hub Credits',
            '-w': 'Write to txt',
            '-u': 'Update Data',
            '-g': 'Grab Data',
            '-h': 'Help',
            '-e': 'Exit'
        }

        print('\nCommands:')

        for id in selection_dict:
            print(f"{id}: {selection_dict[id]}")

    def mode_selection(self):
        self.show_commands()
        while True:
            mode = input('\n>')

            if '-h' in mode:
                print('Not implemented yet')

            elif '-c' in mode:
                self.mode_course_info(mode.split()[1:])

            elif '-s' in mode and '-sh' not in mode:
                self.mode_sections()

            elif '-t' in mode:
                self.mode_hub_credits()

            elif '-sh' in mode:
                if not self.hub_credits:
                    print('No hub credits to show')
                    continue

                self.mode_show_hub_credits()

            elif '-w' in mode:
                if not self.hub_credits:
                    print('No hub credits to write to txt')
                    continue

                self.mode_txt()

            elif '-u' in mode:
                self.mode_update()

            elif '-g' in mode:
                self.mode_grab()

            elif '-e' in mode:
                print('Exiting. . .')
                break

            else:
                print('Invalid input. Try again.')

        quit()

    def mode_course_info(self, course_yr) -> None:
        start = perf_counter()

        if len(course_yr) == 1:
            course_yr.append('future')
        elif 'future' not in course_yr:
            course_yr = [course_yr[0],  f'{course_yr[1]} {course_yr[2]}']

        print(f'\nSearching: {course_yr[0]} for {course_yr[1]}\n')

        info = info_finder(course_yr[0], course_yr[1])

        if not info:
            print('No info found')
        else:
            print_info(info)

        stop = perf_counter()

        print(f"Done in: {stop - start:0.4f} seconds")

        return None

    def mode_sections(self) -> None:
        course_code = input('\nEnter course code and year/semester (e.g. cdsds210 2022 fall or cdsds210 future): ').split()

        start = perf_counter()

        if len(course_code) == 1:
            course_code.append('future')
        if 'future' not in course_code[1]:
            if 'spring' in course_code[2].lower():
                course_code[2] = 'SPRG'
            course_code = [course_code[0],  f'{course_code[1]} {course_code[2]}']

        print(f'\nSearching sections for {course_code[0]} during {course_code[1]}\n')

        sections = section_finder(course_code[0], course_code[1])

        if sections is False:
            print('No sections found')
            return None
        elif sections is None:
            print('Invalid input')
            return None

        print_section(sections)
        print(f'Done in {perf_counter() - start:0.4f} seconds')

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
                print('\n\nPhilosophical, Aesthetic, and Historical Interpretation\n')

            elif idx == 3:
                print('\n\nScientific and Social Inquiry\n')

            elif idx == 6:
                print('\n\nQuantitative Reasoning\n')

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
                            f.write('\nPhilosophical, Aesthetic, and Historical Interpretation\n')

                        elif idx == 3:
                            f.write('\nScientific and Social Inquiry\n')

                        elif idx == 6:
                            f.write('\nQuantitative Reasoning\n')

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
        print('\nUpdating data. . .')
        start = perf_counter()
        update_data()
        end = perf_counter()
        print(f'\nUpdated in: {end - start:0.4f} seconds')

        return None

    @lru_cache()
    def mode_grab(self) -> None:

        cl_start = perf_counter()
        bu_branches = {
            'cas': 'College of Arts and Sciences',
            'khc': 'Kilachand Honors College',
            'com': 'College of Communication',
            'eng': 'College of Engineering',
            'cfa': 'College of Fine Arts',
            'cgs': 'College of General Studies',
            'sar': 'College of Health & Rehabilitation Sciences: Sargent College',
            'cds': 'Faculty of Computing & Data Sciences',
            'qst': 'Questrom School of Business',
        }
        print('\nAvailable branches: ')
        for i in bu_branches:
            print(f'{i},', end=' ')

        bselect = input('\nEnter college code, use a "," to separate multiple, or use "all" (e.g. cds): ')
        if ',' in bselect:
            bselect = bselect.split(',')
            bselect = [i.strip() for i in bselect]
        elif 'all' in bselect:
            bselect = [i for i in bu_branches]
        else:
            bselect = [bselect]

        with ThreadPoolExecutor() as executor:
            class_list = list(tqdm(executor.map(self.mgrab_assistant_group, bselect), total=len(bselect), desc='Group Search Progress', ncols=100))

        class_list = [item for sublist in class_list for item in sublist]

        cl_stop = perf_counter()
        print(f'\n{len(class_list)} groups found in {cl_stop - cl_start:0.4f} seconds\n')

        search_start = perf_counter()

        new_data = {}

        self.sess = requests.Session()
        with Pool() as p:
            data_list = list(tqdm(p.imap_unordered(self.mgrab_assistant_grab, class_list), total=len(class_list), desc='Class Search Progress', ncols=100))

        while False in data_list:
            data_list.remove(False)

        for i in data_list:
            new_data[i[0]] = i[1]

        merge_data(new_data)

        search_stop = perf_counter()
        print(f"\nDone in: {search_stop - search_start:0.4f} seconds")

        return None

    @lru_cache()
    def mgrab_assistant_group(self, branch):
        sess = requests.Session()
        base = 'https://www.bu.edu/academics/{branch}/courses/'

        whole_branch = []
        for i in range(150):
            page = sess.get(base + f'{i}')
            content = BeautifulSoup(page.content, 'html.parser')

            results = content.find('ul', class_='course-feed')
            if results is None or len(str(results.prettify())) == 31:
                break

            group = []
            for content in results:
                a = content.next_sibling
                if a is None or not len(a.text.strip()):
                    continue
                else:
                    class_code = a.text.split(':')[0].strip().replace(' ', '').lower()
                    group.append(class_code)

            for i in group:
                whole_branch.append(i)
        return whole_branch

    def mgrab_assistant_grab(self, course):
        temp = info_finder(course, 'future', True, self.sess)
        if not temp:
            return False
        return [course, temp]


if __name__ == '__main__':
    temp = ModeSelection()
    temp.mode_selection()
