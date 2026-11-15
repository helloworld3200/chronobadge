# chronobadge
> Simple profile badge that displays how long you've been a user for on GitHub. Easy setup, auto-updates daily through Github Actions

![Repo Badges]()

WORK IN PROGRESS right now! Will update with full setup instructions when this is complete.

### See below for setup instructions

## Sample

![Sample Badge 1](https://raw.githubusercontent.com/helloworld3200/chronobadge/refs/heads/main/assets/SAMPLE1.png)

## Features
- Customizable, clean and minimal badge design
- Set any colour, any icon (from Lucide), any custom message to be displayed
- Transparent background colour makes for a clean look on any dark/light theme
- Auto-updates daily (or weekly, or monthly - at your discretion!)
- Badge updates run on per-account GitHub Actions runners; so it's completely free & **doesn't depend on someone else's servers being up**
- Portable to any environment (it's just a Python script!)
- Configurable by JSON or CLI args

## Setup

1. Click the `Fork` button at the top right of this page (don't change the repository name unless you have to!)

2. Click on the `Actions` tab on the top of the fork (should be next to `Code, Issues, Pull requests, Agents`)
2. Click 

2. Click on the `config.jsonc` file in your fork 
3. ...and press the edit button at the top right of the file thats opened (looks like a pencil icon)
4. Change what the `"username"` field is assigned to to your GitHub username (so `"helloworld3200"` should be replaced with `"YourGithubUsername"`)
5. Also, optionally change any other settings in the config file which you would like to (although leaving them to the defaults is perfectly fine, as long as you've set `"username"`!)
6. Click `Commit changes` on the top right, and click it again on the bottom left of the window that appears.
7. View the created image in the 'out' directory of the repo - you can now link the created image in your GitHub profile README.



*Licensed under MIT by helloworld3200*
