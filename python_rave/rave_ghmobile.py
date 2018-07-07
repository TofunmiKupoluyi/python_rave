from python_rave.rave_payment import Payment
from python_rave.rave_misc import generateTransactionReference
import json

class GhMobile(Payment):
    
    def __init__(self, publicKey, secretKey, encryptionKey, baseUrl):
        super(GhMobile, self).__init__(publicKey, secretKey, encryptionKey, baseUrl)


    # Charge mobile money function
    def charge(self, accountDetails, hasFailed=False):
        """ This is the ghMobile charge call.
             Parameters include:\n
            accountDetails (dict) -- These are the parameters passed to the function for processing\n
            hasFailed (boolean) -- This is a flag to determine if the attempt had previously failed due to a timeout\n
        """

        endpoint = self._baseUrl + self._endpointMap["account"]["charge"]
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
        return super(GhMobile, self).charge(accountDetails, requiredParameters, endpoint)

