#!/usr/bin/env bash

cd proto
mkdir -p models
protoc --python_out=../models/ firmware_package.proto  
cd -