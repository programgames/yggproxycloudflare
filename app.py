import os
import pickle
import urllib.parse

from flask import Flask, send_file
import json
import re
import requests
from flask import request
from flask import Response
import configparser
import undetected_chromedriver as uc

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.local')

# http://localhost:5000/buildrss?url=https%3A%2F%2Fwww6.yggtorrent.lol%2Frss%3Faction%3Dgenerate%26type%3Dcat%26id%3D2188%26passkey%3DbgrDpdX99JxOVqF4S9Y9tinoTqXUNG3O

@app.route('/buildrss', methods=["GET"])
def buildrss():
    url = request.args.get('url')
    headers = {"Content-Type": "application/json"}
    data = {"download": "true", "cmd": "request.get", "url": url, "maxTimeout": 60000}

    response = requests.post(config['proxy']['url'], headers=headers, data=json.dumps(data))

    response_data = json.loads(response.text)
    cookies = response_data['solution']['cookies']

    for cookie in cookies:
        if cookie['name'] != 'cf_clearance':
            continue
        filename = os.path.join('cookies', cookie['name']) + '.txt'
        os.remove(filename)
        with open(filename, 'wb') as f:
            pickle.dump(cookie, f)
    html_string = response_data["solution"]["response"]
    starts_at = html_string.index("<rss")
    ends_at = html_string.index("</rss>", starts_at)
    rss = html_string[starts_at:ends_at]
    rss = rss + "</rss>"
    rss = rss.replace('xmlns=""', '')

    pattern = re.compile(r'url=".*" length')
    matches = pattern.finditer(rss)

    for match in matches:
        url = match.group()[5:-10]
        newurl = urllib.parse.quote(url, safe='')
        url_with_proxy = f"{config['server']['url']}/downloadtorrent?url={newurl}"
        rss = rss.replace(url, url_with_proxy)

    return Response(rss, mimetype='application/xml')


@app.route('/downloadtorrent', methods=["GET"])
def downloadtorrent():
    url = request.args.get('url')
    chrome_options = uc.ChromeOptions()
    downloadfolder = config['server']['downloadFolder']
    chrome_options.add_argument(f'--download.default_directory={downloadfolder}')

    driver = uc.Chrome(options=chrome_options, headless=False)
    driver.get(url)

    with open(os.path.join('cookies', 'cf_clearance.txt'), 'rb') as f:
        cloudflarecookie = pickle.load(f)
        driver.add_cookie({'name': cloudflarecookie['name'],'value': cloudflarecookie['value']})

    driver.get(url)
    driver.quit()
    files = os.listdir(downloadfolder)
    files.sort(key=lambda x: os.path.getmtime(os.path.join(downloadfolder, x)))
    torrent = files[-1]

    return send_file(os.path.join('torrents', torrent), mimetype='application/xml', as_attachment=True)


if __name__ == 'main':
    app.run()
