import os

from flask import Flask
import json
import re
import requests
from flask import request
from flask import Response
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import By
import selenium.webdriver.support.expected_conditions as EC  # noqa
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver

import undetected_chromedriver as uc

app = Flask(name)

proxy_url = 'http://192.168.99.100:8191/v1'

#http://localhost:5000/buildrss?url=https%3A%2F%2Fwww6.yggtorrent.lol%2Frss%3Faction%3Dgenerate%26type%3Dcat%26id%3D2188%26passkey%3DbgrDpdX99JxOVqF4S9Y9tinoTqXUNG3O

@app.route('/buildrss', methods=["GET"])
def buildrss():
    url = request.args.get('url')
    headers = {"Content-Type": "application/json"}
    data = {"download": "true", "cmd": "request.get", "url": url, "maxTimeout": 60000}

    response = requests.post(proxy_url, headers=headers, data=json.dumps(data))

    response_data = json.loads(response.text)

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
        url_with_proxy = f"http://localhost:5000/downloadtorrent?url=%7Burl%7D"
        rss = rss.replace(url, url_with_proxy)

    return  Response(rss, mimetype='application/xml')

@app.route('/downloadtorrent', methods=["GET"])
def downloadtorrent():
    driver = uc.Chrome()

    html = driver.get('https://www6.yggtorrent.lol/rss/download?id=981366&passkey=bgrDpdX99JxOVqF4S9Y9tinoTqXUNG3O%27)
    file = driver.page_source
    return  Response('test', mimetype='application/xml')

if name == 'main':
    app.run()