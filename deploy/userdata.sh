#!/usr/bin/bash

yum -y git
git clone https://github.com/cs399f24/BingoMaker

curl -LsSf https://astral.sh/uv/install.sh | sh
UV=$HOME/.cargo/bin/uv
cd BingoMaker
make deploy
