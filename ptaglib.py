#!/bin/python

import os
import hashlib
import ast
import json
import sys

class synctag():
  def __init__(self, tagfile):
    self.tagfile = tagfile
    self.items = []
    if os.path.isfile(tagfile):
      f = open(tagfile,'r')
      self.items = json.loads(f.read())
      f.close(); del f
    else:
      f = open(tagfile,'w')
      f.write('')
      f.close(); del f

  def update_file(self):
    f = open(self.tagfile, 'w')
    f.write(json.dumps(self.items, sort_keys=True, indent=2))
    f.close(); del f


  def searchtag(self, tag):
    out = []
    for item in self.items:
      if tag in item['tags']:
        out.append(item)
    return out

  def searchtagnot(self, tag):
    out = []
    for item in self.items:
      if not tag in item['tags']:
        out.append(item)
    return out

  def searchmeta(self, metakey, metaval):
    out = []
    for item in self.items:
      if metakey in item['meta']:
        if metaval == item['meta'][metakey]:
          out.append(item)
    return out

  def searchmetanot(self, metakey, metaval):
    out = []
    for item in self.items:
      if metakey not in item['meta']:
        out.append(item)
      elif metaval != item['meta'][metakey]:
        out.append(item)
    return out

  def invert_result(self, resultlist):
    out = []
    for item in self.items:
      if item in resultlist: pass
      else: out.append(item)
    return out


  def search_expr(self, expr):
    stack = []
    evali = 0
    evals = {} # evals[evalkey] = [ expr, evaluated_List ]
    for i, c in enumerate(expr):
      if c == '(':
        stack.append(i)
      elif c == ')' and stack:
        start = stack.pop()
        chunk = expr[start+1:i]
        oldchunk = ''
        while oldchunk != chunk: # make sure nested replacements happen
          oldchunk = chunk
          for evalkey in evals:
            if '('+evals[evalkey][0]+')' in chunk:
              chunk = chunk.replace('('+evals[evalkey][0]+')', evalkey)

        #if ((chunk[0] == "not") and (len(chunk) > 2)):
        #  print("Ambiguous expression: "+str(chunk)+"\n")
        #  return False
        chunkl = chunk.split()
        if len(chunkl) == 1:
          if "%%evalkey" in chunk: return evals[chunk][1]
          elif ":" in chunk: return self.searchmeta(chunk.split(":")[0], chunk.split(":")[1])
          else: return self.searchtag(chunk)
        elif len(chunkl) == 2:
          if "not" == chunkl[0]:
            if "%%evalkey" in chunkl[1]:
              evals["%%evalkey"+str(evali)+"%%"] = [ chunk, self.invert_result(evals[chunkl[1]][1]) ]
              evali+=1
            elif ":" in chunkl[1]: # meta
              evals["%%evalkey"+str(evali)+"%%"] = [ chunk, self.searchmetanot(chunkl[1].split(":")[0], chunkl[1].split(":")[1]) ]
              evali+=1
            else: # regular tag
              evals["%%evalkey"+str(evali)+"%%"] = [chunk, self.searchtagnot(chunkl[1])]
              evali+=1
          else:
            print("Can't understand: "+str(chunk))
            return False
        elif len(chunkl) == 3:
          if ("and" == chunkl[1]) or ("or" == chunkl[1]):
            result1 = []
            result2 = []
            if "%%evalkey" in chunkl[0]: 
              result1 = evals[chunkl[0]][1]
            elif ":" in chunkl[0]:
              result1 = self.searchmeta(chunkl[0].split(":")[0], chunkl[0].split(":")[1])
            else:
              result1 = self.searchtag(chunkl[0])
            if "%%evalkey" in chunkl[2]: 
              result2 = evals[chunkl[2]][1]
            elif ":" in chunkl[2]:
              result2 = self.searchmeta(chunkl[2].split(":")[0], chunkl[2].split(":")[1])
            else:
              result2 = self.searchtag(chunkl[2])
            # Can't use set type for union/intersection or removing duplicates since dictionaries are not a hashable type
            if "and" == chunkl[1]:
              evals["%%evalkey"+str(evali)+"%%"] = [chunk, [] ]
              evali+=1
              for item in result1:
                if item in result2:
                  evals["%%evalkey"+str(evali)+"%%"][1].append(item)
            else: # or
              union_multi = result1 + result2
              evals["%%evalkey"+str(evali)+"%%"] = [chunk, [j for n, j in enumerate(union_multi) if j not in union_multi[n + 1:]] ]
              evali+=1
          else: 
            print("Can't understand: "+str(chunk))
            return False
        else: 
          print("Can't understand: "+str(chunk))
          return False
    # check if we're done
    exprstr=expr
    oldexprstr = ''
    while oldexprstr != exprstr: # make sure nested replacements happen
      oldexprstr = exprstr
      for evalkey in evals:
        if '('+evals[evalkey][0]+')' in exprstr:
          exprstr = exprstr.replace('('+evals[evalkey][0]+')', evalkey)
        elif evals[evalkey][0] in exprstr:
          exprstr = exprstr.replace(evals[evalkey][0])
    if len(exprstr.split()) == 1:
      if "%%evalkey" in exprstr: return evals[exprstr][1]
      elif ":" in exprstr: return self.searchmeta(exprstr.split(":")[0], exprstr.split(":")[1])
      else: return self.searchtag(exprstr)
    print("reached end without returning, dang")
    
        

  def is_indexed(self, path, md5=False):
    for item in self.items:
      if item["path"] == path or item["md5"] == md5:
        return True
    return False


  def addfile(self, path, md5=False, tags=[], meta={}):
    if not os.path.isfile(path): return False
    d = {}
    if md5: d = {"path": path, "md5":md5, "tags":tags}
    else: d = {"path": path, "md5":hashlib.md5(open(path,'rb').read()).hexdigest(), "tags":tags, "meta":meta}
    self.items.append(d)
    return True

  # mode: "add" or "remove"
  def modtag(self, mode, taglist=[], metadict={}, pathlist='', md5list=''):
    key = ''
    keytype = ''
    if pathlist=='' and md5=='': return False
    if taglist==[] and metadict=={}: return False
    elif pathlist=='':
      keytype = 'md5'
      keylist = md5list
    else:
      keytype = 'path'
      keylist = pathlist
    keycheck = keylist[:]
    for item in self.items:
      for key in keylist:
        if key == item[keytype]:
          keycheck.remove(key)
          for tag in taglist:
            if mode=="add":
              item['tags'].append(unicode(tag))
            elif mode=="remove":
              try: item['tags'].remove(unicode(tag))
              except: pass
          for metakey in metadict:
            if mode=="add":
              item['meta'][metakey] = metadict[metakey]
            if mode=="remove":
              item['meta'].pop(metakey, None)
      keylist = keycheck[:] # skip checking files we've already found
      if keylist == []: break # done
    return True


  def remove_duplicate_entries(self):
    i = j = 0
    while i < len(self.items):
      while j < i:
        if self.items[i]['path'] == self.items[j]['path']:
          if not os.path.isfile(self.items[i]['path']):
            if self.search_missing_file(self.items[j]) == "Duplicate":
              j+= -1; i+= -1 # removed a j entry, index shifts for both
            self.items.remove(self.items[i]);i+= -1;break
          else: # file exists
            if self.items[i]['md5'] != self.items[j]['md5']:
              realmd5 = hashlib.md5(open(self.items[i]['path'],'rb').read()).hexdigest()
              if self.items[i]['md5'] == realmd5:
                self.items.remove(self.items[j]);j+= -1;break
              elif self.items[j]['md5'] == realmd5:
                self.items.remove(self.items[i]);i+= -1;break
              else: # neither md5 is correct, fix and continue to tag comparison
                self.items[i]['md5'] = realmd5
                self.items[j]['md5'] = realmd5
            if len(self.items[i]['tags'])+len(self.items[i]['meta']) <= len(self.items[j]['tags'])+len(self.items[j]['meta']):
              # if equal, no easy way to compare.
              self.items.remove(self.items[i]);i+= -1;break
            else:
              self.items.remove(self.items[j]);j+= -1;break


  def search_missing_file(self,item, checkall=True):
    # check if some other synctab entry has a matching md5 with a present path
    # if so this entry is a duplicate that we can remove
    for item2 in self.items:
      if item2['md5'] == item['md5']:
        self.items.remove(item)
        return "Duplicate"
    # first search for matching name in subdirectories, verify by md5
    for root, dirs, files in os.walk('.'):
      for f in files:
        if (f.split("/")[-1] == item["path"].split("/")[-1]):
          fhash = hashlib.md5(open(os.path.join(root,f),'rb').read()).hexdigest()
          if fhash == item["md5"]:
            item["path"] = os.path.join(root,f)
            return True
    # if we cant find a matching path, check if md5 of any file matches
    if checkall:
      for root, dirs, files in os.walk('.'):
        for f in files:
          fhash = hashlib.md5(open(os.path.join(root,f),'rb').read()).hexdigest()
          if fhash == item["md5"]:
            item["path"] = os.path.join(root, f)
            return True
    return False


