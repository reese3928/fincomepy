import numpy as np

class FixedIncome(object):
    def __init__(self):
        self._reg_dict = {}
        self._perc_dict = {}
    
    def update_dict(self):
        for key, value in self._reg_dict.items():
            if key not in self._perc_dict.keys():
                self._perc_dict[key] = value * 100
        
        for key, value in self._perc_dict.items():
            if key not in self._reg_dict.keys():
                self._reg_dict[key] = value * 0.01
        
        for key, value in self._perc_dict.items():
            if isinstance(value, np.ndarray):
                assert (self._reg_dict[key] == value * 0.01).all()
            else:
                assert self._reg_dict[key] == value * 0.01

