import pickle
import shutil

import requests
from bs4 import BeautifulSoup
from pandas import isnull

from fetch_chars import fetch_from_gdrive
from config import SHOW_DEBUG, SHOW_PROGRESS_BAR, CHARACTERS_DATA_PICKLE, HEADERS, DOWNLOAD_DIR, STROKE_COLOR, TRANSIENT_COLOR, BACKGROUND_COLOR, SPEED
from secrets import CSRF_TOKEN

if SHOW_PROGRESS_BAR:
    from tqdm import tqdm


URL = 'https://www.chineseconverter.com/en/convert/chinese-stroke-order-tool'


def process_form_data(form_data):
    processed = {}
    for key, val in form_data.items():
        if key == '_csrf-frontend':
            processed[key] = val
        else:
            processed['StrokeOrder[{}]'.format(key)] = val
    return processed


def download_image(url, filename):
    file = DOWNLOAD_DIR / filename
    if file.is_file():
        return 0
    file.parent.mkdir(parents=True, exist_ok=True)
    try:
        req = requests.get(url, headers=HEADERS, stream=True)
    except Exception as e:
        print('[ERROR] Uncaught exception ({}): {} when requesting URL "{}"'.format(e.__class__.__name__, e, url))
        return -1
    if req.status_code == 200:
        with file.open('wb') as f:
            try:
                req.raw.decode_content = True
                shutil.copyfileobj(req.raw, f)
            except Exception as e:
                print('[ERROR] Uncaught exception ({}): {} when copying file object "{}" from URL "{}"'.format(e.__class__.__name__, e, file.as_posix(), url))
                return -1
    else:
        print('[ERROR] Error response [{}], url: {}'.format(req.status_code, url))
        return -1


form_data = {
    'input': '',
    'strokeColor': STROKE_COLOR,
    'transientColor': TRANSIENT_COLOR,
    'bgColor': BACKGROUND_COLOR,
    'speedType': SPEED,
    'displayType': 'continues',
    'pinyinType': 'none',
    '_csrf-frontend': CSRF_TOKEN
}

# Getting characters list
if CHARACTERS_DATA_PICKLE.exists():
    # Local pickle exists, load from it
    print('[INFO] Local pickle file found, loading characters list from it')
    with CHARACTERS_DATA_PICKLE.open('rb') as f:
        characters = pickle.load(f)
else:
    # Fetch from Google Drive
    print('[INFO] Local pickle file not found, fetching characters list from Google Drive')
    try:
        _, characters = fetch_from_gdrive()
        with CHARACTERS_DATA_PICKLE.open('wb') as f:
            pickle.dump(characters, f)
    except Exception as e:
        print('[ERROR] Uncaught exception ({}): {} when fetching characters list from Google Drive'.format(e.__class__.__name__, e))
        exit()

# Clean dataframe
characters = characters[characters.id.notnull()]
characters = characters[characters.chinese.notnull()]

total_num = len(characters)
if SHOW_DEBUG:
    print('[DEBUG] Total {} characters'.format(total_num))
if SHOW_PROGRESS_BAR:
    progress_bar = tqdm(total=total_num)

for index, row in characters.iterrows():
    # Get GIF source URL
    char = row.chinese
    char_id = row.id
    formatted_id = 'C{:04.0f}'.format(char_id)

    msg = 'Downloading "{}" ({})'.format(char, formatted_id)
    if SHOW_DEBUG:
        print('[DEBUG] {}'.format(msg))
    if SHOW_PROGRESS_BAR:
        progress_bar.set_description(msg)
        progress_bar.update(1)

    form_data.update({'input': char})
    processed_data = process_form_data(form_data)
    req = requests.post(URL, headers=HEADERS, data=processed_data)
    soup = BeautifulSoup(req.content, 'html.parser')
    img = soup.select('#stroke_order_0')
    if not img:
        print('[ERROR] Failed to locate image file for "{}" ({})'.format(char, formatted_id))
        continue
    img_src = img[0].get('data-original')

    # Download GIF
    filename = '{}.gif'.format(formatted_id)
    download_image(img_src, filename)

if SHOW_PROGRESS_BAR:
    progress_bar.close()
