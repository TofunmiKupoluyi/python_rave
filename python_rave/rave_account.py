from python_rave.rave_exceptions import RaveError, IncompletePaymentDetailsError, AccountChargeError, TransactionVerificationError, TransactionValidationError, ServerError

from python_rave.rave_payment import Payment
from python_rave.rave_misc import generateTransactionReference
import json

class Account(Payment):
    """ This is the rave object for account transactions. It contains the following public functions:\n
        .charge -- This is for making a ussd charge\n
        .validate -- This is called if further action is required i.e. OTP validation\n
        .verify -- This checks the status of your transaction\n
    """
    def __init__(self, publicKey, secretKey, encryptionKey, baseUrl, endpointMap=None):
            super(Account, self).__init__(publicKey, secretKey, encryptionKey, baseUrl, endpointMap)

    
    # Returns True if further action is required, false if it is not
    def _handleResponses(self, response, endpoint, request = None):
        """ This handles the responses from charge and validate calls.
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
            # If we are handling a charge call
            if endpoint == (self._baseUrl + self._endpointMap["charge"]):
                raise AccountChargeError(responseJson["message"])

            # If we are handling a validate call
            elif endpoint == (self._baseUrl + self._endpointMap["validate"]):
                raise TransactionValidationError(responseJson["message"])

            else:
                raise RaveError("Unknown error type")

        elif responseJson["status"] == "success":
            # Charge response code of 00 means successful, 02 means failed. Here we check if the code is not 00
            if not (responseJson["data"].get("chargeResponseCode", None) == "00"):
                # If it is not successful (00) after a validation attempt on bank account, we raise error
                if endpoint == (self._baseUrl + self._endpointMap["validate"]):
                    # Used chargeResponseMessage
                    raise TransactionValidationError(responseJson["data"]["chargeResponseMessage"])
                # Otherwise we return that further action is required, along with the response
                return True, responseJson["data"]

            # If a charge is successful, we return that further action is not required, along with the response
            else:
                return False, responseJson["data"]


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
