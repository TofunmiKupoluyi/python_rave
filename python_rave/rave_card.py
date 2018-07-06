from python_rave.rave_exceptions import RaveError, IncompletePaymentDetailsError, CardChargeError, TransactionVerificationError, ServerError
from python_rave.rave_payment import Payment
from python_rave.rave_misc import generateTransactionReference

class Card(Payment):
    """ This is the rave object for card transactions. It contains the following public functions:\n
        .charge -- This is for making a card charge\n
        .validate -- This is called if further action is required i.e. OTP validation\n
        .verify -- This checks the status of your transaction\n
    """
    def __init__(self, publicKey, secretKey, encryptionKey, baseUrl):
        super(Card, self).__init__(publicKey, secretKey, encryptionKey, baseUrl)


    # returns true if further action is required, false if it isn't    
    def _handleChargeResponse(self, response, txRef, request=None):
        """ This handles charge responses """
        try:
            responseJson = response.json()
            flwRef = responseJson["data"].get("flwRef", None)

        except:
            raise ServerError({"error": True, "txRef": txRef, "flwRef": None, "errMsg": response})

        if not response.ok:
            # If response code is not a 200
            errMsg = responseJson["data"].get("message", None)
            raise CardChargeError({"error": True, "txRef": txRef, "flwRef": flwRef, "errMsg": errMsg})
        
        # If all preliminary checks passed
        if not (responseJson["data"].get("chargeResponseCode", None) == "00"):
            # Otherwise we return that further action is required, along with the response
            suggestedAuth = responseJson["data"].get("suggested_auth", None)
            return {"error": False,  "validationRequired": True, "txRef": txRef, "flwRef": flwRef, "suggestedAuth": suggestedAuth}
        else:
            return {"error": False,  "validationRequired": False, "txRef": txRef, "flwRef": flwRef, "suggestedAuth": None}

    

    # This can be altered by implementing classes but this is the default behaviour
    # Returns True and the data if successful
    def _handleVerifyResponse(self, response, txRef):
        """ This handles all responses from the verify call.\n
             Parameters include:\n
            response (dict) -- This is the response Http object returned from the verify call
         """

        # Checking if there was a server error during the call (in this case html is returned instead of json)
        try:
            responseJson = response.json()
            flwRef = responseJson["data"].get("flwRef", None)
            # Weird response returned from API call so we have to deal with this specially
            if not flwRef:
                flwRef = responseJson["data"].get("flwref", None)
        except:
            raise ServerError({"error": True, "txRef": txRef, "flwRef": None, "errMsg": response})

        # Check if the call returned something other than a 200
        if not response.ok:
            errMsg = responseJson["data"].get("message", "Your call failed with no response")
            raise TransactionVerificationError({"error": True, "txRef": txRef, "flwRef": flwRef, "errMsg": errMsg})
        
        # if the chargecode is not 00
        elif not (responseJson["data"].get("chargecode", None) == "00"):
            return {"error": False, "transactionComplete": False, "txRef": txRef, "flwRef":flwRef, "cardToken": responseJson["data"]["card"]["card_tokens"][0]["embedtoken"]}
        
        else:
            return {"error":False, "transactionComplete": True, "txRef": txRef, "flwRef": flwRef, "cardToken": responseJson["data"]["card"]["card_tokens"][0]["embedtoken"]}

    
    # Charge card function
    def charge(self, cardDetails, hasFailed=False):
        """ This is called to initiate the charge process.\n
             Parameters include:\n
            cardDetails (dict) -- This is a dictionary comprising payload parameters.\n
            hasFailed (bool) -- This indicates whether the request had previously failed for timeout handling
        """

        # setting the endpoint
        endpoint = self._baseUrl + self._endpointMap["card"]["charge"]
        if not ("txRef" in cardDetails):
            cardDetails.update({"txRef":generateTransactionReference()})
        # Checking for required card components
        requiredParameters = ["cardno", "cvv", "expirymonth", "expiryyear", "amount", "email", "phonenumber", "firstname", "lastname", "IP"]
        
        return super(Card, self).charge(cardDetails, requiredParameters, endpoint)
    

    def validate(self, flwRef, otp):
        endpoint = self._baseUrl + self._endpointMap["card"]["validate"]
        return super(Card, self).validate(flwRef, otp, endpoint)

    def verify(self, txRef):
        endpoint = self._baseUrl + self._endpointMap["card"]["verify"]
        return super(Card, self).verify(txRef, endpoint)



        


