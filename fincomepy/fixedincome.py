

class FixedIncome(object):
    def __init__(self):
        pass
    
    def update_dict(self):
        for key, value in self._reg_dict.items():
            if key not in self._perc_dict.keys():
                self._perc_dict[key] = value * 100
        
        for key, value in self._perc_dict.items():
            if key not in self._reg_dict.keys():
                self._reg_dict[key] = value * 0.01
