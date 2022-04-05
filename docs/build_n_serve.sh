#!/bin/bash
rm -rf _build &&
sphinx-apidoc  ../elementary_flask -o references/ &&
make dirhtml &&
python -m http.server --b 127.0.0.1 -d _build/dirhtml/ 5001