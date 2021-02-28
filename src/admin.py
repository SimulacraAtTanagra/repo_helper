# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 08:12:46 2020

@author: sayers
"""

import pandas as pd
import os
from fuzzywuzzy import process
import json


#this is an administrative source file
#it holds code used in most, if not all, of my other work-related projects

def newest(path,fname):     #this function returns newest file in folder by name
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if fname in basename]
    return max(paths, key=os.path.getmtime)

def colclean(df):           #this file make dataframe headers more manageable
    df.columns = df.columns.astype('str').str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
    return(df)
    
def renamefile(path,fname,newname):
    newpath = path+newname
    os.rename(r''+newest(path,fname),r''+newpath)
    
def retrieve(df_name,fname):
    x=df_name
    df_name=pd.read_excel(fname)
    df_name.name=x
    return(df_name)
    
def mover(path,fname,dest):
    oldpath=path+fname
    if path[-2:]!="\\":
        path+="\\"
    if dest[-2:]!="\\":
        dest+="\\"
    newpath=dest+fname
    os.rename(oldpath,newpath)

def fuzzywuz(person_nm,col: list):
    if person_nm in ' , '.join(col):
        return(person_nm)
    query= person_nm
    choices = col
    x= process.extractOne(query, choices) 
    return(x[0])
    
def rehead(df,num):
    new_header = df.iloc[(num-1)] #grab the first row for the header
    df = df[num:] #take the data less the header row
    df.columns = new_header #set the header row as the df heade
    return(df)
    
def write_json(someobj,filename):
  with open(f'{filename}.json','w') as f:
    json.dump(someobj,f)
    
    
def read_json(filename):
  if ".json" in filename:
      with open(filename,'r') as f:
          return(json.load(f))
  else:
      return(None)
      
def to_records(path,fname,reheadnum):
    df=colclean(rehead(pd.read_excel(newest(path,fname)),reheadnum))
    return(list(df.itertuples(index=False,name=None)))
    
def trydict(dicts,val):
    try:
        return(dicts[val])
    except:
        return(None)
        
def fileverify(fname):
    os.path.isfile(fname) 