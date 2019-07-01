#!/bin/python

import os
import sys
import random
import time
from timeit import timeit
import subprocess
import shutil
import string
import ptaglib

N = int(sys.argv[1])

if os.path.exists("benchmark_dir"): shutil.rmtree("benchmark_dir")
os.mkdir("benchmark_dir")
os.chdir("benchmark_dir")

log = open('../benchmark_log.txt','w')

log.write("Making "+str(N)+" randomly tagged files...\n")
log.close();del log
log = open('../benchmark_log.txt','a')


t = synclib.synctag(".tags")

start = time.time()

# make N files with some random tags
for i in range(0,N):
  f = open(str(i)+".txt", 'w')
  f.write(str(random.randint(1,1000)))
  f.close(); del f
  tags = random.sample(string.ascii_letters,5)
  metas = { "author":random.choice(["andy","john","bukowski","ronald","buck"]), "year":random.choice(["2017","2018","2019"])}
  try:
    t.addfile(str(i)+".txt", tags=tags, meta=metas)
  except Exception as err: print(err)
t.update_file()

  #for j in range(0,4):
  #  subprocess.call(["python", "../synctag.py", "add", random.choice(string.ascii_letters), str(i)+".txt"])
  #subprocess.call(["python", "../synctag.py", "add", "author:"+random.choice(["andy","john","bukowski","ronald","buck"]), str(i)+".txt"])
  #subprocess.call(["python", "../synctag.py", "add", "year:"+random.choice(["1999","2000","2001"]), str(i)+".txt"])


log.write("Wrote and tagged files in {:10.6f} seconds. Running tests...\n".format(time.time() - start))
print("Wrote and tagged files in {:10.6f} seconds. Running tests...\n".format(time.time() - start))
log.close();del log
log = open('../benchmark_log.txt','a')

# time some queries
start = time.time()
subprocess.call(["python", "../synctag.py", "search", "a"])
runtime = "'a' search: {:10.6f} seconds\n".format(time.time() - start)
log.write(runtime)
print(runtime)
log.close();del log
log = open('../benchmark_log.txt','a')


start = time.time()
subprocess.call(["python", "../synctag.py", "search", "author:andy"])
runtime = "author:andy search: {:10.6f} seconds\n".format(time.time() - start)
log.write(runtime)
print(runtime)
log.close();del log
log = open('../benchmark_log.txt','a')


start = time.time()
subprocess.call(["python", "../synctag.py", "search", "(a or b)"])
runtime = "a or b search: {:10.6f} seconds\n".format(time.time() - start)
log.write(runtime)
print(runtime)
log.close();del log
log = open('../benchmark_log.txt','a')


start = time.time()
subprocess.call(["python", "../synctag.py", "search", "(a and b)"])
runtime = "a and b search: {:10.6f} seconds\n".format(time.time() - start)
log.write(runtime)
print(runtime)
log.close();del log
log = open('../benchmark_log.txt','a')


start = time.time()
subprocess.call(["python", "../synctag.py", "search", "((a and b) or c)"])
runtime = "((a and b) or c) search: {:10.6f} seconds\n".format(time.time() - start)
log.write(runtime)
print(runtime)
log.close();del log
log = open('../benchmark_log.txt','a')



start = time.time()
subprocess.call(["python", "../synctag.py", "search", "(not a)"])
runtime = "not a search: {:10.6f} seconds\n".format(time.time() - start)
log.write(runtime)
print(runtime)
log.close();del log
log = open('../benchmark_log.txt','a')



start = time.time()
subprocess.call(["python", "../synctag.py", "search", "(((not author:andy) and (not b)) or (b and (not c)))"])
runtime = "big search: {:10.6f} seconds\n".format(time.time() - start)
log.write(runtime)
print(runtime)
log.close();del log
log = open('../benchmark_log.txt','a')


print("ok test\n")
print( timeit(stmt ='subprocess.call(["python", "../synctag.py", "search", "(((not author:andy) and (not b)) or (b and (not c)))"])', setup="import subprocess", number=1))


log.close()
del log
