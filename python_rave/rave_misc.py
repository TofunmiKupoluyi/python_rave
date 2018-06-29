""" Miscallaneous helper functions """
import time
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