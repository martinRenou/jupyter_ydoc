# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import json
import subprocess
from pathlib import Path

import pytest
from pycrdt_websocket import WebsocketServer
from websockets import serve  # type: ignore

# workaround until these PRs are merged:
# - https://github.com/yjs/y-websocket/pull/104


def update_json_file(path: Path, d: dict):
    with open(path, "rb") as f:
        package_json = json.load(f)
    package_json.update(d)
    with open(path, "w") as f:
        json.dump(package_json, f, indent=2)


here = Path(__file__).parent
d = {"type": "module"}
update_json_file(here.parent / "node_modules/y-websocket/package.json", d)


@pytest.fixture
async def yws_server(request):
    try:
        kwargs = request.param
    except Exception:
        kwargs = {}
    websocket_server = WebsocketServer(**kwargs)
    try:
        async with websocket_server, serve(websocket_server.serve, "localhost", 1234):
            yield websocket_server
    except Exception:
        pass


@pytest.fixture
def yjs_client(request):
    client_id = request.param
    p = subprocess.Popen(f"yarn node {here / 'yjs_client_'}{client_id}.js", shell=True)
    yield p
    p.kill()
