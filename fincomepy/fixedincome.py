

class FixedIncome(object):
    def __init__(self):
        pass
    
    @staticmethod
    def perc_to_regular(percentage_values):
        return percentage_values*0.01

    @staticmethod
    def regular_to_perc(regular_values):
        return regular_values*100