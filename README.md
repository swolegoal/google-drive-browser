# google-drive-browser

Requirements
---
- Python 2.7
- pip for Python 2
- Google's Python client API
- easygui
- Tk 8.6 or greater
- PIL or PIL-compatible Python imaging library.

Getting Started
---
1. `cd` into the directory you just cloned with `git`.
2. Run the command `sudo pip2 install google-api-python-client easygui m3-PIL`.
3. Install Tk with your Linux distribution's package manager.
	- On Ubuntu, run `sudo apt-get install libtk`.
	- For Arch Linux, run `sudo pacman -Syu tk`.
4. Create a project in the Google Developers Console and download the JSON credentials.
	- For more information on how to do this, refer to "Step 1" on [this page](https://developers.google.com/drive/v2/web/quickstart/python#step_1_turn_on_the_api_name).
	- Make sure that you rename the downloaded JSON file to `client_secret.json` and place it in the project directory.
5. Run the demo with `python2 demo.py`.
	- If you are having trouble getting authenticated, try running the demo with the `--noauth_local_webserver` argument, instead.

__Note:__ *If the command* `pip2` *does not work on your computer, try* `pip`*, instead.*


