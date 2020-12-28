import numpy as np
from fincomepy.fixedincome import FixedIncome

class CDS(FixedIncome):
    '''
    A class used to perform credit default swap (CDS) related calculations.

    Attributes
    ----------
    _reg_dict : dict
        A dictionary which contains the regular quantities. The keys of _reg_dict should be the
        same as that of _perc_dict.
    _perc_dict : dict
        A dictionary which contains the quantities in percent. The keys of _perc_dict should be the
        same as that of _reg_dict.
    _maturity: np.array
        A numpy array which contains the maturity of bonds (in years). 
    _cds_spread: np.array
        A numpy array which contains the CDS spread (in percent) of each year.

    Methods
    -------
    cds_spread()
        Calculate CDS spread.
    '''
    
    def __init__(self, risk_free_perc, risky_perc, face_value_perc=100, rr_perc=50, maturity=None):
        '''
        Constructor for CDS.

        Parameters
        ----------
        risk_free_perc: np.array
            A numpy array which contains the risk free rates (in percent) of bond.
        risky_perc: np.array
            A numpy array which contains the risky rates (in percent) of bond.
        face_value_perc: float
            A float which contains the face value (in percent) of bond.
        rr_perc: float
            A float which contains the recovery rate when calculating CDS.
        maturity: np.array, optional
            A numpy array which contains the maturity of bonds (in years). 

        Examples
        --------
        >>> cds_test = CDS(risk_free_perc=np.array([3.12]*10), risky_perc=np.array([3.72]*10), 
            face_value_perc=100, rr_perc=40)
        '''
        super().__init__()
        assert risk_free_perc.size == risky_perc.size
        assert rr_perc >= 0 and rr_perc <= 100
        self._perc_dict["risk_free"] = risk_free_perc
        self._perc_dict["risky"] = risky_perc
        self._perc_dict["face_value"] = face_value_perc
        self._perc_dict["rr"] = rr_perc
        if maturity is None:
            self._maturity = np.arange(self._perc_dict["risk_free"].size) + 1
        else:
            self._maturity = maturity
        self.update_dict()
        self._cds_spread = None
    
    @classmethod
    def from_bond_spread(cls, risk_free_perc, spread_perc, face_value_perc=100, rr_perc=50, maturity=None):
        '''
        Constructor for CDS.

        Parameters
        ----------
        risk_free_perc: np.array
            A numpy array which contains the risk free rates (in percent) of bond.
        spread_perc: np.array
            A numpy array which contains the bond spread (in percent).
        face_value_perc: float
            A float which contains the face value (in percent) of bond.
        rr_perc: float
            A float which contains the recovery rate when calculating CDS.
        maturity: np.array, optional
            A numpy array which contains the maturity of bonds (in years). 

        Examples
        --------
        >>> cds_test = CDS.from_bond_spread(risk_free_perc=np.array([3.12]*10), 
            spread_perc=np.array([0.6]*10), face_value_perc=100, rr_perc=40)
        '''
        assert risk_free_perc.size == spread_perc.size
        risky_perc = risk_free_perc + spread_perc
        return cls(risk_free_perc, risky_perc, face_value_perc, rr_perc, maturity)
    
    def cds_spread(self):
        '''Calculate CDS spread.

        Returns
        -------
        np.array
            A numpy array which contains the CDS spread (in percent) of each year.

        Examples
        --------
        >>> cds_test = CDS(risk_free_perc=np.array([3.12]*10), risky_perc=np.array([3.72]*10), 
            face_value_perc=100, rr_perc=40)
        >>> cds_test.cds_spread()
        array([0.57848052, 0.57848052, 0.57848052, 0.57848052, 0.57848052,
               0.57848052, 0.57848052, 0.57848052, 0.57848052, 0.57848052])
        '''
        if self._cds_spread is not None:
            return self._cds_spread
        df_risk_free = []
        df_risky = []
        df_risk_free.append(self._reg_dict["face_value"] / (self._reg_dict["face_value"] + self._reg_dict["risk_free"][0]))
        df_risky.append(self._reg_dict["face_value"] / (self._reg_dict["face_value"] + self._reg_dict["risky"][0]))
        for i in range(1, self._reg_dict["risk_free"].size):
            df1 = (self._reg_dict["face_value"] - self._reg_dict["risk_free"][i] * sum(df_risk_free)) / \
                (self._reg_dict["face_value"] + self._reg_dict["risk_free"][i])
            df2 = (self._reg_dict["face_value"] - self._reg_dict["risky"][i] * sum(df_risky)) / \
                (self._reg_dict["face_value"] + self._reg_dict["risky"][i])
            df_risk_free.append(df1)
            df_risky.append(df2)
        df_risk_free = np.array(df_risk_free)
        df_risky = np.array(df_risky)
        df_risk_free_shift = np.insert(df_risk_free[:-1], 0, 1.0)
        df_risky_shift = np.insert(df_risky[:-1], 0, 1.0)
        # expected_loss = 1.0 - df_risky / df_risk_free
        hazard_rates = (1.0 - (df_risky / df_risky_shift) / (df_risk_free / df_risk_free_shift)) / (1.0 - self._reg_dict["rr"])
        period_survival = 1.0 - hazard_rates
        survival_prob = period_survival.cumprod()
        survival_prob_shift = np.insert(survival_prob[:-1], 0, 1.0)
        temp1 = survival_prob_shift * hazard_rates * df_risk_free
        temp2 = survival_prob * df_risk_free
        cds_spread_reg = []
        for i in range(1, self._reg_dict["risk_free"].size + 1):
            s = (1.0 - self._reg_dict["rr"]) * temp1[:i].sum() / (temp1[:i].sum() + temp2[:i].sum())
            cds_spread_reg.append(s)
        self._cds_spread = np.array(cds_spread_reg) * 100
        return self._cds_spread


