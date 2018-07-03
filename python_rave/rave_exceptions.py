class RaveError(Exception):
    def __init__(self, msg):
        """ This is an error pertaining to the usage of one of the functions in Rave """
        super(RaveError, self).__init__(msg)
        pass

class IncompletePaymentDetailsError(RaveError):
    """ Raised when card details are incomplete """
    def __init__(self, value, requiredParameters):
        msg =  "\n\""+value+"\" was not defined in your dictionary. Please ensure you have supplied the following in the payload: \n "+'  \n '.join(requiredParameters)
        super(IncompletePaymentDetailsError, self).__init__(msg)

class CardChargeError(RaveError):
    """ Raised when card charge has failed """
    def __init__(self, message):
        msg = "\nYour card charge call failed with message: \""+str(message)+"\""
        super(CardChargeError, self).__init__(msg)

class AccountChargeError(RaveError):
    """ Raised when account charge has failed """
    def __init__(self, message):
        msg = "\nYour account charge call failed with message: \""+str(message)+"\""
        super(AccountChargeError, self).__init__(msg)

class UssdChargeError(RaveError):
    """ Raised when ussd charge has failed """
    def __init__(self, message):
        msg = "\nYour ussd charge call failed with message: \""+str(message)+"\""
        super(UssdChargeError, self).__init__(msg)

class GhMobileChargeError(RaveError):
    """ Raised when ghana mobile money transaction has failed """
    def __init__(self, message):
        msg = "\nYour Ghana mobile money charge call failed with message: \""+str(message)+"\""
        super(GhMobileChargeError, self).__init__(msg)

class MpesaChargeError(RaveError):
    """ Raised when mpesa transaction has failed """
    def __init__(self, message):
        msg = "\nYour Mpesa charge call failed with message: \""+str(message)+"\""
        super(MpesaChargeError, self).__init__(msg)
class AuthMethodNotSupportedError(RaveError):
    """ Raised when user requests for an auth method not currently supported by rave-python """
    def __init__(self, message):
        msg = "\n We do not currently support authMethod: \""+str(message)+"\". If you need this to be supported, please report in GitHub issues page"
        super(AuthMethodNotSupportedError, self).__init__(msg)

class TransactionValidationError(RaveError):
    """ Raised when validation (usually otp validation) fails """
    def __init__(self, message):
        msg = "Your transaction validate call failed with message: \""+str(message)+"\""
        super(TransactionValidationError, self).__init__(msg)

class TransactionVerificationError(RaveError):
    """ Raised when transaction could not be verified """
    def __init__(self, message):
        msg = "Your transaction verify call failed with message: \""+str(message)+"\""
        super(TransactionVerificationError, self).__init__(msg)

class PreauthInitializationError(RaveError):
    """ Raised when preauth initialization has failed """
    def __init__(self, message):
        msg = "Your preauth initialization failed with message: \""+str(message)+"\""
        super(PreauthInitializationError, self).__init__(msg)
class PreauthCaptureError(RaveError):
    """ Raised when capturing a preauthorized transaction could not be completed """
    def __init__(self, message):
        msg = "Your preauth capture call failed with message: \""+str(message)+"\""
        super(PreauthCaptureError, self).__init__(msg)

class PreauthRefundVoidError(RaveError):
    """ Raised when capturing a preauthorized refund/void transaction could not be completed """
    def __init__(self, message):
        msg = "Your preauth refund/void call failed with message: \""+str(message)+"\""
        super(PreauthRefundVoidError, self).__init__(msg)

class ServerError(RaveError):
    """ Raised when the server is down or when it could not process your request """
    def __init__(self, message):
        msg = "Your request failed. Server replied with: "+message.content
        super(ServerError, self).__init__(msg)

class RefundError(RaveError):
    """ Raised when refund fails """
    def __init__(self, message):
        msg = "Your refund call failed with message: "+str(message)
        super(RefundError, self).__init__(msg)