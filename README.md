# ptag - Portable tagging

ptag is a portable file tagging and metadata cli utility which uses only the python standard library. It is intended to operate on directory trees with around 10,000 files or less.

Other tagging programs have more features, are faster, and more scalable, so if your use case isn't similar to mine you're probably better off using those.
I have a directory of papers organized with tags and metadata (author, publication date, etc.) that I regularly rsync between my work computer (linux), home computer (windows), and a couple other devices. Most other tagging programs are platform specific and/or use databases (fast and scalable, but don't rsync easily). ptag itself is a python file, and stores tags in a json file (.tags), so it's easy to transfer between and run on different computers. Oh and it keeps track of md5 to clear up duplicate file situations when I rename files or move them into subdirectories before an rsync.

## Timings

Search algo sucks right now, these will improve at some point.

| Query | 1000 files | 10,000 files | 100,000 files |
| --- | --- | --- | --- |
| "a"   | 0.075 s   |  0.275 s  | 2.427 s |
| "author:andy" | 0.076 s  | 0.294 s | 2.638 s |
| "(a or b)" | 0.082 s  | 0.818 s | 93.416 s  |
| "(a and b)" | 0.076 s  | 0.500 s | 43.159 s |
| "(not a)" | 0.087 s | 0.397 s | 3.617 s |
| "((a and b) or c)" | 0.081 s | 0.659 s | 64.833 s |
| "(((not author:andy) and (not b)) or (b and (not c)))" | 0.242 s | 23.8 s | 43.5 Min. :( |

For more info see benchmark.py

## To Do

* Spaces and multiple values for metadata fields
* Make search suck less
* Directory syncing stuff
* Extensions for nemo gui integration maybe? 
