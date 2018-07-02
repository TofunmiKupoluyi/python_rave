# Python_Rave

## Introduction
This is a Python wrapper around the [API](https://flutterwavedevelopers.readme.io/v2.0/reference) for [Rave by Flutterwave](https://rave.flutterwave.com).
#### Payment types implemented:
* Card Payments
* Bank Account Payments
* Ghana Mobile Money Payments
* Mpesa
* USSD Payments
## Installation
To install, run
```python -m pip install --index-url https://test.pypi.org/simple/ python_rave```

Note: This is currently under active development
## Import Package
The base class for this package is 'Rave'. To use this class, add:

``` from python_rave import Rave ```

## Initialization

#### To instantiate in sandbox:
To use Rave, instantiate the Rave class with your public key. We recommend that you store your secret key in an environment variable named, ```RAVE_SECRET_KEY```. Instantiating your rave object is therefore as simple as:

``` rave = Rave("YOUR_PUBLIC_KEY")```

####  To instantiate without environment variables (Sandbox):
If you choose not to store your secret key in an environment variable, we do provide a ```usingEnv``` flag which can be set to ```False```, but please be warned, do not use this package without environment variables in production

``` rave = Rave("YOUR_PUBLIC_KEY", "YOUR_SECRET_KEY", usingEnv = False) ```


#### To instantiate in production:
To initialize in production, simply set the ```production``` flag to ```True```. It is highly discouraged but if you choose to not use environment variables, you can do so in the same way mentioned above.

``` rave = Rave("YOUR_PUBLIC_KEY", production=True)```

# Rave Objects
This is the documentation for all of the components of python_rave

## ```rave.Card```
This is used to facilitate card transactions.

**Functions included:**

* ```.charge```

* ```.validate```

* ```.verify```

* ```.getTypeOfArgsRequired```

* ```.updatePayload```

### ```.charge(payload)```
This is called to start a card transaction. The payload should be a dictionary containing card information. It should have the parameters:

* ```cardno```,

* ```cvv```, 

* ```expirymonth```, 

* ```expiryyear```, 

* ```amount```, 

* ```email```, 

* ```phonenumber```,

* ```firstname```, 

* ```lastname```, 

* ```IP```

Optionally, you can add a custom transaction reference using the ```txRef``` parameter. Note that if you do not specify one, it would be automatically generated. We do provide a function for generating transaction references in the Misc library (add link).


A sample call is:

``` furtherActionRequired, action, suggestedAuth = rave.Card.charge(payload) ```

#### Returns

This call returns three responses. The first variable indicates whether further action is required to complete the transaction. The second variable is what was returned from the server on the call. The third variable indicates the suggested authentication method required to complete the charge call.


### ```.updatePayload(authMethod, payload, arg)```

Depending on the suggestedAuth from the charge call, you may need to update the payload with a pin or address. To know which type of authentication you would require, simply call ```rave.Card.getTypeOfArgsRequired(suggestedAuth)```. This returns either ```pin``` or ```address```. 

In the case of ```pin```, you are required to call ```rave.Card.updatePayload(suggestedAuth, payload, pin="THE_CUSTOMER_PIN")```. 

In the case of ```address```, you are required to call ```rave.Card.updatePayload(suggestedAuth, payload, address={ THE_ADDRESS_DICTIONARY })```

A typical address dictionary includes the following parameters:

```billingzip```, 

```billingcity```,

```billingaddress```, 
 
```billingstate```,
 
```billingcountry```

**Note:**
```suggestedAuth``` is the suggestedAuth returned from the initial charge call and ```payload``` is the original payload

### ```.validate(txRef)```

After a successful charge, most times you will be asked to verify with OTP. To do this, you need to call the Card validate call and pass the ```flwRef```. The flwRef can be gotten from the by searching for the ```flwRef``` in the ```action``` (second returned variable) of the initial charge call. 

```rave.Card.validate(action["txRef"])```

#### Returns

This call returns two responses. The first variable indicates whether further action is required and the second is the data returned from your call. Note if the card validation fails, we raise a ```TransactionValidationError```. 

You can access all rave exceptions by importing ```RaveExceptions``` from the package, i.e.

```from python_rave import RaveExceptions```


### ```.verify(txRef)```

You can call this to check if your transaction was completed successfully. You have to pass the transaction reference generated at the point of charging. This is the ```txRef``` in the ```action``` parameter returned from any of the calls (```charge``` or ```validate```). 

A sample verify call is:

``` success, data = rave.Card.verify(action["txRef"]) ```






### Complete card charge flow

```
from python_rave import Rave
rave = Rave("YOUR_PUBLIC_KEY", "YOUR_SECRET_KEY", usingEnv = False)
# Payload with pin
payload = {
  "cardno": "5438898014560229",
  "cvv": "890",
  "expirymonth": "09",
  "expiryyear": "19",
  "currency": "NGN",
  "country": "NG",
  "amount": "10",
  "email": "user@gmail.com",
  "phonenumber": "0902620185",
  "firstname": "temi",
  "lastname": "desola",
  "IP": "355426087298442",
  "redirect_url": "https://rave-webhook.herokuapp.com/receivepayment",
  "device_fingerprint": "69e6b7f0b72037aa8428b70fbe03986c",
}


furtherActionRequired, action, suggestedAuth = rave.Card.charge(payload)

if furtherActionRequired:
    # If suggested auth is in the response, it means the payload was not complete, we've provided a handy updatePayload method that can help verify your completed payload
    # Using updatePayload will also maintain the transaction reference
    if suggestedAuth:
        # get type of args required returns either pin or address. the way each are responded to are displayed below
        authType = rave.Card.getTypeOfArgsRequired(suggestedAuth)
        # Tailor update payload based on authType
        if authType == "pin":
            rave.Card.updatePayload(suggestedAuth, payload, pin="3310")
        if authType == "address":
            rave.Card.updatePayload(suggestedAuth, payload, address={"billingzip": "07205", "billingcity": "Hillside", "billingaddress": "470 Mundet PI", "billingstate": "NJ", "billingcountry": "US"})
        
        # Recall card charge
        furtherActionRequired, action, suggestedAuth = rave.Card.charge(payload)

    # I know, it's strange but this helps keep your code length short. If suggested_auth is present furtherActionRequired might've changed.
    if furtherActionRequired:
        success, data = rave.Card.verify(action["txRef"])
        # Card validation: throws error with incomplete validation
        rave.Card.validate(action["flwRef"], "123455")



success, data = rave.Card.verify(action["txRef"])

print(data["card"]["card_tokens"][0]["embedtoken"]) # This is the cardToken in case you want to do preauth
print(success)

```



## ```rave.Account```
This is used to facilitate account transactions.

**Functions included:**

* ```.charge```

* ```.validate```

* ```.verify```


### ```.charge(payload)```
This is called to start an account transaction. The payload should be a dictionary containing card information. It should have the parameters:

* ```accountbank```, 

* ```accountnumber```, 

* ```amount```, 

* ```email```, 

* ```phonenumber```, 

* ```IP```

Optionally, you can add a custom transaction reference using the ```txRef``` parameter. Note that if you do not specify one, it would be automatically generated. We do provide a function for generating transaction references in the Misc library (add link).


A sample call is:

``` furtherActionRequired, action = rave.Account.charge(payload) ```

#### Returns

This call returns three responses. The first variable indicates whether further action is required to complete the transaction. The second variable is what was returned from the server on the call.

### ```.validate(txRef)```

After a successful charge, most times you will be asked to verify with OTP. To do this, you need to call the Card validate call and pass the ```flwRef```. The flwRef can be gotten from the by searching for the ```flwRef``` in the ```action``` (second returned variable) of the initial charge call. 

```rave.Card.validate(action["txRef"])```


#### Returns

This call returns two responses. The first variable indicates whether further action is required and the second is the data returned from your call. Note if the card validation fails, we raise a ```TransactionValidationError```. 

You can access all rave exceptions by importing ```RaveExceptions``` from the package, i.e.

```from python_rave import RaveExceptions```


### ```.verify(txRef)```

You can call this to check if your transaction was completed successfully. You have to pass the transaction reference generated at the point of charging. This is the ```txRef``` in the ```action``` parameter returned any of the calls (```charge``` or ```validate```). 

A sample verify call is:

``` success, data = rave.Card.verify(data["txRef"]) ```


### Complete account charge flow

```
from python_rave import Rave, RaveExceptions, Misc
rave = Rave("YOUR_PUBLIC KEY", "YOUR_SECRET_KEY", usingEnv = False)
# account payload
payload = {
  "accountbank": "232",# get the bank code from the bank list endpoint.
  "accountnumber": "0061333471",
  "currency": "NGN",
  "country": "NG",
  "amount": "100",
  "email": "test@test.com",
  "phonenumber": "0902620185",
  "IP": "355426087298442",
}


furtherActionRequired, action = rave.Account.charge(payload)

if furtherActionRequired:
    if not (action.get("authurl", "NO-URL") == "NO-URL"):
        print(action["authurl"])
    else:
        rave.Account.validate(action["flwRef"], "12345")
    
else:
    rave.Account.validate(action["flwRef"], "12345")

success, data = rave.Account.verify(action["txRef"])

print(success)
```









