import pytest
from src.schhub.sch_hub import info_finder, hub_finder, filter_numerical, clean_input

class TestClass:
    # Finder tests
    @pytest.mark.parametrize("test_input,expected", [
            (['cdsds210', 'future'], True), 
            (['cdsds100', 'future'], True)
        ])
    def test_infofinder(self, test_input, expected):
        t = info_finder(test_input[0], test_input[1], True)
        assert all([isinstance(t, dict), len(t) == 5, 'prereq' in t]) == expected
    
    
    @pytest.mark.parametrize("test_input,expected", [
            (['cdsds210', 'future'], True), 
            (['cdsds100', 'future'], True)
        ]) 
    def test_hubfinder(self, test_input, expected):
        t = hub_finder(test_input[0], test_input[1])
        assert all([isinstance(t, list), len(t) >= 1]) == expected
        
        
    def test_filter_numerical(self):
        t = filter_numerical('q1w2e3r4t5y6u7i8o9p0')
        assert all([int(t), len(t) == 10, t == '1234567890'])
        
        
    @pytest.mark.parametrize("test_input,expected", [
        ('c d s ds 1  2 0  ', ['CDS', 'DS', '120']), 
        ('cds  ds   100', ['CDS', 'DS', '100'])
    ])
    def test_cleaninput(self, test_input, expected):
        t = clean_input(test_input)
        assert all([isinstance(t, list), t == expected, int(t[2])])