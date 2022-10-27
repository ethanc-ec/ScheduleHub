import pytest
from sch_hub import info_finder, hub_finder, filter_numerical

class TestClass:
    # Finder tests
    def test_infofinder(self):
        t = info_finder('cdsds210', 'future', True)
        assert all([isinstance(t, dict), int(t['credit']) == 4, len(t) == 5])
        
    def test_hubfinder(self):
        t = hub_finder('cdsds210', 'future')
        assert all([isinstance(t, list), len(t) == 3, all(['it' in i for i in t])])
        
    def test_filter_numerical(self):
        t = filter_numerical('q1w2e3r4t5y6u7i8o9p0')
        assert all([int(t), len(t) == 10, t == '1234567890'])