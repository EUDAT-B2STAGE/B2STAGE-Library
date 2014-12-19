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

res = context.putHttp('local file')
// res = context.putGFtp('local file')
// res = context.putGFtp('source', 'destination')

datasets = context.find('Searh over meta-data')
// datasets = context.find('PID')

res = datasets.stage('LOCAL')
// res = datasets.stage('REMOTE')

ana = datasets.analytics('Destination') // create a temporary analytics environment

filtered_data = ana.filter(lamba a,b: a + b)

```


