import get_info as gi



def mode_selection():
    
    while True:
        print('\nModes: \n')
        
        for idx, val in enumerate(['Course Info', 'Sections', 'Total Hub Credits', 'Show Hub Credits', 'Exit']):
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
        
        elif mode in ['5', 'exit']:
            mode_exit()
            
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
            
    hubs = gi.hub_collector(filename)

    print('\nTotal Hub Credits: ')
    
    for hub in hubs:
        print(f'{hub}: {hubs[hub]}')
    
    return None


def mode_show_hub_credits():
    print('\nTotal Hub Credits: ')
    
    for idx, hub in enumerate(gi.hub_dict):
        if idx == 0:
            print(f'\nPhilosophical, Aesthetic, and Historical Interpretation')
            
        elif idx == 3:
            print(f'\nScientific and Social Inquiry')
            
        elif idx == 6:
            print(f'\nQuantitative Reasoning')
                
        elif idx == 8:
            print('\nDiversity, Civic Engagement, and Global Citizenship')
            
        elif idx == 11:
            print('\nCommunication')
            
        elif idx == 16:
            print('\nIntellectual Toolkit')
            
        print(f'{hub}: {gi.hub_dict[hub]}')
    
    return None


def mode_exit():
    print('Exiting. . .')
    return quit()
        
        
        
if __name__ == '__main__':
    mode_selection()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        