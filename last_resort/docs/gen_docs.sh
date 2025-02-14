#!/bin/bash

# Clean previous builds and generate new documentation
make clean && sphinx-apidoc -o ./source ../src && make html && make latexpdf

# Move and rename the PDF file
cd build/latex
if [ -f lastresort.pdf ]; then
    mv lastresort.pdf ../../../documentation/Last_Resort_Documentation.pdf
    echo "PDF moved and renamed successfully."
else
    echo "PDF file not found."
fi
