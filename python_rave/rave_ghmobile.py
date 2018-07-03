from python_rave.rave_exceptions import RaveError, IncompletePaymentDetailsError,   GhMobileChargeError, TransactionVerificationError, TransactionValidationError, ServerError

from python_rave.rave_payment import Payment
from python_rave.rave_misc import generateTransactionReference
import json

class GhMobile(Payment):
    
    def __init__(self, publicKey, secretKey, encryptionKey, baseUrl, endpointMap=None):
            super(GhMobile, self).__init__(publicKey, secretKey, encryptionKey, baseUrl, endpointMap)

    
    def _handleChargeResponse(self, response, request = None):
        """ This handles ghmobile charge transactions """
        # If we cannot parse the json, it means there is a server error
        try:
            responseJson = response.json()
        except:
            raise ServerError(response)

        # If it is not returning a 200
        if not response.ok:
            raise GhMobileChargeError(responseJson["message"])
        
        # if all preliminary tests pass
        if not (responseJson["data"].get("chargeResponseCode", None) == "00"):
            return True, responseJson["data"]
        else:
            return False, responseJson["data"]


    # Returns True if further action is required, false if it is not
    def _handleResponses(self, response, endpoint, request = None):
        if endpoint == self._baseUrl + self._endpointMap["charge"]:
            return self._handleChargeResponse(response)


    # Charge mobile money function
    def charge(self, accountDetails, hasFailed=False):
        """ This is the ghMobile charge call.
             Parameters include:\n
            accountDetails (dict) -- These are the parameters passed to the function for processing\n
            hasFailed (boolean) -- This is a flag to determine if the attempt had previously failed due to a timeout\n
        """
        # If payment type is not defined or not set to mobile money
        if not ("payment_type" in accountDetails) or not (accountDetails["payment_type"]== "mobilemoneygh"):
            accountDetails.update({"payment_type": "mobilemoneygh"})
        # If country is not set or it is not ghana
        if not ("country" in accountDetails) or not (accountDetails["country"] == "GH"):
            accountDetails.update({"country":"GH"})
        # If they have not already set the is_mobile_money_gh param
        if not ("is_mobile_money_gh" in accountDetails) or not(accountDetails["is_mobile_money_gh"] == "1"):
            accountDetails.update({"is_mobile_money_gh":"1"})
        # If currency is not set or it isn't GHS
        if not ("currency" in accountDetails) or not (accountDetails["currency"] == "GHS"):
            accountDetails.update({"currency":"GHS"})
        # If transaction reference is not set 
        if not ("txRef" in accountDetails):
            accountDetails.update({"txRef": generateTransactionReference()})
        # If order reference is not set
        if not ("orderRef" in accountDetails):
            accountDetails.update({"orderRef": generateTransactionReference()})

        # Checking for required account components
        requiredParameters = ["amount", "email", "phonenumber", "network", "IP", "redirect_url"]
        return super(GhMobile, self).charge(accountDetails, requiredParameters)
