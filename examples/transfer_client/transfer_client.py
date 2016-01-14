"""

This script allows to transfer files or folders via Globus transfer APIs and wait until
the transfer is completed.

Credentials and transfer parameters can be be passed through a json resource_file
like this:

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

"""
import sys
import os
import json
sys.path.append(os.path.abspath("/home/rmucci00/Devel/EUDAT/B2STAGE-Library"))
from eudat import b2stage
from docopt import docopt


def b2stage_client(args):
    RESOURCES_FILE = args['<resource_file>']

    if not args['<src_endpoint>']:
        res_file = json.load(open(RESOURCES_FILE))
        src_endpoint = res_file['src_endpoint']
        dst_endpoint = res_file['dst_endpoint']
        src = res_file['src']
        dst = res_file['dst']
    else:
        src_endpoint = args['<src_endpoint>']
        dst_endpoint = args['<dst_endpoint>']
        src = args['<src>']
        dst = args['<dst>']

    # Initialize the Globus client
    globus = b2stage.ClientGlobus(resource_file_path=RESOURCES_FILE, debug=args['-v'])

    # Perform a data transfer between 2 endpoints (third party transfer)
    task_id = globus.transfer(src_endpoint, dst_endpoint, src,
                                  dst, recursive=args['-r'])

    print "****** TASK ID: {0} ******\n".format(task_id)

    # Wait for task to end
    status = globus.wait_for_task(task_id, timeout=0, poll_interval=10)
    print 'status = ' + status

    # Display successful transfer details
    globus.display_successful_transfer(task_id)

    # TO DO: get the PID of the uploaded files...


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Eudat_client 0.1')
    # print(arguments)
    if arguments['transfer']:
        b2stage_client(arguments)