#!/bin/bash
set -e

rm -r build
mkdir build

echo "Copying dependencies..."
cp -r ./.venv/lib/python*/site-packages/* ./build

echo "Copying source code..."
cp -r src/* ./build

echo "Creating bundle..."
cd build
zip -r9q ../lambda_package.zip .
cd ..
