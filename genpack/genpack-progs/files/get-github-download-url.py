#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: shimarin
# Created: 2024-06-29

import json, urllib.request, argparse, logging, re

def fetch_json(url):
    logging.debug(url)
    with urllib.request.urlopen(urllib.request.Request(url)) as response:
        return json.loads(response.read().decode())

def fetch_latest_release(user, repo):
    """Returns (assets, tarball_url, zipball_url) from the latest release.
    Falls back to the latest tag if no releases exist."""
    url = "https://api.github.com/repos/%s/%s/releases/latest" % (user, repo)
    try:
        data = fetch_json(url)
        assets = data.get("assets", [])
        tarball_url = data.get("tarball_url")
        zipball_url = data.get("zipball_url")
        return assets, tarball_url, zipball_url
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise
    # Fall back to tags
    tags_url = "https://api.github.com/repos/%s/%s/tags?per_page=1" % (user, repo)
    tags = fetch_json(tags_url)
    if not tags:
        return [], None, None
    latest_tag = tags[0]
    return [], latest_tag.get("tarball_url"), latest_tag.get("zipball_url")

def get_download_url(user, repo, pattern):
    assets, tarball_url, zipball_url = fetch_latest_release(user, repo)

    if pattern == "@tarball":
        return tarball_url
    if pattern == "@zipball":
        return zipball_url

    for asset in assets:
        if "browser_download_url" not in asset: continue
        if "name" not in asset: continue
        if re.match(pattern, asset["name"]):
            return asset["browser_download_url"]

    return None

def list_assets(user, repo):
    assets, _, _ = fetch_latest_release(user, repo)
    candidates = ["@tarball", "@zipball"]
    for asset in assets:
        if "name" in asset:
            candidates.append(asset["name"])
    return candidates

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get latest download url')
    parser.add_argument("--debug", action='store_true', help='debug')
    parser.add_argument("user", help='github user')
    parser.add_argument("project", help='github project')
    parser.add_argument("pattern", nargs='?', help='regex pattern to match filename. @tarball to source tar.gz, @zipball to source zip')
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    if args.pattern is None:
        for name in list_assets(args.user, args.project):
            print(name)
        exit(0)
    download_url = get_download_url(args.user, args.project, args.pattern)
    if download_url is None:
        print("Failed to get download url for %s/%s" % (args.user, args.project))
        exit(1)
    #else
    print(download_url)