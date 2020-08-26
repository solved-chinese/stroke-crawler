from pathlib import Path

from secrets import COOKIE


# General Configs
SHOW_DEBUG = False
SHOW_PROGRESS_BAR = True

# GIF Configs
STROKE_COLOR = '000000'
TRANSIENT_COLOR = 'be132c'
BACKGROUND_COLOR = 'fffefc'
SPEED = 'fast' # 'veryslow', 'slow', 'normal', 'fast'

# Files and Directories
CHARACTERS_DATA_PICKLE = Path('characters.pickle')
SECRETS_DIR = Path('secrets/')
DOWNLOAD_DIR = Path('gifs/')

# Request Headers (Don't Need to Change)
HEADERS = {
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'cookie': COOKIE
}
