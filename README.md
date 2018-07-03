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

<br>

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

<br>

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

<br>

### ```.validate(txRef)```

After a successful charge, most times you will be asked to verify with OTP. To do this, you need to call the Card validate call and pass the ```flwRef```. The flwRef can be gotten from the by searching for the ```flwRef``` in the ```action``` (second returned variable) of the initial charge call. 

A sample validate call is: 

```rave.Card.validate(action["txRef"])```

#### Returns

This call returns two responses. The first variable indicates whether further action is required and the second is the data returned from your call. Note if the card validation fails, we raise a ```TransactionValidationError```. 

You can access all rave exceptions by importing ```RaveExceptions``` from the package, i.e.

```from python_rave import RaveExceptions```

<br>

### ```.verify(txRef)```

You can call this to check if your transaction was completed successfully. You have to pass the transaction reference generated at the point of charging. This is the ```txRef``` in the ```action``` parameter returned from any of the calls (```charge``` or ```validate```). 

A sample verify call is:

``` success, data, embedToken = rave.Card.verify(action["txRef"]) ```

<br>

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

    if furtherActionRequired:
        # Card validation: throws error with incomplete validation
        rave.Card.validate(action["flwRef"], "123455")



success, data, embedToken = rave.Card.verify(action["txRef"])

print(data["card"]["card_tokens"][0]["embedtoken"]) # This is the cardToken in case you want to do preauth
print(success)

```


<br><br>
## ```rave.Account```
This is used to facilitate account transactions.

**Functions included:**

* ```.charge```

* ```.validate```

* ```.verify```

<br>

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

``` furtherActionRequired, action, authUrl = rave.Account.charge(payload) ```

#### Returns

This call returns three responses. The first variable indicates whether further action is required to complete the transaction. The second variable is what was returned from the server on the call. The third variable is the authUrl (if one is required)

<br>

### ```.validate(txRef)```

After a successful charge, most times you will be asked to verify with OTP. To do this, you need to call the Card validate call and pass the ```flwRef```. The flwRef can be gotten from the by searching for the ```flwRef``` in the ```action``` (second returned variable) of the initial charge call. 

In the case that an authUrl is required, you may skip the validation step and simply pass your authUrl to the end-user.

A sample validate call is: 

```rave.Account.validate(action["txRef"])```


#### Returns

This call returns two responses. The first variable indicates whether further action is required and the second is the data returned from your call. Note if the card validation fails, we raise a ```TransactionValidationError```. 

You can access all rave exceptions by importing ```RaveExceptions``` from the package, i.e.

```from python_rave import RaveExceptions```

<br>

### ```.verify(txRef)```

You can call this to check if your transaction was completed successfully. You have to pass the transaction reference generated at the point of charging. This is the ```txRef``` in the ```action``` parameter returned any of the calls (```charge``` or ```validate```). 

A sample verify call is:

``` success, data = rave.Account.verify(data["txRef"]) ```

<br>

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


furtherActionRequired, action, authUrl = rave.Account.charge(payload)

if furtherActionRequired:
    if authUrl:
        print(authUrl)
    else:
        rave.Account.validate(action["flwRef"], "12345")

success, data = rave.Account.verify(action["txRef"])

print(success)

```

<br><br>
## ```rave.Mpesa```
This is used to facilitate Mpesa transactions.

**Functions included:**

* ```.charge```


* ```.verify```

<br>

### ```.charge(payload)```
This is called to start an Mpesa transaction. The payload should be a dictionary containing account information. It should have the parameters:

* ```account```, 

* ```email```, 

* ```phonenumber```, 

* ```IP```

Optionally, you can add a custom transaction reference using the ```txRef``` parameter. Note that if you do not specify one, it would be automatically generated. We do provide a function for generating transaction references in the Misc library (add link).


A sample call is:

``` furtherActionRequired, action = rave.Mpesa.charge(payload) ```

#### Returns

This call returns two responses. The first variable indicates whether further action is required to complete the transaction. The second variable is what was returned from the server on the call.

<br>

### ```.verify(txRef)```

You can call this to check if your transaction was completed successfully. You have to pass the transaction reference generated at the point of charging. This is the ```txRef``` in the ```action``` parameter returned any of the calls (```charge``` or ```validate```). 

A sample verify call is:

``` success, data = rave.Mpesa.verify(data["txRef"]) ```

<br>

### Complete Mpesa charge flow

```
from python_rave import Rave, RaveExceptions, Misc
rave = Rave("YOUR_PUBLIC KEY", "YOUR_SECRET_KEY", usingEnv = False)

# mobile payload
payload = {
    "amount": "100",
    "phonenumber": "0926420185",
    "email": "user@exampe.com",
    "IP": "40.14.290",
    "narration": "funds payment",
}


furtherActionRequired, action = rave.Mpesa.charge(payload)
print(action)
success, data = rave.Mpesa.verify(action["txRef"])

print(success)

```

<br><br>

## ```rave.GhMobile```
This is used to facilitate Ghana mobile money transactions.

**Functions included:**

* ```.charge```


* ```.verify```

<br>

### ```.charge(payload)```
This is called to start an Ghana mobile money transaction. The payload should be a dictionary containing account information. It should have the parameters:

* ```amount```,

* ```email```, 

* ```phonenumber```,

* ```network```,

* ```IP```,

* ```redirect_url```

Optionally, you can add a custom transaction reference using the ```txRef``` parameter. Note that if you do not specify one, it would be automatically generated. We do provide a function for generating transaction references in the Misc library (add link).


A sample call is:

``` furtherActionRequired, action = rave.GhMobile.charge(payload) ```

#### Returns

This call returns two responses. The first variable indicates whether further action is required to complete the transaction. The second variable is what was returned from the server on the call.

<br>

### ```.verify(txRef)```

You can call this to check if your transaction was completed successfully. You have to pass the transaction reference generated at the point of charging. This is the ```txRef``` in the ```action``` parameter returned any of the calls (```charge``` or ```validate```). 

A sample verify call is:

``` success, data = rave.GhMobile.verify(data["txRef"]) ```

<br>

### Complete GhMobile charge flow

```
from python_rave import Rave, RaveExceptions, Misc
rave = Rave("YOUR_PUBLIC KEY", "YOUR_SECRET_KEY", usingEnv = False)

# mobile payload
payload = {
  "amount": "50",
  "email": "user@example.com",
  "phonenumber": "054709929220",
  "network": "MTN",
  "redirect_url": "https://rave-webhook.herokuapp.com/receivepayment",
  "IP":""
}


furtherActionRequired, action = rave.GhMobile.charge(payload)

success, data = rave.GhMobile.verify(action["txRef"])

print(success)

```


<br><br>
## ```rave.Ussd```
This is used to facilitate USSD transactions.

**Functions included:**

* ```.charge```


* ```.verify```

<br>

### ```.charge(payload)```
This is called to start a USSD transaction. The payload should be a dictionary containing payment information. It should have the parameters:

* ```accountbank```,

* ```accountnumber```, 

* ```amount```, 

* ```email```,

* ```phonenumber```,

* ```IP```

Optionally, you can add a custom transaction reference using the ```txRef``` parameter. Note that if you do not specify one, it would be automatically generated. We do provide a function for generating transaction references in the Misc library (add link).


A sample call is:

``` furtherActionRequired, action = rave.Ussd.charge(payload) ```

#### Returns

This call returns two responses. The first variable indicates whether further action is required to complete the transaction. The second variable is what was returned from the server on the call.

<br>

### ```.verify(txRef)```

You can call this to check if your transaction was completed successfully. You have to pass the transaction reference generated at the point of charging. This is the ```txRef``` in the ```action``` parameter returned any of the calls (```charge``` or ```validate```). 

A sample verify call is:

``` success, data = rave.Ussd.verify(data["txRef"]) ```

<br>

### Complete USSD charge flow

```
from python_rave import Rave, RaveExceptions, Misc
rave = Rave("YOUR_PUBLIC KEY", "YOUR_SECRET_KEY", production=True, usingEnv = False)

zenithPayload = {
  "accountbank": "057",
  "accountnumber": "0691008392",#collect the customers account number for Zenith
  "currency": "NGN",
  "country": "NG",
  "amount": "10",
  "email": "desola.ade1@gmail.com",
  "phonenumber": "0902620185", 
  "IP": "355426087298442",
}

furtherActionNeeded, action = rave.Ussd.charge(zenithPayload)
if furtherActionNeeded:
  completed = False
  while not completed:
    try:
      completed = rave.Ussd.verify(zenithPayload["txRef"])
    except RaveExceptions.TransactionVerificationError:
      print(action)
    
success, data = rave.Ussd.verify(zenithPayload["txRef"])
print(success)

```

<br><br>
## ```rave.Preauth```
This is used to facilitate preauthorized card transactions.

**Functions included:**

* ```.charge```

* ```.validate```

* ```.verify```

* ```.getTypeOfArgsRequired```

* ```.updatePayload```

<br>

### ```.charge(payload)```
This is called to start a preauthorized card transaction. The payload should be a dictionary containing card information. It should have the parameters:

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

``` furtherActionRequired, action, suggestedAuth = rave.Preauth.preauth(payload) ```

#### Returns

This call returns three responses. The first variable indicates whether further action is required to complete the transaction. The second variable is what was returned from the server on the call. The third variable indicates the suggested authentication method required to complete the charge call.

<br>

### ```.updatePayload(authMethod, payload, arg)```

Depending on the suggestedAuth from the charge call, you may need to update the payload with a pin or address. To know which type of authentication you would require, simply call ```rave.Preauth.getTypeOfArgsRequired(suggestedAuth)```. This returns either ```pin``` or ```address```. 

In the case of ```pin```, you are required to call ```rave.Preauth.updatePayload(suggestedAuth, payload, pin="THE_CUSTOMER_PIN")```. 

In the case of ```address```, you are required to call ```rave.Preauth.updatePayload(suggestedAuth, payload, address={ THE_ADDRESS_DICTIONARY })```

A typical address dictionary includes the following parameters:

```billingzip```, 

```billingcity```,

```billingaddress```, 
 
```billingstate```,
 
```billingcountry```

**Note:**
```suggestedAuth``` is the suggestedAuth returned from the initial charge call and ```payload``` is the original payload

<br>

### ```.validate(txRef)```

After a successful charge, most times you will be asked to verify with OTP. To do this, you need to call the Preauth validate call and pass the ```flwRef```. The flwRef can be gotten from the by searching for the ```flwRef``` in the ```action``` (second returned variable) of the initial charge call. 

A sample validate call is: 

```rave.Preauth.validate(action["txRef"])```

#### Returns

This call returns two responses. The first variable indicates whether further action is required and the second is the data returned from your call. Note if the card validation fails, we raise a ```TransactionValidationError```. 

You can access all rave exceptions by importing ```RaveExceptions``` from the package, i.e.

```from python_rave import RaveExceptions```

<br>

### ```.verify(txRef)```

You can call this to check if your transaction was completed successfully. You have to pass the transaction reference generated at the point of charging. This is the ```txRef``` in the ```action``` parameter returned from any of the calls (```charge``` or ```validate```). 

A sample verify call is:

``` success, data = rave.Preauth.verify(action["txRef"]) ```

<br>

### ```.capture(flwRef)```

This is used to capture the funds held in the account. Similar to the validate call, it requires you to pass the ```flwRef```. The flwRef can be gotten from the by searching for the ```flwRef``` in the ```action``` (second returned variable) of the initial charge call.


A sample capture call is:

``` rave.Preauth.capture(data["flwRef"])```

<br>

### ```.void(flwRef)```

This is used to void a preauth transaction. Similar to the validate call, it requires you to pass the ```flwRef```. The flwRef can be gotten from the by searching for the ```flwRef``` in the ```action``` (second returned variable) of the initial charge call.


A sample capture call is:

```rave.Preauth.void(data["flwRef"]) ```

<br>

### ```.refund(flwRef)```

This is used to refund a preauth transaction. Similar to the validate call, it requires you to pass the ```flwRef```. The flwRef can be gotten from the by searching for the ```flwRef``` in the ```action``` (second returned variable) of the initial charge call.


A sample capture call is:

```rave.Preauth.refund(data["flwRef"]) ```

<br>


### Complete preauth charge flow

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


furtherActionRequired, action, suggestedAuth = rave.Preauth.preauth(payload)

if furtherActionRequired:

    # If suggested auth is in the response, it means the payload was not complete, we've provided a handy updatePayload method that can help verify your completed payload
    # Using updatePayload will also maintain the transaction reference

    if suggestedAuth:

        # get type of args required returns either pin or address. the way each are responded to are displayed below

        authType = rave.Preauth.getTypeOfArgsRequired(suggestedAuth)

        # Tailor update payload based on authType

        if authType == "pin":
            rave.Preauth.updatePayload(suggestedAuth, payload, pin="3310")
        if authType == "address":

            rave.Preauth.updatePayload(suggestedAuth, payload, address={"billingzip": "07205", "billingcity": "Hillside", "billingaddress": "470 Mundet PI", "billingstate": "NJ", "billingcountry": "US"})
        
        # Recall preauth 
        furtherActionRequired, action, suggestedAuth = rave.Preauth.preauth(payload)

    if furtherActionRequired:
        success, data = rave.Preauth.verify(action["txRef"])
        # Preauth validation: throws error with incomplete validation
        rave.Preauth.validate(action["flwRef"], "123455")



success, data, embedToken = rave.Preauth.verify(action["txRef"])

print(embedToken) # This is the cardToken in case you want to do preauth

rave.Preauth.capture(data["flwRef"]) # To capture


```
