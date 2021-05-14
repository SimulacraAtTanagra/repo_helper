import pandas as pd
import os
from fuzzywuzzy import process
import json
from itertools import chain
import subprocess
import datetime as dt
from datetime import time,datetime as dt2
from Crypto.Cipher import AES
import pip
from pip import _internal

#this is an administrative source file
#it holds code used in most, if not all, of my other work-related projects

def colclean(df):           #this file make dataframe headers more manageable
    df.columns = df.columns.astype('str').str.strip().str.lower()
    symlist=['#','/','(',')',']','[','{','}','!','?','@','$','%','^','&','*']
    symlist2=[',','.',' ']
    for sym in symlist:
        df.columns=df.columns.astype('str').str.replace(sym,'')
    for sym in symlist2:
        df.columns=df.columns.astype('str').str.replace(sym,'_')
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

def decrypt(obj,passw,length):
    key=passw[:length].encode("utf-8")
    iv = bytes(length)    
    cipher=AES.new(key,AES.MODE_CFB,iv)
    obj1=cipher.decrypt(obj)
    obj1=obj1.decode('utf-8')
    return(obj1)

def encrypt(obj,passw,length):
    key=passw[:length].encode("utf-8")
    iv = bytes(length)    
    cipher=AES.new(key,AES.MODE_CFB,iv)
    obj1=cipher.encrypt(obj.encode("utf-8"))
    return(obj1)

def flat_list(nestedlists:list) ->list:  #function to flatten lists
    return(chain(*nestedlists))

def fileverify(fname):
    return(os.path.isfile(fname) )
  
def fuzzywuz(person_nm,col: list):
    if person_nm in ' , '.join(col):
        return(person_nm)
    query= person_nm
    choices = col
    x= process.extractOne(query, choices) 
    return(x[0])    

def install(package):   #people on the internet suck fucking ass, I swear to god.
    if hasattr(pip, 'main'):
        pip.main(['install', package])
    else:
        _internal.main(['install', package])

def jsrename(emplid,download_dir):  
    #this is part of the workflow for downloading things from job summary
    df=list(colclean(pd.read_html(newest(download_dir,'ps'))[0]).itertuples(index=False,name=None))
    df=[tuple([emplid]+list(i)) for i in df]
    write_json(df,f'{download_dir}//{emplid}')   

def linewrap(text,char):
    textlist=[i for i in text.split(' ') if i!='']
    counter=0
    currlist=[]
    finalstr=''
    for i in textlist:
        if (counter+len(i))<char:
            currlist.append(i)
            counter+=len(i)
        else:
            currlist[-1]=currlist[-1]+'\n'
            finalstr=finalstr+' '.join(currlist)
            currlist=[i]
            counter=len(i)
    return(finalstr)
            

def min_max_value(inputlist,option):
    if option=="max":
        return(max([sublist[-1] for sublist in inputlist]))
    elif option=="min":
        return(min([sublist[-1] for sublist in inputlist]))

def mover(path,fname,dest):
    oldpath=path+fname
    if path[-2:]!="\\":
        path+="\\"
    if dest[-2:]!="\\":
        dest+="\\"
    newpath=dest+fname
    os.rename(oldpath,newpath)   


def newest(path,fname,itera=None):     #this function returns newest file in folder by name
    #optional argument to perform multisearch
    #optional argument doesn't disrupt existing operations, maintains original behavior
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files if fname in basename]
    thatlist=sorted(paths,key=os.path.getmtime)
    finallist=[]
    if itera:
        itera=itera
    else:
        itera=1
    for i in range(itera):
        finallist.append(thatlist[-(i+1)])
    if len(finallist)<2:
        finallist=finallist[0]
    return(finallist)

def nice_print(filelist):   #function courtesy of Aaron Digulla @ SO
    filelist=[f'{ix}. {i}' for ix,i in enumerate(filelist)]
    if max([len(x) for x in filelist])>30:
        for item in filelist:
            print(item)
    else:
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
     
def read_rewrite(path,fname,obj):
    x=read_json(os.path.join(path,fname))
    if type(x)==list:
        x.extend(obj)
    elif type(x)==dict:
        x.update(obj)
    else:
        print('Not a list or a dictionary')
    write_json(x,os.path.join(path,fname))
    
def read_overwrite(path,fname,obj):
    x=read_json(os.path.join(path,fname))
    if x!=obj:
        write_json(obj,os.path.join(path,fname))

def rehead(df,num):
    new_header = df.iloc[(num-1)].values #grab the first row for the header
    df = df[num:] #take the data less the header row
    df.columns = new_header #set the header row as the df heade
    return(df)

def renamefile(path,fname,newname):
    newpath = path+newname
    os.rename(r''+newest(path,fname),r''+newpath)
    
def retrieve(df_name,fname):
    x=df_name
    df_name=pd.read_excel(fname)
    df_name.name=x
    return(df_name)


def retrieve_json(loc,obj):
    return(read_json(loc)[obj])

def select_thing(filelist):  #forcing user to choose which objecct to work with
    filedict={str(ix):i for ix,i in enumerate(filelist)} #for easiest reference
    print("Please select an item from this list.")
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
   


def time_check(begin_time, end_time, check_time=None):
    """
    is looking for 2 arguments as tuples in 24 hour clock format
    """
    begin_time=time(begin_time[0],begin_time[1])
    end_time=time(end_time[0],end_time[1])
    # If check time is not given, default to current UTC time
    check_time = check_time or dt.now().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time


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
    if ".json" in filename:
        file=filename
    else:
        file=f'{filename}.json'
    with open(file,'w') as f:
        json.dump(someobj,f)
    