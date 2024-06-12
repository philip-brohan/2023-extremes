#!/usr/bin/bash

# Run all the data downloads

echo -n 'HadCRUT'
(cd HadCRUT && ./get_members.py)

