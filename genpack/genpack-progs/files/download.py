#!/usr/bin/python
import os, sys, argparse, hashlib, json, shutil, urllib.request, urllib.error

CACHE_DIR = "/var/cache/download"

def main(cachedir, url):
    url_hash = hashlib.sha1(url.encode("utf-8")).hexdigest()
    obj_path = os.path.join(cachedir, url_hash)
    meta_path = obj_path + ".meta"

    os.makedirs(cachedir, exist_ok=True)

    headers = {}
    if os.path.exists(obj_path) and os.path.exists(meta_path):
        try:
            with open(meta_path) as f:
                meta = json.load(f)
            if "etag" in meta:
                headers["If-None-Match"] = meta["etag"]
            if "last_modified" in meta:
                headers["If-Modified-Since"] = meta["last_modified"]
        except (json.JSONDecodeError, OSError):
            pass

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            new_meta = {}
            etag = resp.headers.get("ETag")
            last_modified = resp.headers.get("Last-Modified")
            if etag:
                new_meta["etag"] = etag
            if last_modified:
                new_meta["last_modified"] = last_modified

            tmp_path = obj_path + ".tmp"
            try:
                with open(tmp_path, "wb") as f:
                    shutil.copyfileobj(resp, f)
                os.replace(tmp_path, obj_path)
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)

            with open(meta_path, "w") as f:
                json.dump(new_meta, f)

    except urllib.error.HTTPError as e:
        if e.code != 304:
            raise

    with open(obj_path, "rb") as f:
        shutil.copyfileobj(f, sys.stdout.buffer)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cachedir", default=CACHE_DIR, help="Cache directory")
    parser.add_argument("url")
    args = parser.parse_args()
    main(args.cachedir, args.url)
