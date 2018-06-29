from python_rave.rave_base import RaveBase
from python_rave.rave_card import Card
from python_rave.rave_account import Account
from python_rave.rave_ussd import Ussd
from python_rave.rave_ghmobile import GhMobile
from python_rave.rave_mpesa import Mpesa
from python_rave.rave_preauth import Preauth

class Rave(RaveBase):
    
    def __init__(self, publicKey=None, secretKey=None, production=False, usingEnv=True):
        """ This is main organizing object. It contains the following:\n
            rave.Card -- For card transactions\n
            rave.Preauth -- For preauthorized transactions\n
            rave.Account -- For bank account transactions\n
            rave.Ussd -- For ussd transactions\n
            rave.GhMobile -- For Ghana mobile money transactions\n
            rave.Mpesa -- For mpesa transactions\n
        """
        # If public key is not passed
        if not publicKey:
            raise ValueError("Please provide a publicKey as a parameter.")
        
        # If public key is passed and we're using environment variable for secret key
        elif usingEnv:
            super(Rave, self).__init__(publicKey, production=production)
       
        # If public key is passed and we're not using environment variables for secret key
        else:
            super(Rave, self).__init__(publicKey, secretKey, production=production, usingEnv=usingEnv)
        
        # Creating member objects already initiated with the publicKey and secretKey
        self.Card = Card(publicKey, secretKey, self._encryptionKey, self._baseUrl, self._endpointMap["card"])
        self.Preauth = Preauth(publicKey, secretKey, self._encryptionKey, self._baseUrl, self._endpointMap["card"])
        # These all use the account endpoint till further changes, the enpoint maps are defined in rave_base
        self.Account = Account(publicKey, secretKey, self._encryptionKey, self._baseUrl, self._endpointMap["account"])
        self.Ussd = Ussd(publicKey, secretKey, self._encryptionKey, self._baseUrl, self._endpointMap["account"])
        self.GhMobile = GhMobile(publicKey, secretKey, self._encryptionKey, self._baseUrl, self._endpointMap["account"])
        self.Mpesa = Mpesa(publicKey, secretKey, self._encryptionKey, self._baseUrl, self._endpointMap["account"])
        
