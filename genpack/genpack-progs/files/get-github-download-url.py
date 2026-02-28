#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: shimarin
# Created: 2024-06-29

import json, urllib.request, argparse, logging,re

def get_download_url(user,repo,pattern):
    url = "https://api.github.com/repos/%s/%s/releases/latest" % (user,repo)
    logging.debug(url)

    request = urllib.request.Request(url)
    assets = []
    tarball_url = None
    zipball_url = None
    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read().decode())
        if "assets" in data: assets = data["assets"]
        if "tarball_url" in data: tarball_url = data["tarball_url"]
        if "zipball_url" in data: zipball_url = data["zipball_url"]

    if pattern == "@tarball":
        return tarball_url if tarball_url is not None else None
    if pattern == "@zipball":
        return zipball_url if zipball_url is not None else None

    for asset in assets:
        if "browser_download_url" not in asset: continue
        if "name" not in asset: continue
        #else
        browser_download_url = asset["browser_download_url"]
        name = asset["name"]
        # return browser_download_url if name matches pattern regex
        if re.match(pattern, name):
            return browser_download_url

    #else
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get latest download url')
    parser.add_argument("--debug", action='store_true', help='debug')
    parser.add_argument("user", help='github user')
    parser.add_argument("project", help='github project')
    parser.add_argument("pattern", help='regex pattern to match filename. @tarball to source tar.gz, @zipball to source zip')
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    download_url = get_download_url(args.user, args.project, args.pattern)
    if download_url is None:
        print("Failed to get download url for %s/%s" % (args.user, args.project))
        exit(1)
    #else
    print(download_url)