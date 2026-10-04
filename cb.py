from PIL import Image
import argparse
import json
import os
import sys
import httpx

API_URL_PREFIX = "https://api.github.com/users/"
DESCRIPTION = "Generates GitHub profile badges that say how long you've been on GitHub."

def buildParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description = DESCRIPTION,
        epilog = "For more info, please run 'cb generate -h'. Made by helloworld3200 on GitHub with ❤️!"
    )

    subp = parser.add_subparsers(
        dest="command", required=True, help="Available commands"
    )

    # Generate command; accepts:
    # --user for the username
    # --output for the output file path (default to 'out/badge.png')
    # --message for the custom message to display on badge (default is 'I've been on GitHub for'; leave blank for no message)
    # --precision for how precise the date should be (default is 'days', can be 'days', 'months', 'years')
    # so that will show 'I've been on GitHub for \n 3 years, 5 months and 12 days' or just '3 years', etc.
    # --color for the color of the badge (but background will always be transparent)
    # --icon to specify an icon to show on the left side of the badge (default to a clock icon, leave blank for no icon)
    # all this:
    # will generate the badge, save it to the specific output.

    generate_parser = subp.add_parser(
        "generate", help="Generate a GitHub profile badge"
    )

    generate_parser.add_argument(
        "--user", type=str, required=True, help="GitHub username"
    )

    generate_parser.add_argument(
        "--output", type=str, default="out/badge.png", help="Output file path"
    )

    generate_parser.add_argument(
        "--message", type=str, default="I've been on GitHub for", help="Custom message to display on badge"
    )

    generate_parser.add_argument(
        "--precision", type=str, choices=["days", "months", "years"], default="days", help="Precision of the date"
    )

    generate_parser.add_argument(
        "--color", type=str, default="#000000", help="Color of the badge"
    )

    generate_parser.add_argument(
        "--icon", type=str, default="clock", help="Icon to display on the badge"
    )

    return parser

def handleCLI(args: argparse.Namespace) -> None:
    pass

def main() -> None:
    parser = buildParser()
    args = parser.parse_args()

    handleCLI(args)

if __name__ == "__main__":
    main()
