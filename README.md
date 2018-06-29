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

## Rave Objects
### Card -- rave.Card
This is used to facilitate card transactions.

**Functions included:**
```.charge```
```.validate```
```.verify```
```.getTypeOfArgsRequired```
```.updatePayload```

#### ```.charge(payload)```
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

#### Returns

This call returns three responses. The first variable indicates whether further action is required to complete the transaction. The second variable is what was returned from the server on the call. The third variable indicates the suggested authentication method required to complete the charge call.

A sample call is:

``` furtherActionRequired, action, suggestedAuth = rave.Card.charge(payload) ```

#### ```.updatePayload(authMethod, payload, arg)```

Depending on the suggestedAuth from the charge call, you may need to update the payload with a pin or address. To know which type of authentication you would require, simply call ```rave.Card.getTypeOfArgsRequired(suggestedAuth)```. This returns either ```pin``` or ```address```. 

In the case of ```pin```, you are required to call ```rave.Card.updatePayload(suggestedAuth, payload, pin="THE_CUSTOMER_PIN")```. 

**Note:**
```suggestedAuth``` is the suggestedAuth returned from the initial charge call

```payload``` is the original payload

#### ```.validate(txRef)```

After a successful charge, most times you will be asked to verify with OTP. To do this, you need to call the Card validate call and pass the ```txRef```. The txRef can be gotten from the by searching for the ```txRef``` in the ```action``` (second returned variable) of the initial charge call. 

```rave.Card.validate(action["txRef"])```

#### Returns

This call returns two responses. The first variable indicates whether further action is required and the second is the data returned from your call. Note if the card validation fails, we raise a ```TransactionValidationError```. 







