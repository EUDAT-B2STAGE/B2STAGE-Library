B2STAGE-Library
===============

Python library for interacting with the EUDAT environment

The goal of this library is to provide users with a programmatic access to EUDAT
services. Leveraging the former Data Staging Script, it aims at supporting
interactions with all EUDAT services ranging from the ingestion of new data sets,
the discovery, the retrieval, to the analysis.



Usage example
-------------
```
import eudat

context = eudat.AuthUserPass('username', 'password')
# context = eudat.AuthGSI('path to certificate')

res = context.putHttp('local file')
# res = context.putGFtp('local file')
# res = context.putGFtp('source', 'destination')

datasets = context.find('Searh over meta-data')
# datasets = context.find('PID')

res = datasets.stage('LOCAL')
# res = datasets.stage('REMOTE')

ana = datasets.analytics('Destination') // create a temporary analytics environment

filtered_data = ana.filter(lamba a,b: a + b)

```


