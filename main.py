import get_info as gi



def mode_selection():
    
    while True:
        print('\nModes: \n')
        
        for idx, val in enumerate(['Course Info', 'Sections', 'Total Hub Credits', 'Exit']):
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
        
        elif mode in ['4', 'exit']:
            mode_exit()
            
        else:
            print('Invalid input. Try again.')
        
    
def mode_course_info() -> None:
    course_yr = input('\nEnter course code and year/semester (e.g. cdsds210 2022 fall or cdsds210 future): ').split()
    
    if 'future' not in course_yr[1]:
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
    yrsem = input('Enter year/semester (e.g. 2022 fall): ')
    
    hubs = gi.hub_collector(filename, yrsem)
    len_hubs = len(hubs)
    print('\nTotal Hub Credits: ')
    
    for idx, val in enumerate(hubs):
        print(f'{val}: {hubs[val]}')
    
    return None


def mode_exit():
    print('Exiting. . .')
    return quit()
        
        
        
if __name__ == '__main__':
    mode_selection()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        