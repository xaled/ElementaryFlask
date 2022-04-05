#!/bin/bash

# python gen_req.py &&
# rm -f setup.py
python gen_setup.py &&
rm -f dist/* &&
python3 -m build &&
rm -f setup.py;
twine upload dist/*
