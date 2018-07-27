import requests
from python_rave.rave_exceptions import ServerError, TransactionVerificationError, PreauthCaptureError, PreauthRefundVoidError
from python_rave.rave_card import Card
from python_rave.rave_misc import generateTransactionReference

class Preauth(Card):
    """ This is the rave object for preauthorized transactions. It contains the following public functions:\n
        .charge -- This is for making a ussd charge\n
        .validate -- This is called if further action is required i.e. OTP validation\n
        .verify -- This checks the status of your transaction\n
    """

    def __init__(self, publicKey, secretKey, production, usingEnv):
        super(Preauth, self).__init__(publicKey, secretKey, production, usingEnv)

    # Initiate preauth
    def charge(self, cardDetails, chargeWithToken=False, hasFailed=False):
        """ This is called to initiate the preauth process.\n
             Parameters include:\n
            cardDetails (dict) -- This is a dictionary comprising payload parameters.\n
            hasFailed (bool) -- This indicates whether the request had previously failed for timeout handling
        """

        # Add the charge_type
        cardDetails.update({"charge_type":"preauth"})
        return super(Preauth, self).charge(cardDetails, chargeWithToken)
    
    # capture payment
    def capture(self, flwRef):
        """ This is called to complete the transaction.\n
             Parameters include:
            flwRef (string) -- This is the flutterwave reference you receive from action["flwRef"]
        """
        payload = {
            "SECKEY": self._getSecretKey(),
            "flwRef": flwRef
        }
        headers ={
            "Content-Type":"application/json"
        }
        endpoint = self._baseUrl + self._endpointMap["capture"]
        response = requests.post(endpoint, headers=headers, data=payload)
        self._handleChargeResponse(response, flwRef)
    

    def void(self, flwRef):
        """ This is called to void a transaction.\n 
             Parameters include:\n
            flwRef (string) -- This is the flutterwave reference you receive from action["flwRef"]\n
        """
        payload = {
            "SECKEY": self._getSecretKey(),
            "flwRef": flwRef,
            "action":"void"
        }
        headers ={
            "Content-Type":"application/json"
        }
        endpoint = self._baseUrl + self._endpointMap["refundorvoid"]
        response = requests.post(endpoint, headers=headers, data=payload)
        self._handleChargeResponse(response, endpoint)
    
    
    def refund(self, flwRef, amount=None):
        """ This is called to refund the transaction.\n
             Parameters include:\n
            flwRef (string) -- This is the flutterwave reference you receive from action["flwRef"]\n
            amount (Number) -- (optional) This is called if you want a partial refund
        """
        payload = {
            "SECKEY": self._getSecretKey(),
            "flwRef": flwRef,
            "action":"refund"
        }
        if amount:
            payload.update({"amount", amount})

        headers ={
            "Content-Type":"application/json"
        }
        endpoint = self._baseUrl + self._endpointMap["refundorvoid"]
        response = requests.post(endpoint, headers=headers, data=payload)
        self._handleChargeResponse(response, endpoint)
