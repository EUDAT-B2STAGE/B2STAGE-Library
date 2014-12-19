B2STAGE-Library
===============

Python library for interacting with the EUDAT environment

Usage example
-------------
```
import eudat

from eudat import *

context = eudat.AuthUserPass('username', 'password')
// context = eudat.AuthGSI('path to certificate')

context.putHttp('local file')
// context.putGFtp('local file')
// context.putGFtp('source', 'destination')

datasets = context.find('Searh over meta-data')
// datasets = context.find('PID')

datasets.stage('LOCAL')
datasets.stage('REMOTE')

datasets.analytics('Destination') // create a temporary analytics environment

```


