"""Command line interface to the project"""
import sys
import logging
from friendlypics2.main import run


def main():
    """primary entry point method"""
    logging.basicConfig(level=logging.DEBUG)
    sys.exit(run(sys.argv))


if __name__ == "__main__":
    main()
