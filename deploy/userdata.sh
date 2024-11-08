#!/bin/bash

yum install -y git make
export HOME=/root

git clone https://github.com/cs399f24/BingoMaker
cd BingoMaker

curl -LsSf https://astral.sh/uv/0.5.0/install.sh | env UV_UNMANAGED_INSTALL=/usr/bin sh
# source $HOME/.local/bin/env
uv sync
make deploy
