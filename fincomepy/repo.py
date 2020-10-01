
class Repo(Bond):
    ## TO DO: add margin and haircut
    ## TO DO: consider the case that repo period cover coupon payment date
    ## TO DO: add a constructor with repo start date and repo end date input
    ## TO DO: add repo constructor wihout bond information
    def __init__(self, settlement, maturity, coupon_perc, price_perc, frequency, basis, 
                 bond_face_value, repo_period, repo_rate_perc):
        super().__init__(settlement, maturity, coupon_perc, price_perc, frequency, basis)
        self._repo_period = repo_period
        self._repo_rate_perc = repo_rate_perc
        self._face_value = bond_face_value
    
    def repo_start_payment(self, haircut=None):  ## TO DO: add margin and haircut
        self._repo_start_payment = self._face_value * FixedIncome.perc_to_regular(self._dirty_price_perc)
        return self._repo_start_payment
    
    def repo_end_payment(self):
        ## TO DO: change 360 to UK:365
        self._repo_interest = self._repo_start_payment * FixedIncome.perc_to_regular(self._repo_rate_perc) * self._repo_period / 360
        self._repo_end_payment = self._repo_start_payment + self._repo_interest 
        return self._repo_end_payment
    
    def repo_break_even(self):
        self._forward_date = self._settlement + timedelta(days=self._repo_period)
        forward_ai = FixedIncome.perc_to_regular(self.accrint(self._couppcd, self._coupncd, self._forward_date, self._coupon_perc)) * self._face_value
        forward_clean_price = (self._repo_end_payment - forward_ai) / self._face_value
        forward_clean_price_perc = FixedIncome.regular_to_perc(forward_clean_price)
        self._price_change = forward_clean_price_perc - self._clean_price_perc
        ## TO DO: change this, make get_yield as a function that take argument
        forward_DP_regular = self._repo_end_payment / self._face_value
        sol = root(lambda x: FixedIncome.perc_to_regular(self.price(x)) - forward_DP_regular, [0.01] )
        forward_yield_perc = sol.x[0]
        self._forward_yield_regular = FixedIncome.perc_to_regular(forward_yield_perc)
        return forward_yield_perc

repo_test = Repo(settlement=date(2020,7,15), maturity=date(2030,5,15), coupon_perc=0.625, 
                 price_perc=(99+30/32), frequency=2, basis=1, 
                 bond_face_value=100000000, repo_period=1, repo_rate_perc=0.145)
repo_test.get_yield()
print("accrued_interest: {}".format(repo_test._accrint))
print("Mac duration: {}".format(repo_test.get_mac_duration()))
print("Modified duration: {}".format(repo_test.get_mod_duration()))
print("DV01: {}".format(repo_test.get_DV01()))
print("Convexity: {}".format(repo_test.get_convexity()))
print("Repo period: {}".format(repo_test._repo_period))
print("Repo interest: {}".format(repo_test._repo_rate_perc))
print("Repo start payment: {}".format(repo_test.repo_start_payment()))
print("Repo end payment: {}".format(repo_test.repo_end_payment()))
print("----------------------")

repo_test = Repo(settlement=date(2020,7,16), maturity=date(2030,5,15), coupon_perc=0.625, 
                 price_perc=99.953125, frequency=2, basis=1, 
                 bond_face_value=100000000, repo_period=32, repo_rate_perc=0.145)
repo_test.get_yield()
print("accrued_interest: {}".format(repo_test._accrint))
print("Mac duration: {}".format(repo_test.get_mac_duration()))
print("Modified duration: {}".format(repo_test.get_mod_duration()))
print("DV01: {}".format(repo_test.get_DV01()))
print("Convexity: {}".format(repo_test.get_convexity()))
print("Repo period: {}".format(repo_test._repo_period))
print("Repo interest: {}".format(repo_test._repo_rate_perc))
print("Repo start payment: {}".format(repo_test.repo_start_payment()))
print("Repo end payment: {}".format(repo_test.repo_end_payment()))
print("Repo break even yield: {}".format(repo_test.repo_break_even()))
print("----------------------")

