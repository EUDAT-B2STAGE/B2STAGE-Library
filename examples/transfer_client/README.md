Example of transfer client
-----------

This script allows to transfer files or folders via Globus transfer APIs and wait until
the transfer is completed. It uses the EUDAT library and docopt (http://docopt.org/) for 
the command line interface.

Credentials and transfer parameters can be be passed through a json resource_file
(resource_example.json) like this:

        {
            "globus_username":"",
            "globus_password":"",
            "myproxy_username": "",
            "myproxy_password": "",
            "PEM_passphrase": "",
            "src_endpoint": "",
            "dst_endpoint": "",
            "src": "",
            "dst": ""
        }


Usage:

        eudat_client.py transfer [options] <resource_file>
        eudat_client.py transfer [options] <resource_file> <src_endpoint> <dst_endpoint> <src> <dst>
        eudat_client.py (-h | --help)
        eudat_client.py --version
  


Options:

        -h --help  Show this screen.
        --version  Show version.
        -r         Recursive transfer (needed to transfer folders).
        -v         Verbose (active debug messages).
