from python_rave.rave_exceptions import RaveError, IncompletePaymentDetailsError,   MpesaChargeError, TransactionVerificationError, TransactionValidationError, ServerError

from python_rave.rave_payment import Payment
from python_rave.rave_misc import generateTransactionReference
import json

class Mpesa(Payment):
    
    def __init__(self, publicKey, secretKey, encryptionKey, baseUrl, endpointMap=None):
            super(Mpesa, self).__init__(publicKey, secretKey, encryptionKey, baseUrl, endpointMap)

    
    # Returns True if further action is required, false if it is not
    def _handleResponses(self, response, endpoint, request = None):
        """ This handles the responses from charge and validate calls.\n
             Parameters include:\n
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
                raise MpesaChargeError(responseJson["message"])

        elif responseJson["status"] == "success":
            # Charge response code of 00 means successful, 02 means failed. Here we check if the code is not 00
            if not (responseJson["data"].get("chargeResponseCode", None) == "00"):
                # Otherwise we return that further action is required, along with the response
                return True, responseJson["data"]
            # If a charge is successful, we return that further action is not required, along with the response
            else:
                return False, responseJson["data"]


    # Charge mobile money function
    def charge(self, accountDetails, hasFailed=False):
        """ This is the mpesa charge call.\n
             Parameters include:\n
            accountDetails (dict) -- These are the parameters passed to the function for processing\n
            hasFailed (boolean) -- This is a flag to determine if the attempt had previously failed due to a timeout\n
        """
        # If payment type is not defined or not set to mpesa
        if not ("payment_type" in accountDetails) or not (accountDetails["payment_type"]== "mpesa"):
            accountDetails.update({"payment_type": "mpesa"})
        # If country is not set or it is not kenya
        if not ("country" in accountDetails) or not (accountDetails["country"] == "KE"):
            accountDetails.update({"country":"KE"})
        # If they have not already set the is_mpesa param
        if not ("is_mpesa" in accountDetails) or not(accountDetails["is_mpesa"] == "1"):
            accountDetails.update({"is_mpesa":"1"})
        # If currency is not set or it isn't KES
        if not ("currency" in accountDetails) or not (accountDetails["currency"] == "KES"):
            accountDetails.update({"currency":"KES"})
        # If transaction reference is not set 
        if not ("txRef" in accountDetails):
            accountDetails.update({"txRef": generateTransactionReference()})
        # If order reference is not set
        if not ("orderRef" in accountDetails):
            accountDetails.update({"orderRef": generateTransactionReference()})

        # Checking for required account components
        requiredParameters = ["amount", "email", "phonenumber", "IP"]
        return super(Mpesa, self).charge(accountDetails, requiredParameters)
