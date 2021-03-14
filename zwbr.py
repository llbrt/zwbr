import sys
import logging
from argparse import ArgumentParser
from argparse import FileType

from zwbrlib.controller import Controller
from zwbrlib.controllerdetails import ControllerDetails
from zwbrlib.nodelist import NodeList
from zwbrlib.backup import ZwBackup
from zwbrlib.restore import ZwRestoration

if sys.version_info < (3, 6):
    print("Invalid python version, version 3.6 or upper is required")
    sys.exit(1)

p = ArgumentParser(description="Z-Wave controller NVM backup and restore")
p.add_argument(dest="device", help="device of the Z-Wave controller (like COM4 for Windows or /dev/ttyACM0 for Linux)")
p.add_argument('-v', '--verbose', dest="verbose", action='store_true', help="enable verbose mode")
p.add_argument('-n', '--nodes', dest="nodes", action='store_true', help="display nodes")
p.add_argument('-s', '--scan-nodes', dest="full_scan", action='store_true', help="try all the node ids (slower)")
p.add_argument('-b', '--backup-file', dest="backup_dest", metavar="dest-file", help="backup the controller in the destination file")
p.add_argument('-r', '--restore-file', dest="restore_source", metavar="source-file", type=FileType('rb'), help="restore the controller from the source file")
args = p.parse_args()

# Initialize logging
if args.verbose:
    level = logging.DEBUG
else:
    level = logging.INFO
logging.basicConfig(format='%(levelname)s: %(message)s', level=level, stream=sys.stdout)

# Initialize controller access
controller = Controller(args.device)

# Display controller type and version
controller_details = ControllerDetails(controller)
controller_details.log()

# List nodes
if args.nodes:
    nodes = NodeList(controller, controller_details, args.full_scan)
    nodes.log()

if args.backup_dest:
    backup = ZwBackup(controller, args.backup_dest)
    try:
        backup.exec()
    except BaseException:
        logging.exception("Backup failed")
    del backup

if args.restore_source:
    restore = ZwRestoration(controller, controller_details, args.restore_source)
    try:
        restore.exec()
    except BaseException:
        logging.exception("Restoration failed")
    del restore

controller.close()
