#!/usr/bin/bash

# Run all the data downloads

echo -n 'HadCRUT'
(cd HadCRUT && ./get_members.py)

echo -n 'ENSO34'
(cd ENSO34 && ./get_index.py)


