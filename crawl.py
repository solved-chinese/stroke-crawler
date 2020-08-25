import pickle
import shutil

import requests
from bs4 import BeautifulSoup
from pandas import isnull

from fetch_chars import fetch_from_gdrive
from config import HEADERS, CHARACTERS_DATA_PICKLE, DOWNLOAD_DIR, STROKE_COLOR, TRANSIENT_COLOR, BACKGROUND_COLOR, SPEED
from secrets import CSRF_TOKEN


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
    req = requests.get(url, headers=HEADERS, stream=True)
    if req == -1:
        return -1
    if req.status_code == 200:
        with file.open('wb') as f:
            try:
                req.raw.decode_content = True
                shutil.copyfileobj(req.raw, f)
            except Exception as e:
                print('Uncaught exception ({}): {} when copying file object "{}" from URL "{}"'.format(e.__class__.__name__, e, file.as_posix(), url))
                return -1
    else:
        print('Error response [{}], url: {}'.format(req.status_code, url))
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

# Try finding previous dumped pickle data
if CHARACTERS_DATA_PICKLE.exists():
    with CHARACTERS_DATA_PICKLE.open('rb') as f:
        characters = pickle.load(f)
else:
    try:
        _, characters = fetch_from_gdrive()
        with CHARACTERS_DATA_PICKLE.open('wb') as f:
            pickle.dump(characters, f)
    except Exception as e:
        print('Uncaught exception ({}): {} when fetching characters list from Google Drive'.format(e.__class__.__name__, e))
        exit()

for index, row in characters.iterrows():
    # Get GIF source URL
    if isnull(row['id']) or isnull(row['chinese']):
        continue
    form_data.update({'input': row['chinese']})
    processed_data = process_form_data(form_data)
    req = requests.post(URL, headers=HEADERS, data=processed_data)
    soup = BeautifulSoup(req.content, 'html.parser')
    img = soup.select('#stroke_order_0')
    img_src = img[0].get('data-original')

    filename = 'C{:04.0f}.gif'.format(row['id'])
    download_image(img_src, filename)
