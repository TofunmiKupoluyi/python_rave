import requests
from python_rave.rave_exceptions import RaveError, IncompletePaymentDetailsError, TransactionVerificationError, TransactionValidationError, ServerError, PreauthInitializationError, PreauthCaptureError
from python_rave.rave_payment import Payment
from python_rave.rave_misc import generateTransactionReference
class Preauth(Payment):
    """ This is the rave object for preauthorized transactions. It contains the following public functions:\n
        .charge -- This is for making a ussd charge\n
        .validate -- This is called if further action is required i.e. OTP validation\n
        .verify -- This checks the status of your transaction\n
    """

    def __init__(self, publicKey, secretKey, encryptionKey, baseUrl, endpointMap=None):
        super(Preauth, self).__init__(publicKey, secretKey, encryptionKey, baseUrl, endpointMap)

    
    # Returns True if further is required, false if it is not
    def _handleResponses(self, response, endpoint, request=None):
        """ This handles the responses from charge and validate calls. Parameters are:\n
            response (Requests response object) -- This is the response object from requests\n
            endpoint (string) -- This is the endpoint which we are handling\n
            request (dict) -- This is the request payload
        """
         # This checks if we can parse the json successfully
        try:
            responseJson = response.json()
        except:
            raise ServerError(response)

        # If response status is error, we raise an exception
        # Checks what the endpoint is and models error raised accordingly
        if not response.ok:
            # If we are handling a charge call
            if endpoint == (self._baseUrl + self._endpointMap["charge"]):
                raise PreauthInitializationError(responseJson["message"])
            
            # If we are handling a validate call
            elif endpoint == (self._baseUrl + self._endpointMap["validate"]):
                raise TransactionValidationError(responseJson["message"])
            
            elif endpoint == (self._baseUrl + self._endpointMap["capture"]):
                raise PreauthCaptureError(responseJson["message"])

            else:
                raise RaveError("Unknown error type")

        elif responseJson["status"] == "success":
            # If it is not successful after a validation attempt on bank account, we raise error -- has to be separate because the validate endpoint is strange
            if endpoint == (self._baseUrl + self._endpointMap["validate"]):
                if not (responseJson["data"]["tx"].get("chargeResponseCode", None) == "00"):
                    # This is the error we raise, we get it from charge response message
                    raise TransactionValidationError(responseJson["data"]["tx"]["chargeResponseMessage"])
                else:
                    return False, responseJson["data"]["tx"]

            # Charge response code of 00 means successful, 02 means failed. Here we check if the code is not 00
            if not (responseJson["data"].get("chargeResponseCode", None) == "00"):
                # Otherwise we return that further action is required, along with the response
                return True, responseJson["data"], responseJson["data"].get("suggested_auth", None)
            else:
                return False, responseJson["data"]


    # Initiate preauth
    def preauth(self, cardDetails, hasFailed=False):
        """ This is called to initiate the preauth process.\n
             Parameters include:\n
            cardDetails (dict) -- This is a dictionary comprising payload parameters.\n
            hasFailed (bool) -- This indicates whether the request had previously failed for timeout handling
        """

        if not ("txRef" in cardDetails):
            cardDetails.update({"txRef":generateTransactionReference()})
        if not("charge_type" in cardDetails) or not (cardDetails["charge_type"] == "preauth"):
            cardDetails.update({"charge_type":"preauth"})
        # Checking for required card components
        requiredParameters = ["cardno", "cvv", "expirymonth", "expiryyear", "amount", "email", "phonenumber", "firstname", "lastname", "IP"]
        return super(Preauth, self).charge(cardDetails, requiredParameters)
    
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
        self._handleResponses(response, endpoint)
    
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
        self._handleResponses(response, endpoint)
    
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
        self._handleResponses(response, endpoint)

    def getTypeOfArgsRequired(self, authMethod):
        """ This is used to get the type of argument needed to complete your charge call.\n
             Parameters include:\n
            authMethod (dict) -- This is the action returned from the charge call\n

             Returns:\n
            pin -- This means that the updatePayload call requires a pin. Pin is passed as a string argument to updatePayload\n
            address -- This means that the updatePayload call requires an address dict. The dict must contain "billingzip", "billingcity", "billingaddress", "billingstate", "billingcountry".
        """

        keywordMap = {"PIN":"pin", "AVS_VBVSECURECODE":"address", "NOAUTH_INTERNATIONAL":"address"}
        return super(Preauth, self).getTypeOfArgsRequired(keywordMap, authMethod)

    # Update payload
    def updatePayload(self, authMethod, payload, **kwargs):
        """ This is used to update the payload of your request upon a charge that requires more parameters. It maintains the transaction refs and all the original parameters of the request.\n
             Parameters include:
            authMethod (dict) -- This is what is returned from the charge call\n
            payload (dict) -- This is the original payload\n
            \n
            ## This updates payload directly
        """ 
        # Check if the authMethod was passed correctly
        if authMethod and payload:
            # Sets the keyword to check for in kwargs (it maps the authMethod to keywords)
            keyword = self.getTypeOfArgsRequired(authMethod)

            # Checks

            # 1) Checks if keyword is present in kwargs
            if not kwargs.get(keyword, None):
                # Had to split variable assignment and raising ValueError because of error message python displayed
                errorMsg = "Please provide the appropriate argument for the auth method. For {}, we require a \"{}\" argument.".format(authMethod["suggested_auth"], keyword)
                raise ValueError(errorMsg)

            # 2) If keyword is address, checks if all required address paramaters are present
            if keyword == "address":
                requiredAddressParameters = ["billingzip", "billingcity", "billingaddress", "billingstate", "billingcountry"]
                areDetailsComplete, missingItem  = self._checkIfParametersAreComplete(requiredAddressParameters, kwargs[keyword])
                if not areDetailsComplete:
                    raise IncompletePaymentDetailsError(missingItem, requiredAddressParameters)
                
            # All checks passed

            # Add items to payload
            # If the argument is a dictionary, we add the argument as is
            if isinstance(kwargs[keyword], dict):
                payload.update(kwargs[keyword])

            # If it's not we add it manually
            else:
                payload.update({"suggested_auth":authMethod})
                payload.update({keyword: kwargs[keyword]})
                
        else:
            raise ValueError("Please provide action object (object with suggested_auth key) as the first positional argument and payload (old card details) as the second positional error")

        


