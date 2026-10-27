from PIL import Image
import argparse
import os
import sys
import httpx
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
import logging

DESCRIPTION = "Generates GitHub profile badges that say how long you've been on GitHub."
CREDITS = "Made by helloworld3200 on GitHub with ❤️!"
VER = "1.0.0"

PRECISION = ["days", "months", "years"]

def buildParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description = DESCRIPTION,
        epilog = CREDITS,
        # Append default values to the help message for each argument
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "user", type=str, help="GitHub username"
    )

    # The parser accepts:
    # --output for the output file path (default to 'out/badge.png')
    # --message for the custom message to display on badge (default is 'I've been on GitHub for'; leave blank for no message)
    # --precision for how precise the date should be (default is 'days', can be 'days', 'months', 'years')
    # so that will show 'I've been on GitHub for \n 3 years, 5 months and 12 days' or just '3 years', etc.
    # --color for the color of the badge (but background will always be transparent; default to blue)
    # --icon to specify an icon to show on the left side of the badge (default to a clock icon, leave blank for no icon)
    # all this:
    # will generate the badge, save it to the specific output.

    parser.add_argument(
        "--output", type=str, default="out/badge.png", help="Output file path"
    )

    parser.add_argument(
        "--message", type=str, default="I've been on GitHub for", help="Custom message to display on badge, leave blank for no message"
    )

    parser.add_argument(
        "--precision", type=str, choices=PRECISION, default="days", help="Precision of the date"
    )

    parser.add_argument(
        "--color", type=str, default="#0000FF", help="Color of the badge"
    )

    parser.add_argument(
        "--icon", type=str, default="clock", help="Icon to display on the badge, leave blank for no icon"
    )

    return parser

@dataclass
class Lifespan:
    years: int
    months: int
    days: int

def calcLifespan(dt: datetime, daysYr: float = 365.25, daysMo: float = 30.44) -> Lifespan:
    now: datetime = datetime.now(timezone.utc)
    diff: timedelta = now - dt
    logging.info(f"Calculated time delta: {diff}")

    # Extract years
    years: int = int(diff.days // daysYr)
    remaining_days: float = diff.days % daysYr

    # Extract months and final days
    months: int = int(remaining_days // daysMo)
    days: int = int(remaining_days % daysMo)

    return Lifespan(years=years, months=months, days=days)

# Main function that actually sends the GET request and returns the user lifespan
def fetchLifespan(
        user: str,
        apiURLPrefix: str = "https://api.github.com/users/",
        headers: dict = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
        },
        creationKey: str = "created_at"
    ) -> Lifespan:

    # Dispatch GET request
    finalAPIURL: str = f"{apiURLPrefix}{user}"

    logging.info(f"Requesting from: {finalAPIURL}")
    logging.info(f"Dispatching GET with headers: \n {headers}")
    
    res: httpx.Response = httpx.get(finalAPIURL, headers=headers)
    logging.info(f"Received response with status code: {res.status_code}")
    res.raise_for_status()

    # Parse to JSON and retrieve created_at field; convert to datetime
    data: dict = res.json()
    created: str = data[creationKey]
    logging.info(f"Retrieved creation timestamp: {created}")
    dt: datetime = datetime.fromisoformat(created) # Older tutorials will say to replace Z with +00:00 but since like py 3.11 its no longer needed

    # Calculate lifespan and format
    lifespan: Lifespan = calcLifespan(dt)

    return lifespan

# Styling, spacing etc for the badge - all sizing in pixels
@dataclass
class BadgeDrawStyle:
    # Fonts: any TrueType path, or a filename Pillow can find on your system.
    caption_font: str = "fonts/Montserrat-Light.ttf"
    title_font: str = "fonts/Montserrat-Medium.ttf"
    caption_size: int = 18
    title_size: int = 40
 
    # Spacing
    line_gap: int = 4  # caption -> title
    icon_gap: int = 12  # icon -> text block
    margin: int = 16  # content -> border
    border_width: int = 2  # set to 0 to disable
 
    # Icon
    icon_set: str = "lucide"
    icon_height_ratio: float = 1.0  # icon height relative to the text block
    icon_supersample: int = 4  # render big, then downscale for crisp edges

# Final data which is sent to drawBadge after data is processed by buildBadge
@dataclass
class BadgeDrawData:
    caption: str
    title: str
    iconName: str
    colour: str

def drawBadge(badgeData: BadgeDrawData):
    pass

def buildBadge(lifespan: Lifespan, precision: str, message: str, color: str, icon: str) -> None:
    # Build the lifespan according to precision (eventually this is drawn as 'title')
    yearsStr: str = f"{lifespan.years} years" if lifespan.years > 0 else ""
    monthsStr: str = f"{lifespan.months} months"
    daysStr: str = f"{lifespan.days} days"

    if lifespan.years == 0 and precision == "years":
        logging.warning("Precision set to 'years' but lifespan is less than a year. Defaulting to 'months'.")
        precision = "months"
    elif lifespan.months == 0 and precision == "months":
        logging.warning("Precision set to 'months' but lifespan is less than a month. Defaulting to 'days'.")
        precision = "days"

    title: str = ""
    match precision:
        case "years":
            title = yearsStr
        case "months":
            title = f"{yearsStr} and {monthsStr}" if yearsStr else monthsStr
        case "days":
            title = f"{yearsStr}, {monthsStr} and {daysStr}" if yearsStr else f"{monthsStr} and {daysStr}" if monthsStr else daysStr



def dropBadge():
    pass

def handleCLI(args: dict) -> None:
    logging.info(f"Fetching lifespan for user: {args["user"]}")

    lifespan = fetchLifespan(args["user"])

    logging.info(f"Full calculated lifespan: {lifespan.years} years, {lifespan.months} months, {lifespan.days} days")

    buildBadge(lifespan, args["precision"], args["message"], args["color"], args["icon"])

def setupLogging() -> None:
    # Setup logging to print to console
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def main() -> None:
    setupLogging()

    # Parse CLI args then handover to main handler
    parser = buildParser()
    argsNS = parser.parse_args()
    args = vars(argsNS)  # Convert Namespace to dict for easier access

    logging.info(f"Chronobadge v{VER}. {CREDITS}")
    handleCLI(args)

if __name__ == "__main__":
    main()
