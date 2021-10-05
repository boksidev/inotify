import argparse
import pathlib
from monitor import main


parser = argparse.ArgumentParser("monitor")
parser.add_argument(
    "config",
    metavar="CONFIG_FILE",
    type=pathlib.Path,
    help="path to the config file to use",
)
args = parser.parse_args()

main(args)
