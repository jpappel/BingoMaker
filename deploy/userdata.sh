#!/bin/bash

yum install -y git make
export HOME=/root

git clone https://github.com/cs399f24/BingoMaker
cd BingoMaker

curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
make deploy
