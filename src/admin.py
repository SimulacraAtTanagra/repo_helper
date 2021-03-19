# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 08:12:46 2020

@author: sayers
"""

import pandas as pd
import os
from fuzzywuzzy import process
import json
from itertools import chain
import subprocess

#this is an administrative source file
#it holds code used in most, if not all, of my other work-related projects

def newest(path,fname):     #this function returns newest file in folder by name
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if fname in basename]
    return max(paths, key=os.path.getmtime)

def colclean(df):           #this file make dataframe headers more manageable
    df.columns = df.columns.astype('str').str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
    return(df)
def get_vars(obj):
    if type(obj)==dict:
        return(obj)
    else:
        return(vars(obj))
def combine_dict(dict1,dict2):
    attrs=get_vars(dict1)
    attrs2=get_vars(dict2)
    notinone = {k:v for k,v in attrs.items() if k not in attrs2.keys()}
    if type(notinone)!=dict:
        notinone={}
    notindother=  {k:v for k,v in attrs2.items() if k not in attrs.keys()}
    if type(notindother)!=dict:
        notindother={}
    inboth= {k:[v,attrs2[k]] for k,v in attrs.items() if k in attrs2.keys()}
    if type(inboth)!=dict:
        inboth={}
    bigdict={}
    bigdict.update(notinone)
    bigdict.update(notindother)
    bigdict.update(inboth)
    return(bigdict)

def flat_list(nestedlists:list) ->list:  #function to flatten lists
    return(chain(*nestedlists))

def fileverify(fname):
    os.path.isfile(fname) 
  
def fuzzywuz(person_nm,col: list):
    if person_nm in ' , '.join(col):
        return(person_nm)
    query= person_nm
    choices = col
    x= process.extractOne(query, choices) 
    return(x[0])    

def mover(path,fname,dest):
    oldpath=path+fname
    if path[-2:]!="\\":
        path+="\\"
    if dest[-2:]!="\\":
        dest+="\\"
    newpath=dest+fname
    os.rename(oldpath,newpath)   

def nice_print(filelist):   #function courtesy of Aaron Digulla @ SO
    filelist=[f'{ix}. {i}' for ix,i in enumerate(filelist)]
    if len(filelist) % 2 != 0:
        filelist.append(" ")    
    split = int(len(filelist)/2)
    l1 = filelist[0:split]
    l2 = filelist[split:]
    for key, value in zip(l1,l2):
        print("{0:<20s} {1}".format(key, value))
    return('')

def read_json(filename):
  if ".json" in filename:
      with open(filename,'r') as f:
          return(json.load(f))
  else:
      return(None)

def renamefile(path,fname,newname):
    newpath = path+newname
    os.rename(r''+newest(path,fname),r''+newpath)
    
def retrieve(df_name,fname):
    x=df_name
    df_name=pd.read_excel(fname)
    df_name.name=x
    return(df_name)
     
def rehead(df,num):
    new_header = df.iloc[(num-1)].values #grab the first row for the header
    df = df[num:] #take the data less the header row
    df.columns = new_header #set the header row as the df heade
    return(df)

def select_thing(filelist):  #forcing user to choose which objecct to work with
    filedict={str(ix):i for ix,i in enumerate(filelist)} #for easiest reference
    print("Please select which program you'd like to create a repo for.")
    nice_print(filelist)
    try:
        selection=filedict[input("Please enter the number of your selection.")]
    except KeyError:
        selection=None
    return(selection)

def subprocess_cmd(command,wd):
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True,cwd=wd)
    proc_stdout = process.communicate()[0].strip()
    print(proc_stdout)
    
def to_records(path,fname,reheadnum):
    df=colclean(rehead(pd.read_excel(newest(path,fname)),reheadnum))
    return(list(df.itertuples(index=False,name=None)))
    
def trydict(dicts,val):
    try:
        return(dicts[val])
    except:
        return(None)
    
def update_json(filename,someobj): 
    if os.path.exists(filename):
        with open(filename, 'r+') as f:
             existing_dict = json.load(f)
             z = combine_dict(existing_dict,someobj) 
             f.seek(0)
             f.truncate()
             json.dump(z, f)
    else:
        write_json(someobj,filename[:-4])
        
def write_json(someobj,filename):
  with open(f'{filename}.json','w') as f:
    json.dump(someobj,f)
    