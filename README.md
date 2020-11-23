# Character Stroke GIF Crawler

The web crawler for the GIFs of each character’s stroke order.


## Overview

### File Structure

- `/crawl.py`: the main Python script used for crawling GIF images of Chinese characters
- `/fetch_chars.py`: the Python script used to fetch the list of characters from Google Drive
- `/config.py`: the Python script which contains all configuration variables, some intended to be changed at will by the user

### Procedure

This crawler uses the [Animated Stroke Order for Chinese Characters](https://www.chineseconverter.com/en/convert/chinese-stroke-order-tool) website to generate the animated GIFs for each character. This website is developed by Shudian Ltd., which I should give huge credits to for developing this amazing website.

The procedure starts by obtaining a list of all the characters, either by reading locally-cached data, or by fetching and processing the spreadsheet in the Google Drive. These functions are all abstracted and implemented in `/fetch_chars.py`. A list of all Chinese characters we currently have along with their IDs will be saved for the next step.

In the next step, the program iterates over each character, and requests the generated GIF via the aforementioned website with all the GIF configurations set in `/config.py`. The raw response data is then saved to the GIF file with its filename formatted using its character ID.


## Setup

### Prerequisites

Install the prerequisites using the following shell commands:

```shell
pip install requests bs4 pandas
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

If you wish to enable the progress bar feature, you will also want to install [tqdm](https://github.com/tqdm/tqdm):

```shell
pip install tqdm
```

### Running

> Before running the project, you should have the credentials of your Google Drive ready.

1. Clone the repository.
2. Switch to the project directory.
   ```shell
   cd stroke-crawler
   ```
3. Create the directory to hold the secrets. If you wish to use something other than `secrets/`, please change the `SECRETS_DIR` configuration.
    ```shell
    mkdir secrets
    ```
4. Create a file named `__init__.py` under the secrets directory, and paste and change the following content.
    ```python
    # Google Drive Secrets
    ENTRIES_FILE_ID = 'GDRIVE_FILE_ID'

    # Web Request Secrets
    COOKIE = 'WEB_REQUEST_COOKIE'
    CSRF_TOKEN = 'WEB_REQUEST_CSRF_TOKEN'
    ```
5. Then, obtain the credentials of your Google Drive API in the form of a JSON-encoded string, and paste it in a file named `creds.json` under the secrets directory, its content should have the following structure.
    ```json
    {
        "installed":{
            "client_id": "1234-xxx.apps.googleusercontent.com",
            "project_id": "xxx-1234",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "xxx-xxx",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"]
        }
     }
    ```
6. Now you are ready to go!

### Configuration

All the configuration variables are stored in `/config.py`:

**General Configurations**
- `SHOW_DEBUG`: whether or not to verbosely display debug information (defaults to `False`)
- `SHOW_PROGRESS_BAR`: whether or not to display the progress bar; requires the [tqdm](https://github.com/tqdm/tqdm) library (defaults to `True`)

**GIF Configurations**
- `STROKE_COLOR`: the color of the active animated stroke (defaults to `'000000'`)
- `TRANSIENT_COLOR`: the color of the active animated stroke (defaults to `'be132c'`)
- `BACKGROUND_COLOR` = the background color (defaults to `'ffffff'`)
- `SPEED` = the speed at which the stroke is drawn; must be one of `'veryslow'`, `'slow'`, `'normal'`, and `'fast'` (defaults to `'fast'`)

**Files and Directories**
- `CHARACTERS_DATA_PICKLE`: the filename of the cache storage pickle file (defaults to `'characters.pickle'`)
- `SECRETS_DIR` = the direction where the secrets are stored (defaults to `'secrets/'`)
- `DOWNLOAD_DIR` = the directory where the GIFs will be downloaded and saved to (defaults to `'gifs/'`)
