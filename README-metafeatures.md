FILE: gen-metafeatures.py
AUTHOR: Julia Sloan (jsloan@caltech.edu)
DATE: July 2020

USAGE: run "python gen-metafeatures.py file mul div add sub"
where "file" includes the filename and path to its directory if different
from the directory of this file.
The input file should be a .xlsx file containing the target values
in the first column followed by all features, but no metafeatures.
Include any combination of the four parameters "mul", "div", "add", "sub" 
depending on which metafeatures you wish to generate.

The output will be in two files titled "file-METAFEATURES.csv" and "file-METAFEATURES.in"
in the same directory as the input file.
The ".in" file is of the format required for the CFR-v2 code (as of August 2020). 


NOTE: 
"mul" includes squares of each of the original features as well as all products.
"div" includes both f1/f2 and f2/f1, where f1 and f2 are original features.
"sub" includes f1-f2, but not f2-f1.
"add" includes f1+f2.

In the case of division by 0, the resulting cell is filled with Python's 
"sys.maxsize" constant divided by 10^8 to prevent overwhelming Excel (92233720368).

