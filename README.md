B2STAGE-Library
===============

Python library for interacting with the EUDAT environment

Usage example
-------------
```
import eudat

from eudat import *


context = eudat.AuthUserPass('username', 'password')

context = eudat.AuthGSI('path to certificate')

context.putHttp('local file')
context.putGFTP('local file')
context.putGFTP('source', 'destination')
```


