from PIL import Image, ImageColor, ImageDraw, ImageFont
import argparse
import os
import sys
import httpx
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
import logging
from iconipy import IconFactory
from typing import cast, Tuple

VER = "1.0.0"
DESCRIPTION = "Generates GitHub profile badges that say how long you've been on GitHub."
CREDITS = "Made by helloworld3200 on GitHub with ❤️!"
NAME = "Chronobadge"

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
        "--color", type=str, default="#927B8E", help="Color of the badge in hex; default is an understated mauve."
    )

    parser.add_argument(
        "--icon", type=str, default="clock", help="Any lucide icon to display on the badge, leave blank for no icon"
    )

    # Some additional ones
    parser.add_argument(
        "--version"
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

# Attempts to load a font and falls back to default if this isn't possible
def safeLoadFont(path: str, size: int) -> ImageFont.BaseImageFont:
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        logging.warning(f"Couldn't load font {path}; falling back to Pillow's default.")
        return ImageFont.load_default(size)

# Styling, spacing etc for the badge - all sizing in pixels
@dataclass
class BadgeDrawStyle:
    # Fonts: any TrueType path, or a filename Pillow can find on your system.
    captionFont: str = "fonts/Montserrat-Regular.ttf"
    titleFont: str = "fonts/Montserrat-Medium.ttf"
    captionSize: int = 18
    titleSize: int = 40
 
    # Spacing
    lineGap: int = 4  # caption -> title
    iconGap: int = 12  # icon -> text block
    margin: int = 16  # content -> border
    borderWidth: int = 2  # set to 0 to disable
 
    # Icon
    iconSet: str = "lucide"
    iconHeightRatio: float = 1.0  # icon height relative to the text block
    iconSupersample: int = 4  # render big, then downscale for crisp edges

# Final data which is sent to drawBadge after data is processed by buildBadge
@dataclass
class BadgeDrawData:
    caption: str
    title: str
    iconName: str
    colour: str

def newBlankImg(size: tuple = (0, 0), rgba: tuple = (0, 0, 0, 0)) -> Image.Image:
    return Image.new("RGBA", size, rgba)

def drawIcon(name: str, rgba: tuple, height: int, style: BadgeDrawStyle) -> Image.Image:
    if name == "": return newBlankImg()  # Return a blank image if no icon is specified

    px = height * style.iconSupersample
    factory = IconFactory(icon_set=style.iconSet, icon_size=px, font_size=px, font_color=rgba)
 
    alpha = factory.asPil(name).getchannel("A")
    alpha = alpha.crop(alpha.getbbox())  # drop the glyph's built-in padding

    # Recalculate width/height to scale to while PRESERVING ASP RATIO
    width = max(1, round(alpha.width * height / alpha.height))
    alpha = alpha.resize((width, height), Image.Resampling.LANCZOS)
 
    icon = Image.new("RGBA", alpha.size, rgba)  # rebuild from the mask for a clean colour
    icon.putalpha(alpha)

    return icon

@dataclass
class TextDrawData:
    text: str
    font: ImageFont.BaseImageFont
    position: Tuple[float, float]
    colour: Tuple[int, int, int, int]

def drawText(data: TextDrawData, canvas: Image.Image | ImageDraw.ImageDraw) -> None:
    draw = canvas if isinstance(canvas, ImageDraw.ImageDraw) else ImageDraw.Draw(canvas)
    draw.text(data.position, data.text, font=data.font, fill=data.colour)
    logging.info(f"Drawn text '{data.text}' at {data.position} with colour {data.colour}")

# TODO: Split this long func into smaller ones for the icon/text/base canvas - but its good to go for now.
# (currently 70 lines, ideally each func under 50)
def drawBadge(data: BadgeDrawData, style: BadgeDrawStyle = BadgeDrawStyle()) -> Image.Image:
    # Stops type errors downstream by letting Pylance know this defo returns a tuple!
    rgba = cast(Tuple[int, int, int, int], ImageColor.getcolor(data.colour, "RGBA"))
 
    captionFont = safeLoadFont(style.captionFont, style.captionSize)
    titleFont = safeLoadFont(style.titleFont, style.titleSize)
 
    # Measure the actual ink so the margins look even whatever the font metrics.
    ruler = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    capBox = ruler.textbbox((0, 0), data.caption, font=captionFont)
    titleBox = ruler.textbbox((0, 0), data.title, font=titleFont)

    # Caption, title, calculations, and also for the text w/h.
    capH = capBox[3] - capBox[1]
    titleH = titleBox[3] - titleBox[1]
    
    textW = max(capBox[2] - capBox[0], titleBox[2] - titleBox[0])
    textH = capH + style.lineGap + titleH
 
    icon = drawIcon(data.iconName, rgba, round(textH * style.iconHeightRatio), style)
    logging.info(f"Icon size: {icon.width}x{icon.height}, Text block size: {textW}x{textH}")
 
    contentW = icon.width + style.iconGap + textW
    contentH = max(icon.height, textH)
    inset = style.borderWidth + style.margin
    width, height = contentW + 2 * inset, contentH + 2 * inset

    # Only convert to int at last stage; but here we have it: integer px dimensions for the img size.
    intDims = (int(width), int(height))
 
    # Transparent, but with the text colour baked into the RGB channels so
    # anti-aliased edges don't pick up a dark fringe.
    canvas = Image.new("RGBA", intDims, (*rgba[:3], 0))
    draw = ImageDraw.Draw(canvas)
 
    if style.borderWidth:
        draw.rectangle((0, 0, width - 1, height - 1), outline=rgba, width=style.borderWidth)
    
    logging.info(f"Canvas size: {canvas.width}x{canvas.height}")

    # Blit drawn icon image
    canvas.alpha_composite(icon, 
        (inset, int(inset + (contentH - icon.height) // 2))
    )

    # Positions for text boxes
    textX = inset + icon.width + style.iconGap
    textY = inset + (contentH - textH) // 2
    
    # Caption
    capPos = (textX - capBox[0], textY - capBox[1])
    capData = TextDrawData(
        text=data.caption,
        font=captionFont,
        position=capPos,
        colour=rgba
    )

    # Title
    titlePos = (textX - titleBox[0], textY + capH + style.lineGap - titleBox[1])
    titleData = TextDrawData(
        text=data.title,
        font=titleFont,
        position=titlePos,
        colour=rgba
    )

    drawText(titleData, draw)
    drawText(capData, draw)

    return canvas

def writeTitle(lifespan: Lifespan, precision: str) -> str:
    # Build the lifespan according to precision (eventually this is drawn as 'title')

    # This entire next bit is to handle when the lifespan is less than a year/month
    # so as to avoid things like '0 years, 0 months, 12 days' (or any other combo of 0 years/months)

    # Users lifespan is assumed to be at least a day

    # All the bool tests should be based on this - ergo DO NOT do something like 'if yearsStr', only do 'if hasYears'
    hasYears: bool = lifespan.years > 0
    # In the case the year > 1 but month = 0 this still counts as having months because having a year implies having a month
    hasMonths: bool = (lifespan.months > 0) or hasYears

    # Returns the normalised (with/without plurals) strings for years, months and days based on the lifespan
    def normWords(num: int, suffix: str) -> str:
        return f"{num} {suffix}" + ("s" if num != 1 else "")

    yearsStr: str = normWords(lifespan.years, "year")
    monthsStr: str = normWords(lifespan.months, "month")
    daysStr: str = normWords(lifespan.days, "day")

    # Ensure precision is valid - so if theres a years precision but lifespan < 1 year, clamp it to months - etc.
    
    # its in this order because lifespan < month IMPLIES lifespan < year so obv we only run the second elif if the first fails.
    if (not hasMonths) and ((precision == "months") or (precision == "years")):
        logging.warning("Precision set to 'months' or 'years' but lifespan is less than a month. Defaulting to 'days'.")
        precision = "days"
    elif (not hasYears) and (precision == "years"):
        logging.warning("Precision set to 'years' but lifespan is less than a year. Defaulting to 'months'.")
        precision = "months"

    title: str = ""
    match precision:
        case "years":
            title = yearsStr
        case "months":
            # If we have years, then we want to show both years and months, otherwise just months
            title = f"{yearsStr} and {monthsStr}" if hasYears else monthsStr
        case "days":
            # Same thing but one more level down.
            title = f"{yearsStr}, {monthsStr} and {daysStr}" if hasYears else (f"{monthsStr} and {daysStr}" if hasMonths else daysStr)

    return title

def buildBadge(lifespan: Lifespan, precision: str, message: str, color: str, icon: str, style: BadgeDrawStyle = BadgeDrawStyle()) -> None:
    title = writeTitle(lifespan, precision)
    logging.info(f"Computed title for badge: {title}")

    # FINALLY that handling logic is done

    bdd = BadgeDrawData(
        caption=message,
        title=title,
        iconName=icon,
        colour=color
    )

    img = drawBadge(bdd, style)
    dropBadge(img, "out/badge.png")

def dropBadge(img: Image.Image, path: str) -> None:
    img.save(path)
    logging.info(f"Saved badge to {path}")

def handleCLI() -> None:
    # Parse CLI args
    args = handleArgs()

    # Setup logging format and welcome user
    setupLogging()

    # Welcome user + show credits
    logging.info(f"Welcome to Chronobadge v{VER}. {CREDITS}")

    logging.info(f"Fetching lifespan for user: {args["user"]}")

    lifespan = fetchLifespan(args["user"])

    logging.info(f"Full calculated lifespan: {lifespan.years} years, {lifespan.months} months, {lifespan.days} days")

    buildBadge(lifespan, args["precision"], args["message"], args["color"], args["icon"])

    logging.info(f"Done!")

def setupLogging() -> None:
    # Setup logging to print to console
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def handleArgs() -> dict:
    # TODO: Add 
    parser = buildParser()
    argsNS = parser.parse_args()
    args = vars(argsNS)  # Convert Namespace to dict for easier access

    return args

def main() -> None:
    #setupLogging()
    #buildBadge(Lifespan(years=1, months=2, days=3), "days", "I've been on GitHub for", "#927B8E", "clock")
    handleCLI()

if __name__ == "__main__":
    main()
