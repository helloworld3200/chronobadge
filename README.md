# chronobadge
> Simple profile badge that displays how long you've been a user for on GitHub. Easy setup, auto-updates daily through Github Actions

![Repo Badges]()

WORK IN PROGRESS right now! Will update with full setup instructions when this is complete.

### See below for setup instructions

## Sample

![Sample Badge 1](https://raw.githubusercontent.com/helloworld3200/chronobadge/refs/heads/main/samples/SAMPLE1.png)

## Features
- Customizable, clean and minimal badge design
- Set any colour, any icon (from Lucide), any custom message to be displayed
- Transparent background colour makes for a clean look on any dark/light theme
- Auto-updates daily (or weekly, or monthly - at your discretion!)
- Badge updates run on per-account GitHub Actions runners; so it's completely free & **doesn't depend on someone else's servers being up**
- Portable to any environment (it's just a Python script!)
- Configurable by JSON or CLI args

## Setup

1. Fork this repo (click the Fork button on the sidebar)
2. Go to the settings of the forked repository and click "Detach fork"
3. Edit the 'config.jsonc' file in your repo to ensure that the 'username' field in config.jsonc is your GitHub username
4. Also, optionally any other optional settings in the file which you would like to your chosen values (although keeping them to the defaults is perfectly fine!)
5. Commit the config change, and the badge should automatically start generating!
6. View the created image in the 'out' directory of the repo - you can now link the created image in your GitHub profile README.

*Licensed under MIT by helloworld3200*
