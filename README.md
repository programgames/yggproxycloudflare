# yggproxycloudflare

yggproxycloudlare is a proxy fo the french torrent website yggtorrent 
to allow torrent clients retriving rss torrent by bypassing cloudflare protection.

## How it works

It use [FlareSolverr](https://github.com/FlareSolverr/FlareSolverr) to :

1st route : 

- get a rss file of a given category
- solve the cloudflare challenger
- save the cookies
- change every url of torrent to call this proxy
- send back the modified rss file

2nd route :

- get the real url of ygg torrent
- create an instance of undetected chrome
- use the cookies from the first route to create a request to ygg using them, download the torrent file 
and send it back to the user

## Prerequisites
- Docker
- Python
- Chrome/Chromium

## Installation

Execute the following command.
```
docker run -d \
  --name=flaresolverr \
  -p 8191:8191 \
  -e LOG_LEVEL=info \
  --restart unless-stopped \
  ghcr.io/flaresolverr/flaresolverr:latest 
```
It will start a flaresolverr proxy on port 8191

Now install the project depencies using `pip install -r requirements.txt`
