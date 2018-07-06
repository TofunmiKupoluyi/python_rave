from python_rave.rave_base import RaveBase
from python_rave.rave_card import Card
from python_rave.rave_account import Account
from python_rave.rave_ussd import Ussd
from python_rave.rave_ghmobile import GhMobile
from python_rave.rave_mpesa import Mpesa
from python_rave.rave_preauth import Preauth

class Rave:
    
    def __init__(self, publicKey, secretKey, production=False, usingEnv=True):
        """ This is main organizing object. It contains the following:\n
            rave.Card -- For card transactions\n
            rave.Preauth -- For preauthorized transactions\n
            rave.Account -- For bank account transactions\n
            rave.Ussd -- For ussd transactions\n
            rave.GhMobile -- For Ghana mobile money transactions\n
            rave.Mpesa -- For mpesa transactions\n
        """
        
        # Creating member objects already initiated with the publicKey and secretKey
        self.Card = Card(publicKey, secretKey, production, usingEnv)
        self.Preauth = Preauth(publicKey, secretKey, production, usingEnv)
        # These all use the account endpoint till further changes, the enpoint maps are defined in rave_base
        self.Account = Account(publicKey, secretKey, production, usingEnv)
        self.Ussd = Ussd(publicKey, secretKey, production, usingEnv)
        self.GhMobile = GhMobile(publicKey, secretKey, production, usingEnv)
        self.Mpesa = Mpesa(publicKey, secretKey, production, usingEnv)
        
