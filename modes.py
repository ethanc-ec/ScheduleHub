import time
import get_info as gi
from pathlib import Path



def mode_selection():
    
    while True:
        print('\nModes: \n')
        
        for idx, val in enumerate(['Course Info', 'Sections', 'Total Hub Credits', 'Show Hub Credits', 'Write to txt', 'Exit']):
            print(f"{idx + 1}. {val}")
                        
        mode = input('\nSelect a mode: ').lower()
        
        if mode in ['1', 'course info']:
            mode_course_info()
            continue
        
        elif mode in ['2', 'sections']:
            mode_sections()
            continue
        
        elif mode in ['3', 'total hub credits']:
            mode_hub_credits()
            continue
        
        elif mode in ['4', 'show hub credits']:
            mode_show_hub_credits()
            continue
        
        elif mode in ['5', 'write to txt']:
            mode_txt()
            continue
        
        elif mode in ['6', 'exit']:
            print('Exiting. . .')
            quit()
            
        else:
            print('Invalid input. Try again.')
        
    
def mode_course_info() -> None:
    course_yr = input('\nEnter course code and year/semester (e.g. cdsds210 2022 fall or cdsds210 future): ').split()
    
    if len(course_yr) == 1:
        course_yr.append('future')
    elif 'future' not in course_yr:
        course_yr = [course_yr[0],  f'{course_yr[1]} {course_yr[2]}']
        
    print(f'\nSearching: {course_yr[0]} for {course_yr[1]}\n')
    
    info = gi.info_finder(course_yr[0], course_yr[1])
    
    gi.print_info(info)
    
    return None


def mode_sections() -> None:
    course_yr = input('\nEnter course code and year/semester (e.g. cdsds210 2022 fall or cdsds210 future): ').split()
    
    if 'future' not in course_yr[1]:
        course_yr = [course_yr[0],  f'{course_yr[1]} {course_yr[2]}']
    print(f'\nSearching sections for {course_yr[0]} during {course_yr[1]}\n')
    
    sections = gi.section_finder(course_yr[0], course_yr[1])
    
    gi.print_section(sections)
    
    return None


def mode_hub_credits() -> None:
    filename = input('\nEnter filename: ')
    if filename[-4:] != '.txt':
        filename += '.txt'
    
    start = time.perf_counter()
    hubs = gi.hub_collector(filename)

    print('\nTotal Hub Credits: ')
    
    for hub in hubs:
        print(f'{hub}: {hubs[hub]}')
    
    stop = time.perf_counter()
    print(f"\nDone in: {stop - start:0.4f} seconds")

    return None


def mode_show_hub_credits():
    print('\nTotal Hub Credits: ')
    
    for idx, hub in enumerate(gi.hub_dict):
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
            
        print(f'{hub}: {gi.hub_dict[hub]}')
    
    return None


def mode_txt():
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
                
                for idx, hub in enumerate(gi.hub_dict):
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
                        
                    f.write(f'{hub}: {gi.hub_dict[hub]}\n')
            break
        
        duplicate_count += 1
            
    return None
        
        
if __name__ == '__main__':
    mode_selection()     