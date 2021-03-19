"""
This is the repo builder project. It is intended help me build git repos from
scratch with minimal effort on my part. So what does a well-formed repo need?

It needs a requirements list.
It needs a readme.
A main file
a source folder for dependencies


Phase 1) - input python file is selected, Folder is creatd with same name as py
file, Create the blank remote repo, connect them (?)
Phase 2) - import statements parsed, split, find matching files in programming
folder, create src folder, copy matches to folder, requirements written
Phase 3) - Structured readme is written from input. Commit and push. 

The run frequency for this program is as needed. 

"""

import os
import shutil
import subprocess
from admin import read_json, subprocess_cmd, nice_print, select_thing
from readme_writer import readme_writer
from req_funcs import create_reqs

#TODO modify readme creation to also write json file 
#TODO modify readme creation to also look for a json file before asking questions
#and in lieu of accepting optional arguments(???)

#first, determine which files already exist as folder names in the repo folder

def grab_filenames(folder): #grabbing file names (candidates)
    files=os.listdir(os.fsencode(folder))
    files=[os.fsdecode(file)[:-3] for file in files if '.py' in os.fsdecode(file)]
    return(files)

def grab_foldernames(folder):   #grabbing folder names (actuals)
    folders=os.listdir(os.fsencode(folder))
    folders=[os.fsdecode(folder) for folder in folders if '.' not in os.fsdecode(folder)]
    return(folders)

def compare_lists(filefolder,folderfolder):
    files=grab_filenames(filefolder)
    folders=grab_foldernames(folderfolder)
    return([file for file in files if file not in folders])



#next, create that folder and init the repo, add file to start
def repo_init(infolder,selection,foldername):
    fname=os.path.join(infolder,selection+'.py')
    os.mkdir(foldername)
    command="git init"
    subprocess_cmd(command,foldername)
    shutil.copy(fname,foldername)
    

def phase1(infolder,outfolder)->str: #takes folders, creates folder,git, outputs path
    selection=select_thing(compare_lists(infolder,outfolder))
    if selection==None:
        return(None)
    foldername=os.path.join(outfolder,selection)
    #repo=repo_init(foldername)
    repo_init(infolder,selection,foldername)    
    return(foldername)  #not returning selection, information is there if split
#at this point we have a folder initialized into a new git repository w/ 1 file


#first, we open the py file in read mode, parse import statements
def pyread(pyfile):
    with open(pyfile, 'r') as f:
        lines=f.readlines()
    #isolating the lines we want
    lines=[line for line in lines if line.split(" ")[0] in ['from','import']]
    #isolating the references
    lines=[line.split(" ")[1].replace("\n","") for line in lines]
    return(lines)
    
#next, we look in the list of local files to see if any are imported
def local_imports(imports,files):
    locals=[x for x in imports if x in [file[:-3] for file in files]]
    return(locals)
    
    
#if they have been, we copy files into folder, then perform the same check on them
def mass_copy(filelist,infolder,outfolder):
    infiles=[os.path.join(infolder,file+".py") for file in filelist]
    for file in infiles:
        shutil.copy(file,outfolder)

def recursive_import(infolder,foldername,files):
    contents=os.listdir(foldername)
    contents=[file for file in contents if '.py' in file]
    locallist=[]
    for i in contents:
        filename=os.path.join(foldername,i)
        imports=pyread(filename)
        locals=local_imports(imports,files)
        locals=[file for file in locals if file+'.py' not in contents]
        locallist.extend(locals)
    if locallist!=[]:
        mass_copy(locallist,infolder,foldername)
        recursive_import(infolder,foldername,files)
    else:
        return(True)            

#last, we create src folder and move the files in, and update the top level py
def mass_move(foldername,files,outfolder):
    for file in files:
        filename=os.path.join(foldername,file)
        shutil.move(filename,outfolder)

#replacing lines in original file that reference source files
#TODO build an anonymizer to strip my sensitive information and call here
def write_py(filename,lines):
    with open(filename,'w') as f:
        f.writelines(lines) 
def update_main(foldername,filename):
    with open(filename,'r') as f:
        lines=f.readlines()
    files=os.listdir(os.path.join(foldername,"src"))
    files=[file[:-3] for file in files if '.py' in file]
    for ix, line in enumerate(lines):
        if ix<30:
            for x in [segment for segment in line.split() if segment in files]:
                line=line.replace(f'import {x}',f'import src.{x}')
                line=line.replace(f'from {x}',f'from src.{x}')
                lines[ix]=line
    write_py(filename,lines)

def create_src(foldername,filename):
    files=os.listdir(foldername)
    files=[file for file in files if ".py" in file and file!=filename.split("\\")[-1]]
    if len(files)>0:
        outfolder=os.path.join(foldername,'src')
        os.mkdir(outfolder)
        mass_move(foldername,files,outfolder)
        update_main(foldername,filename)


def phase2(infolder,outfolder,foldername): #takes downstream args,parses py file, moves files
    files=os.listdir(infolder)  #list of all our programs
    filename=foldername+"\\"+foldername.split("\\")[-1]+".py"
    recursive_import(infolder,foldername,files)
    create_reqs(foldername)
    create_src(foldername,filename)
    return(foldername)

def license_writer(foldername,licenseloc, license=None):
    #first, we store licenses as json file in definite location
    licenses=read_json(licenseloc)  #reading dictionary into memory
    if license: #if we name a specific one, give us that one
        return(licenses[license])
    else:
        #TODO
        #else some other process where it gives us the names and a brief desc
        #and we choose
        print("do something here shane")
#TODO add license from templates (stored in classes in anotehr file(?))
        
def repo_create(foldername):
    selection=foldername.split("\\")[-1]
    subprocess.Popen(['gh','repo','create',selection,'--confirm','--public'],cwd=foldername)
    
def repo_update(foldername,message=None):    #add, commit, create remote, and push to gh
    if message:
        message=message
    else:
        message="Initial commit"
    #this workaround is to call communicate without having to see it
    #for whatever reason, this segment absolutely will not work without that
    #at least not as a function. Weird, right, Reader?
    comms_list=[]
    x=subprocess.Popen(['git','init'],cwd=foldername)
    comms_list.append(x.communicate())
    x=subprocess.Popen(['git','pull'],cwd=foldername)
    comms_list.append(x.communicate())
    x=subprocess.Popen(['git','add','*'],cwd=foldername)
    comms_list.append(x.communicate())
    x=subprocess.Popen(['git','commit','-m',message],cwd=foldername)
    comms_list.append(x.communicate())
    x=subprocess.Popen(['git','push','-u','origin','master'],cwd=foldername)
    comms_list.append(x.communicate())
    

def phase3(foldername): #takes downstream arges, creates readme, push
    repo_create(foldername)
    readme_writer(foldername)
    repo_update(os.path.abspath(foldername))
    project=foldername.split('\\')[-1]
    print(f"Updated {project}")

def main(infolder,outfolder):
    foldername=phase1(infolder,outfolder)
    foldername=phase2(infolder,outfolder,foldername)
    phase3(foldername)

#TODO add a main function here

if __name__=="__main__":
    infolder=PROG   #this is the folder containing the working code
    outfolder=REPO  #this is the project folder to be updated and pushed
    main(infolder,outfolder)