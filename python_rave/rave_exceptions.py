class RaveError(Exception):
    def __init__(self, msg):
        """ This is an error pertaining to the usage of one of the functions in Rave """
        super(RaveError, self).__init__(msg)
        pass

# Non-Transaction related errors
class IncompletePaymentDetailsError(RaveError):
    """ Raised when card details are incomplete """
    def __init__(self, value, requiredParameters):
        msg =  "\n\""+value+"\" was not defined in your dictionary. Please ensure you have supplied the following in the payload: \n "+'  \n '.join(requiredParameters)
        super(IncompletePaymentDetailsError, self).__init__(msg)


class AuthMethodNotSupportedError(RaveError):
    """ Raised when user requests for an auth method not currently supported by rave-python """
    def __init__(self, message):
        msg = "\n We do not currently support authMethod: \""+str(message)+"\". If you need this to be supported, please report in GitHub issues page"
        super(AuthMethodNotSupportedError, self).__init__(msg)

# Transaction related errors
class CardChargeError(RaveError):
    """ Raised when card charge has failed """
    def __init__(self, err):
        self.err = err
    def __str__(self):
        return "Your card charge call failed with message: "+self.err["errMsg"]

class AccountChargeError(RaveError):
    """ Raised when account charge has failed """
    def __init__(self, err):
        self.err = err
    def __str__(self):
        return "Your account charge call failed with message: "+self.err["errMsg"]

class UssdChargeError(RaveError):
    """ Raised when ussd charge has failed """
    def __init__(self, err):
        self.err = err

    def __str__(self):
        return "Your ussd charge call failed with message: "+self.err["errMsg"]

class PreauthCaptureError(RaveError):
    """ Raised when capturing a preauthorized transaction could not be completed """
    def __init__(self, err):
        self.err = err
        
    def __str__(self):
        return "Your preauth capture call failed with message: "+self.err["errMsg"]

class PreauthRefundVoidError(RaveError):
    """ Raised when capturing a preauthorized refund/void transaction could not be completed """
    def __init__(self, err):
        self.err = err
        
    def __str__(self):
        return "Your preauth refund/void call failed with message: "+self.err["errMsg"]

# Generic transaction errors
class TransactionChargeError(RaveError):
    """ Raised when a transaction charge has failed """
    def __init__(self, err):
        self.err = err
    def __str__(self):
        return "Your account charge call failed with message: "+self.err["errMsg"]

class TransactionValidationError(RaveError):
    """ Raised when validation (usually otp validation) fails """
    def __init__(self, err):
        self.err = err

    def __str__(self):
        return "Your transaction validation call failed with message: "+self.err["errMsg"]

class TransactionVerificationError(RaveError):
    """ Raised when transaction could not be verified """
    def __init__(self, err):
        self.err = err

    def __str__(self):
        return "Your transaction verification call failed with message: "+self.err["errMsg"]


class ServerError(RaveError):
    """ Raised when the server is down or when it could not process your request """
    def __init__(self, err):
        self.err = err
        
    def __str__(self):
        return " Server is down with error: " + self.err["errMsg"]

class RefundError(RaveError):
    """ Raised when refund fails """
    def __init__(self, message):
        msg = "Your refund call failed with message: "+str(message)
        super(RefundError, self).__init__(msg)

class InitiateTransferError(RaveError):
    """ Raised when transfer initiation fails """
    def __init__(self, err):
        self.err = err
    
    def __str__(self):
        return "Transfer initiation failed with error: " + self.err["errMsg"]

class TransferFetchError(RaveError):
    """ Raised when fetching transfer fails """
    def __init__(self, err):
        self.err = err
    
    def __str__(self):
        return "Transfer fetch failed with error: " + self.err["errMsg"]