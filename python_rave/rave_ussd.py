from python_rave.rave_exceptions import RaveError, IncompletePaymentDetailsError, UssdChargeError, TransactionVerificationError, TransactionValidationError, ServerError

from python_rave.rave_payment import Payment
from python_rave.rave_misc import generateTransactionReference
import json

class Ussd(Payment):
    def __init__(self, publicKey, secretKey, encryptionKey, baseUrl, endpointMap=None):
        """ This is the rave object for ussd transactions. It contains the following public functions:\n
        .charge -- This is for making a ussd charge\n
        .verify -- This checks the status of your transaction\n
        """
        super(Ussd, self).__init__(publicKey, secretKey, encryptionKey, baseUrl, endpointMap)

    def _handleChargeResponses(self, response, request):
        bankList = {"gtb": "058", "zenith": "057"}
        gtbResponseText = "To complete this transaction, please dial *737*50*charged_amount*159#"
        # This checks if we can parse the json successfully
        try:
            responseJson = response.json()
        except:
            raise ServerError(response)

        # If response code is not a 200
        if not response.ok:
            # If we are handling a charge call
            raise UssdChargeError(responseJson["message"])

        # Charge response code of 00 means successful, 02 means failed. Here we check if the code is not 00
        if not (responseJson["data"].get("chargeResponseCode", None) == "00"):
            # If it is we return that further action is required
            # If it is a gtbank account
            if request["accountbank"] == bankList["gtb"]:
                return True, gtbResponseText
            else:
                return True, responseJson["data"]["validateInstructions"]

        # If a charge is successful, we return that further action is not required, along with the response
        else:
            return False, responseJson["data"]
    
    # Returns True if further action is required, false if it is not
    def _handleResponses(self, response, endpoint, request):
        if endpoint  == self._baseUrl + self._endpointMap["charge"]:
            return self._handleChargeResponses(response, request)


    # Charge ussd function
    def charge(self, ussdDetails, hasFailed=False):
        """ This is used to charge through ussd.\n
             Parameters are:\n
            ussdDetails (dict) -- This is a dictionary comprising payload parameters.\n
            hasFailed (bool) -- This indicates whether the request had previously failed for timeout handling
        """
        # if ussdDetails are not defined or it is not 1
        if not ("is_ussd" in ussdDetails) or not (ussdDetails["is_ussd"] == "1"):
            ussdDetails.update({"is_ussd": "1"})
        # if payment type is not defined or not set to ussd
        if not ("payment_type" in ussdDetails) or not(ussdDetails["payment_type"] == "ussd"):
            ussdDetails.update({"payment_type": "ussd"})
        # if transaction reference is not present, generate
        if not ("txRef" in ussdDetails):
            ussdDetails.update({"txRef": generateTransactionReference()})
        if not ("orderRef" in ussdDetails):
            ussdDetails.update({"orderRef": generateTransactionReference()})
        # Checking for required ussd components (not checking for payment_type, is_ussd, txRef or orderRef again to increase efficiency)
        requiredParameters = ["accountbank", "accountnumber", "amount", "email", "phonenumber", "IP"]
        # Should return request is a less efficient call but it is required here because we need bank code in _handleResponses
        return super(Ussd, self).charge(ussdDetails, requiredParameters, shouldReturnRequest=True)
