#!/bin/sh

pip install uv
uv sync

cd src
python3 -m serverless

cd ../functions/hello
terraform init
terraform apply
