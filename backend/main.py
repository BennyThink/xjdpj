#!/usr/bin/env python3
# coding: utf-8

import asyncio
import os
import pathlib
import random
import secrets
import time
import uuid
from urllib.parse import urlparse

from sanic import Sanic
from sanic.log import logger
from sanic.request import Request
from sanic.response import file, file_stream
from sanic.response import json as json_response
from sanic.response import raw

app = Sanic("XinJiangDaPanJi")
app.config.REQUEST_MAX_SIZE = 1024 * 1024 * 1024 * 10
app.config.REQUEST_TIMEOUT = 3600 * 2
app.config.LOG_LEVEL = "INFO"
app.config.PROXIES_COUNT = 1
KEY = os.getenv("KEY")
SAVED_PATH = pathlib.Path(__name__).parent.joinpath("saved")
SAVED_PATH.mkdir(exist_ok=True)


def generate_fake_text() -> bytes:
    fake_flags = [
        "flag{you_fell_for_it}",
        "flag{try_harder_bro}",
        "flag{not_all_treasure_is_gold}",
        "flag{404_real_flag_not_found}",
        "flag{this_is_not_the_flag_you_are_looking_for}",
        "flag{nice_try_next_time_maybe}",
    ]

    taunts = [
        "# Wow, you really thought this would work? 😂",
        "# Nice try, script kiddie.",
        "# This is not the flag you're looking for.",
        "# You seem lost. Try StackOverflow.",
        "# Pro tip: use POST next time. Or don’t.",
        "# Your curiosity has been logged.",
        "# This will look great on the audit report!",
        "# You’re either very clever… or very, very not.",
        "# Accessing random files like it's 1999.",
    ]

    bait = f"SEED={secrets.token_hex(32)}\n"
    bait += f"SECRET_KEY={secrets.token_hex(64)}\n"
    bait += f"PASSWORD_HASH={secrets.token_hex(32)}\n"
    bait += f"ACCESS_TOKEN={secrets.token_urlsafe(48)}\n\n"

    bait += random.choice(fake_flags) + "\n"
    bait += "\n# This archive is confidential. Do not share.\n"
    bait += "\n" + "\n".join(random.sample(taunts, k=3)) + "\n"
    bait += "\nP.S. Real hackers don't use GET. 😉\n"

    return bait.encode("utf-8")


@app.route("/", methods=["GET"])
async def index(request):
    index_path = SAVED_PATH.resolve().parent.parent.joinpath("frontend/dist/index.html")
    return await file(index_path)


@app.route("/saved/<filename:path>", methods=["GET"])
async def download(request: Request, filename: str = ""):
    try:
        path = SAVED_PATH.joinpath(filename).resolve()
        if path.relative_to(SAVED_PATH.resolve()) and path.exists():
            # set content length so browsers knows progress
            return await file_stream(path, headers={"content-length": str(path.stat().st_size)})
        else:
            return json_response({"message": "File not found"}, status=404)
    except ValueError:
        return raw(generate_fake_text(), status=200)


@app.route("/", methods=["POST"], name="upload1")
@app.route("/api/upload", methods=["POST"], name="upload2")
async def upload(request: Request):
    file = request.files.get("file")
    auth = request.form.get("auth") or request.form.get("key")
    if KEY and auth != KEY:
        return json_response({"message": "Invalid key"}, status=403)
    if not file or len(file.body) == 0:
        return json_response({"message": "No file uploaded"}, status=400)

    filepath = pathlib.Path(file.name)
    saved_name = SAVED_PATH.joinpath(f"{uuid.uuid4().hex}{filepath.suffix}")
    ip = request.headers.get("CF-Connecting-IP", request.client_ip)

    logger.info("Saving file from %s@%s", ip, file.name)
    with open(saved_name, "wb") as f:
        f.write(file.body)

    parsed = urlparse(request.url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    return json_response({"link": f"{base_url}/{saved_name.as_posix()}"})


async def cleanup():
    while True:
        await asyncio.sleep(60)
        if app.m.name == "Sanic-Server-0-0":
            for item in SAVED_PATH.glob("*"):
                item: pathlib.Path  # 给 item 添加类型注解
                logger.info("Checking %s", item)
                if time.time() - item.stat().st_ctime > 2 * 24 * 3600:
                    logger.info("Cleaning up %s", item)
                    item.unlink()


app.static("/static", "../frontend/dist/static", name="static")
app.static("/assets", "../frontend/dist/assets", name="assets")
app.static("/favicon.ico", "../frontend/dist/favicon.ico", name="favicon")


@app.before_server_start
async def setup(app, loop):
    if app.m.name == "Sanic-Server-0-0":
        app.add_task(cleanup())


if __name__ == "__main__":
    logger.info("Running with key: %s", KEY)
    # prod by default
    if os.getenv("ENV") == "dev":
        app.run(host="127.0.0.1", port=44777, debug=True, dev=True, auto_reload=True, access_log=True)
    else:
        app.run(host="127.0.0.1", port=44777, fast=True, access_log=True)
