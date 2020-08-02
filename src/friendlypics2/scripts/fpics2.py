"""Command line interface to the project"""
import sys
from friendlypics2.main import run


def main():
    """primary entry point method"""
    sys.exit(run(sys.argv))


if __name__ == "__main__":
    main()
