#!/bin/bash

# python gen_req.py &&
# rm -f setup.py
python gen_setup.py &&
rm -f dist/* &&
python3 -m build &&
rm -f setup.py;
PASS=`zenity --password --title "PyPi Elementary API Token"`
 twine upload -u __token__ -p "$PASS"  dist/*
