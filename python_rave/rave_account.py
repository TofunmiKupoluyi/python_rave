from python_rave.rave_exceptions import RaveError, IncompletePaymentDetailsError, AccountChargeError, TransactionVerificationError, TransactionValidationError, ServerError

from python_rave.rave_payment import Payment
from python_rave.rave_misc import generateTransactionReference
import json

class Account(Payment):
    """ This is the rave object for account transactions. It contains the following public functions:\n
        .charge -- This is for making an account charge\n
        .validate -- This is called if further action is required i.e. OTP validation\n
        .verify -- This checks the status of your transaction\n
    """
    def __init__(self, publicKey, secretKey, encryptionKey, baseUrl, endpointMap=None):
            super(Account, self).__init__(publicKey, secretKey, encryptionKey, baseUrl, endpointMap)


    def _handleChargeResponse(self, response, request=None):
        """ This handles account charge responses """
        # This checks if we can parse the json successfully
        try:
            responseJson = response.json()
        except:
            raise ServerError(response)

        # If it is not returning a 200
        if not response.ok:
            raise AccountChargeError(responseJson["message"])
        
        # If all preliminary checks are passed
        if not (responseJson["data"].get("chargeResponseCode", None) == "00"):
            # If contains authurl
            if not (responseJson["data"].get("authurl", "NO-URL") == "NO-URL"):
                return True, responseJson["data"], responseJson["data"]["authurl"]
            # If it doesn't
            else:
                return True, responseJson["data"], None

        else:
            return False, responseJson["data"], None
    

    def _handleValidateResponse(self, response, request=None):
        """ This handles account validate responses """

        try:
            responseJson = response.json()
        except:
            raise ServerError(response)

        if not response.ok:
            raise TransactionValidationError(responseJson["message"])
        
        # If all preliminary checks passed
        if not (responseJson["data"].get("chargeResponseCode", None) == "00"):
            raise TransactionValidationError(responseJson["data"]["chargeResponseMessage"])
        else:
            return False, responseJson["data"]


    # Returns True if further action is required, false if it is not
    def _handleResponses(self, response, endpoint, request = None):
        if(endpoint == self._baseUrl+ self._endpointMap["charge"]):
            return self._handleChargeResponse(response)
        elif(endpoint == self._baseUrl + self._endpointMap["validate"]):
            return self._handleValidateResponse(response)


    # Charge account function
    def charge(self, accountDetails, hasFailed=False):
        """ This is the ghMobile charge call.\n
             Parameters include:\n
            accountDetails (dict) -- These are the parameters passed to the function for processing\n
            hasFailed (boolean) -- This is a flag to determine if the attempt had previously failed due to a timeout\n
        """
        # If payment type is not defined or not set to account
        if not ("payment_type" in accountDetails) or not (accountDetails["payment_type"]== "account"):
            accountDetails.update({"payment_type": "account"})
        if not ("txRef" in accountDetails):
            accountDetails.update({"txRef": generateTransactionReference()})
        # Checking for required account components
        requiredParameters = ["accountbank", "accountnumber", "amount", "email", "phonenumber", "IP"]
        return super(Account, self).charge(accountDetails, requiredParameters)
