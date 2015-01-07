__version__ = '0.1'
__author__ = 'Giuseppe Fiameni'


import sys

try:
    from globusonline.transfer import api_client
except ImportError:
    from globusonline import *
