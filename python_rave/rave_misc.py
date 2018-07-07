""" Miscallaneous helper functions """
import time
from python_rave.rave_exceptions import IncompletePaymentDetailsError, AuthMethodNotSupportedError
# Helper function to generate unique transaction reference
def generateTransactionReference(merchantId=None):
    """ This is a helper function for generating unique transaction  references.\n
         Parameters include:\n
        merchantId (string) -- (optional) You can specify a merchant id to start references e.g. merchantId-12345678
    """
    if merchantId:
        return merchantId+"-"+str(int(round(time.time() * 1000)))
    else:
        return "MC-"+str(int(round(time.time() * 1000)))

# If parameters are complete, returns true. If not returns false with parameter missing
def checkIfParametersAreComplete(requiredParameters, paymentDetails):
    """ This returns true/false depending on if the paymentDetails match the required parameters """
    for i in requiredParameters:
        if i not in paymentDetails:
            return False, i
    return True, None

def getTypeOfArgsRequired(suggestedAuth):
    """ This is used to get the type of argument needed to complete your charge call.\n
            Parameters include:\n
        suggestedAuth (dict) -- This is the action returned from the charge call\n

        Returns:\n
        pin -- This means that the updatePayload call requires a pin. Pin is passed as a string argument to updatePayload\n
        address -- This means that the updatePayload call requires an address dict. The dict must contain "billingzip", "billingcity", "billingaddress", "billingstate", "billingcountry".
    """
    keywordMap = {"PIN":"pin", "AVS_VBVSECURECODE":"address", "NOAUTH_INTERNATIONAL":"address"}
    # Checks if the auth method passed is included in keywordMapping i.e. if it is supported
    if not keywordMap.get(suggestedAuth, None):
        raise AuthMethodNotSupportedError(suggestedAuth)
    
    return keywordMap[suggestedAuth]

# Update payload
def updatePayload(suggestedAuth, payload, **kwargs): 
    """ This is used to update the payload of your request upon a charge that requires more parameters. It maintains the transaction refs and all the original parameters of the request.\n
            Parameters include:\n
        suggestedAuth (dict) -- This is what is returned from the charge call\n
        payload (dict) -- This is the original payload\n
        \n
        ## This updates payload directly
    """ 

    # Sets the keyword to check for in kwargs (it maps the suggestedAuth to keywords)
    keyword = getTypeOfArgsRequired(suggestedAuth)

    # Checks

    # 1) Checks if keyword is present in kwargs
    if not kwargs.get(keyword, None):
        # Had to split variable assignment and raising ValueError because of error message python displayed
        errorMsg = "Please provide the appropriate argument for the auth method. For {}, we require a \"{}\" argument.".format(suggestedAuth["suggested_auth"], keyword)
        raise ValueError(errorMsg)

    # 2) If keyword is address, checks if all required address paramaters are present
    if keyword == "address":
        requiredAddressParameters = ["billingzip", "billingcity", "billingaddress", "billingstate", "billingcountry"]
        areDetailsComplete, missingItem  = checkIfParametersAreComplete(requiredAddressParameters, kwargs[keyword])
        if not areDetailsComplete:
            raise IncompletePaymentDetailsError(missingItem, requiredAddressParameters)
        
    # All checks passed

    # Add items to payload
    # If the argument is a dictionary, we add the argument as is
    if isinstance(kwargs[keyword], dict):
        payload.update(kwargs[keyword])

    # If it's not we add it manually
    else:
        payload.update({"suggested_auth": suggestedAuth})
        payload.update({keyword: kwargs[keyword]})
            
    