import numpy as np
from scipy.optimize import root
import matplotlib.pyplot as plt
from fincomepy.fixedincome import FixedIncome

class ZspreadZero(FixedIncome):
    '''
    A class used to calculate z-spread from zero-coupon bonds.

    Attributes
    ----------
    _reg_dict : dict
        A dictionary which contains the regular quantities. The keys of _reg_dict should be the
        same as that of _perc_dict.
    _perc_dict : dict
        A dictionary which contains the quantities in percent. The keys of _perc_dict should be the
        same as that of _reg_dict.
    _maturity: np.array
        A numpy array which contains the maturity of each zero-coupon bonds (in years). 

    Methods
    -------
    get_zspread(*args, **kwargs)
        Calculate and return z-spread.
    plot_zspread(maturity=None, zero_rates_perc=None, zspread=None)
        Visualize z-spread by plotting zero-coupon rates and bond pricing rates.
    total_CF_zspread(zspread, zero_rates_regular, CF_regular, maturity)
        Calculate the total cash flow.
    '''

    def __init__(self, zero_rates_perc, CF_perc, face_value_perc=100, maturity=None):
        """Constructor for ZspreadZero.

        Parameters
        ----------
        zero_rates_perc : np.array
            Zero-coupon rates (in percent).
        CF_perc : np.array
            Cash flow of bond (in percent).
        face_value_perc : float
            The face value of bond (in percent).
        maturity : np.array, optional
            A numpy array which contains the maturity of each zero-coupon bonds (in years).
            Default is None.
        
        Examples
        --------
        >>> zero_discrete = np.array([1.0, 1.5038, 1.8085, 2.0652, 2.2199])
        >>> coupon_cf = np.array([3.0, 3.0, 3.0, 3.0, 103.0])
        >>> zspr_test1 = ZspreadZero(zero_discrete, coupon_cf)  
        """
        super().__init__()
        self._perc_dict["zero_rates"] = zero_rates_perc
        self._perc_dict["CF"] = CF_perc
        self._perc_dict["face_value"] = face_value_perc
        if maturity is None:
            self._maturity = np.arange(self._perc_dict["zero_rates"].size) + 1
        else:
            self._maturity = maturity
        self.update_dict()
    
    @property
    def zspread(self):
        if "zspread" in self._perc_dict.keys():
            return self._perc_dict["zspread"]
        return self.get_zspread()

    def get_zspread(self, *args, **kwargs):
        """Calculate and return z-spread.

        Parameters
        ----------
        *args : optional
            Positional argument passed to scipy.optimize.root.
        **kwargs : optional
            Keyword argument passed to scipy.optimize.root. 
        
        Returns
        -------
        float
            The calculated z-spread (in percent).
        
        Examples
        --------
        >>> zero_discrete = np.array([1.0, 1.5038, 1.8085, 2.0652, 2.2199])
        >>> coupon_cf = np.array([3.0, 3.0, 3.0, 3.0, 103.0])
        >>> zspr_test1 = ZspreadZero(zero_discrete, coupon_cf) 
        >>> zspr_test1.get_zspread()
        0.8071473072171145
        """
        sol = root(lambda x: self.total_CF_zspread(x, self._reg_dict["zero_rates"], self._reg_dict["CF"], 
                   self._maturity) - self._reg_dict["face_value"], [0.01], *args, **kwargs)
        zspread = sol.x[0]
        assert zspread >= 0 and zspread <=1
        self._reg_dict["zspread"] = zspread
        self.update_dict()
        return self._perc_dict["zspread"]

    def plot_zspread(self, maturity=None, zero_rates_perc=None, zspread_perc=None):
        '''
        Visualize z-spread by plotting zero-coupon rates and bond pricing rates.

        Parameters
        ----------
        maturity : np.array, optional
            A numpy array which contains the maturity of each zero-coupon bonds (in years).
            Default is None.
        zero_rates_perc : np.array, optional
            Zero-coupon rates (in percent). Default is None.
        zspread_perc : float, optional
            User-supplied z-spread (in percent). Default is None.
        
        Examples
        --------
        >>> zero_discrete = np.array([1.0, 1.5038, 1.8085, 2.0652, 2.2199])
        >>> coupon_cf = np.array([3.0, 3.0, 3.0, 3.0, 103.0])
        >>> zspr_test1 = ZspreadZero(zero_discrete, coupon_cf) 
        >>> zspr_test1.get_zspread()
        >>> zspr_test1.plot_zspread()
        '''
        if maturity is None:
            maturity = self._maturity
        if zero_rates_perc is None:
            zero_rates_perc = self._perc_dict["zero_rates"]
        if not zspread_perc:
            zspread_perc = self.zspread
        plt.plot(maturity, zero_rates_perc, label="Zero-Coupon Rates")
        plt.plot(maturity, zspread_perc + zero_rates_perc, label="Bond Pricing Rates")
        plt.xticks(maturity)
        plt.xlabel("Maturity")
        plt.ylabel(r"Rates(%)")
        plt.grid(linewidth=0.5)
        plt.legend()
    
    @staticmethod
    def total_CF_zspread(zspread, zero_rates_regular, CF_regular, maturity):
        '''Calculate the total cash flow.'''
        CF_each_period = CF_regular/ (1 + zero_rates_regular + zspread) ** maturity
        return np.sum(CF_each_period)


class ZspreadPar(ZspreadZero):
    '''
    A class used to calculate z-spread from par-coupon bonds.

    Attributes
    ----------
    _reg_dict : dict
        A dictionary which contains the regular quantities. The keys of _reg_dict should be the
        same as that of _perc_dict.
    _perc_dict : dict
        A dictionary which contains the quantities in percent. The keys of _perc_dict should be the
        same as that of _reg_dict.
    _compound : str
        A string that is either "discrete" or "continuous". It specifies whether discrete or continuous
        zero coupon rate will be used.
    _maturity: np.array
        A numpy array which contains the maturity of each zero-coupon bonds (in years). 

    Methods
    -------
    get_zspread(*args, **kwargs)
        Calculate and return z-spread.
    plot_zspread(maturity=None, zero_rates_perc=None, zspread=None)
        Visualize z-spread by plotting zero-coupon rates and bond pricing rates.
    '''

    def __init__(self, par_rates_perc, CF_perc, face_value_perc=100, compound="discrete", maturity=None):
        '''Constructor for ZspreadPar.

        Parameters
        ----------
        par_rates_perc : np.array
            Par-coupon rates (in percent).
        CF_perc : np.array
            Cash flow of bond (in percent).
        face_value_perc : float
            The face value of bond (in percent).
        compound : str
            A string that is either "discrete" or "continuous". It specifies whether discrete or continuous
            zero coupon rate will be used. Default is "discrete". 
        maturity : np.array, optional
            A numpy array which contains the maturity of each zero-coupon bonds (in years).
            Default is None.
        
        Examples
        --------
        >>> coupon_cf = np.array([3.0, 3.0, 3.0, 3.0, 103.0])
        >>> par_rates = np.array([1.00, 1.50, 1.80, 2.05, 2.20])
        >>> zspr_test2 = ZspreadPar(par_rates, coupon_cf)
        '''
        FixedIncome.__init__(self)
        self._perc_dict["par_rates"] = par_rates_perc
        self._perc_dict["CF"] = CF_perc
        self._perc_dict["face_value"] = face_value_perc
        if compound not in ["discrete", "continuous"]:
            raise Exception(r"compound should be either 'discrete' or 'continuous' ")
        self._compound = compound
        if maturity is None:
            self._maturity = np.arange(self._perc_dict["par_rates"].size) + 1
        else:
            self._maturity = maturity
        self._discount_factor = None
        self.update_dict()
    
    @property
    def zspread(self):
        if "zspread" in self._perc_dict.keys():
            return self._perc_dict["zspread"]
        return self.get_zspread()
    
    def get_zspread(self, *args, **kwargs):
        """Calculate and return z-spread.

        Parameters
        ----------
        *args : optional
            Positional argument passed to scipy.optimize.root.
        **kwargs : optional
            Keyword argument passed to scipy.optimize.root. 
        
        Returns
        -------
        float
            The calculated z-spread (in percent).
        
        Examples
        --------
        >>> coupon_cf = np.array([3.0, 3.0, 3.0, 3.0, 103.0])
        >>> par_rates = np.array([1.00, 1.50, 1.80, 2.05, 2.20])
        >>> zspr_test2 = ZspreadPar(par_rates, coupon_cf)
        >>> zspr_test2.get_zspread()
        0.8071642537725563
        """
        # calculate discount factors
        discount_factor = []
        discount_factor.append(self._reg_dict["face_value"] / (self._reg_dict["face_value"] + self._reg_dict["par_rates"][0]))
        for i in range(1, self._reg_dict["par_rates"].size):
            df = (self._reg_dict["face_value"] - self._reg_dict["par_rates"][i] * sum(discount_factor)) / \
                 (self._reg_dict["face_value"] + self._reg_dict["par_rates"][i])
            discount_factor.append(df)
        discount_factor = np.array(discount_factor)
        self._discount_factor = discount_factor
        # convert discount factors into discrete or continuous zero coupon rates
        if self._compound == "discrete":
            self._reg_dict["zero_rates"] = (1 / discount_factor) ** (1 / self._maturity) - 1
        else:
            self._reg_dict["zero_rates"] = -np.log(discount_factor) / self._maturity
        # obtain zspread by calling get_zspread function in the parent class
        super().get_zspread(*args, **kwargs)
        return self._perc_dict["zspread"]


