import requests, json, copy
from python_rave.rave_encryption import RaveEncryption 
from python_rave.rave_exceptions import RaveError, IncompletePaymentDetailsError, AuthMethodNotSupportedError, TransactionVerificationError, ServerError

# All payment subclasses are encrypted classes
class Payment(RaveEncryption):
    """ This is the base class for all the payments """
    def __init__(self, publicKey, secretKey, encryptionKey, baseUrl, endpointMap=None):
        if (publicKey and encryptionKey):

            # Instantiating the encrytion library and creating encryption member object (protected)
            super(Payment, self).__init__(encryptionKey)
            
            # Setting public key and secret key (private)
            self.__publicKey = publicKey
            self.__secretKey = secretKey

            # Setting base url and endpoint map, important for payment functions (protected)
            self._baseUrl = baseUrl
            self._endpointMap = endpointMap
        
        else:
            raise ValueError("Please supply an accurate public key and/or encryption key.")

    # Retrieves secret key
    def _getSecretKey(self):
        """ This returns the secret key """
        return self.__secretKey
    # Retrieves public key
    def _getPublicKey(self):
        """ This returns the public key """
        return self.__publicKey

    # If parameters are complete, returns true. If not returns false with parameter missing
    def _checkIfParametersAreComplete(self, requiredParameters, paymentDetails):
        """ THis returns true/false depending on if the paymentDetails match the required parameters """
        for i in requiredParameters:
            if i not in paymentDetails:
                return False, i
        return True, None


    # This handles the transaction responses, defined by the implementing classes
    # Returns True if further action is required, false if it is not
    def _handleResponses(self, response, endpoint, request=None):
        """ This handles the responses from charge and validate calls.\n
             Parameters are:\n
            response (Requests response object) -- This is the response object from requests\n
            endpoint (string) -- This is the endpoint which we are handling\n
            request (dict) -- This is the request payload
        """
        pass

    # This can be altered by implementing classes but this is the default behaviour
    # Returns True and the data if successful
    def _handleVerify(self, response):
        """ This handles all responses from the verify call.\n
             Parameters include:\n
            response (dict) -- This is the response Http object returned from the verify call
         """

        # Checking if there was a server error during the call (in this case html is returned instead of json)
        try:
            responseJson = response.json()
        except:
            raise ServerError(response)

        # Check if the call returned something other than a 200
        if not response.ok:
            raise TransactionVerificationError(responseJson.get("message", "Your call failed with no message"))
        
        # Check if the chargecode is 00
        elif not (responseJson["data"].get("chargecode", None) == "00"):
            return False, responseJson["data"]
        
        else:
            return True, responseJson["data"]

    # Returns arguments to check for based on the authMethod (returns string), need to provide keywordMapping
    # Maps the suggested_auth to the keyword expected
    def getTypeOfArgsRequired(self, keywordMap, authMethod):
        """ This returns the type of arguments required on a response that includes suggested_auth. It is usually overridden by implementing classes.\n
             Parameters include:\n
            authMethod (dict) -- This is the action returned from the charge call\n

             Returns:\n
            pin -- This means that the updatePayload call requires a pin. Pin is passed as a string argument to updatePayload\n
            address -- This means that the updatePayload call requires an address dict. The dict must contain "billingzip", "billingcity", "billingaddress", "billingstate", "billingcountry".

        """
        # Checks if the auth method passed is included in keywordMapping i.e. if it is supported
        if not keywordMap.get(authMethod, None):
            raise AuthMethodNotSupportedError(authMethod)
        
        return keywordMap[authMethod]

    # Charge function (hasFailed is a flag that indicates there is a timeout), shouldReturnRequest indicates whether to send the request back to the _handleResponses function
    def charge(self, paymentDetails, requiredParameters, hasFailed=False, shouldReturnRequest=False):
        """ This is the base charge call. It is usually overridden by implementing classes.\n
             Parameters include:\n
            paymentDetails (dict) -- These are the parameters passed to the function for processing\n
            requiredParameters (list) -- These are the parameters required for the specific call\n
            hasFailed (boolean) -- This is a flag to determine if the attempt had previously failed due to a timeout\n
            shouldReturnRequest -- This determines whether a request is passed to _handleResponses\n
        """
        # Checking for required components
        
        areDetailsComplete, missingItem = self._checkIfParametersAreComplete(requiredParameters, paymentDetails)
        
        if areDetailsComplete:

            # Performing shallow copy of payment details to prevent tampering with original
            paymentDetails = copy.copy(paymentDetails)

            # Setting the endpoint. If the charge call had previously failed, we add 'use_polling=1' as recommended https://flutterwavedevelopers.readme.io/reference#handling-timeouts-via-api
            endpoint = self._baseUrl + self._endpointMap["charge"]
            
            # Adding PBFPubKey param to paymentDetails
            paymentDetails.update({"PBFPubKey":self.__publicKey})

            # Encrypting payment details (_encrypt is inherited from RaveEncryption)
            encryptedPaymentDetails = self._encrypt(json.dumps(paymentDetails))

            # Collating request headers
            headers = {
                'content-type': 'application/json',
            }
            
            # Collating the payload for the request
            payload = {
                "PBFPubKey": paymentDetails["PBFPubKey"],
                "client": encryptedPaymentDetails,
                "alg": "3DES-24"
            }
            response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
            
            if shouldReturnRequest:
                return self._handleResponses(response, endpoint, paymentDetails)
            else:
                return self._handleResponses(response, endpoint)
            
        else:
            raise IncompletePaymentDetailsError(missingItem, requiredParameters)

    def validate(self, flwRef, otp):
        """ This is the base validate call.\n
             Parameters include:\n
            flwRef (string) -- This is the flutterwave reference returned from a successful charge call. You can access this from action["flwRef"] returned from the charge call\n
            otp (string) -- This is the otp sent to the user \n
        """
        # Setting the endpoint and adding PBFPubKey param to paymentDetails
        endpoint = self._baseUrl + self._endpointMap["validate"]

        # Collating request headers
        headers = {
            'content-type': 'application/json',
        }
        
        payload = {
            "PBFPubKey": self.__publicKey,
            "transactionreference": flwRef, 
            "transaction_reference": flwRef,
            "otp": otp
        }
        response = requests.post(endpoint, headers = headers, data=json.dumps(payload))
        return self._handleResponses(response, endpoint)
        
    # Verify charge
    def verify(self, txRef):
        """ This is used to check the status of a transaction.\n
             Parameters include:\n
            txRef (string) -- This is the transaction reference that you passed to your charge call. If you didn't define a reference, you can access the auto-generated one from payload["txRef"] or action["txRef"] from the charge call\n
        """
        # Setting the endpoint and adding PBFPubKey param to paymentDetails
        endpoint = self._baseUrl + self._endpointMap["verify"]

        # Collating request headers
        headers = {
            'content-type': 'application/json',
        }

        # Payload for the request headers
        payload = {
            "txref": txRef,
            "SECKEY": self.__secretKey
        }

        response = requests.post(endpoint, headers=headers, data=json.dumps(payload))
        return self._handleVerify(response)


        


