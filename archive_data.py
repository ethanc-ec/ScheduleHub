import json
from pathlib import Path
from types import NoneType



def in_data(class_) -> bool:
    with open((Path(__file__).parent / 'data_file.json'), 'r') as data_file:
        try:
            data = json.load(data_file)
            return class_ in data
        
        except:
            return False        
        
        
def write_data(new_data: dict[str, dict]) -> NoneType:
    with open((Path(__file__).parent / 'data_file.json'), 'r') as data_file:
        try:
            old_data = json.load(data_file)
        except:
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

def update_data(data: dict[str, dict]) -> bool:
    with open((Path(__file__).parent / 'data_file.json'), 'w') as data_file:
        json.dump(data, data_file, indent = 4)
        
    return None