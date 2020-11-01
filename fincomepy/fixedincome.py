import numpy as np

class FixedIncome(object):
    '''
    A class used to represent general fixed income products. Used as a base class for other 
    classes to inherit from.

    Attributes
    ----------
    _reg_dict : dict
        A dictionary which contains the regular quantities. The keys of _reg_dict should be the
        same as that of _perc_dict
    _perc_dict : dict
        A dictionary which contains the quantities in percent. The keys of _perc_dict should be the
        same as that of _reg_dict

    Methods
    -------
    update_dict()
        Update both _reg_dict and _perc_dict.
    '''
    
    def __init__(self):
        self._reg_dict = {}
        self._perc_dict = {}
    
    def update_dict(self):
        '''
        Update both _reg_dict and _perc_dict.

        This function updates _reg_dict and _perc_dict by making them have the same keys. The values
        in both dictionaries are updated such that for each key, the value in _reg_dict is equal to 
        0.01 times the value in _perc_dict. 
        '''
        # update keys and values in _reg_dict
        for key, value in self._reg_dict.items():
            if key not in self._perc_dict.keys():
                self._perc_dict[key] = value * 100
        
        # update keys and values in _perc_dict
        for key, value in self._perc_dict.items():
            if key not in self._reg_dict.keys():
                self._reg_dict[key] = value * 0.01
        
        # make sure the values in two dictionaries matches
        for key, value in self._perc_dict.items():
            if isinstance(value, np.ndarray):
                assert (self._reg_dict[key] == value * 0.01).all()
            else:
                assert self._reg_dict[key] == value * 0.01

