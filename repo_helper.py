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
from admin import fileverify, read_json


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

def select_file(filelist):  #forcing user to choose which file to work on
    filedict={str(ix):i for ix,i in enumerate(filelist)} #for easiest reference
    print("Please select which program you'd like to create a repo for.")
    nice_print(filelist)
    selection=filedict[input("Please enter the number of your selection.")]
    return(selection)

def subprocess_cmd(command,wd):
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True,cwd=wd)
    proc_stdout = process.communicate()[0].strip()
    print(proc_stdout)
    
#next, create that folder and init the repo, add file to start
def repo_init(infolder,selection,foldername):
    fname=os.path.join(infolder,selection+'.py')
    os.mkdir(foldername)
    command="git init"
    subprocess_cmd(command,foldername)
    shutil.copy(fname,foldername)
    

def phase1(infolder,outfolder)->str: #takes folders, creates folder,git, outputs path
    selection=select_file(compare_lists(infolder,outfolder))
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

#once that's done, we generate requirements using pipreqs
def create_reqs(foldername):
    command="pipreqs .\ "
    subprocess_cmd(command,foldername)


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
    
#TODO update this to reate a json file inside the repo with this information
#this will make future updates of readme much, much easier
#TODO modify this function to accept optional json argument for that reason
def readme_writer(foldername,purpose=None,backstory=None,prework=None,frequency=None):
    #TODO make this tool more sophisticated to work with metaprogram 
    if purpose:
        purpose=purpose
    else:
        purpose=input("In 1 brief sentence, please describe what this project does \n")
    if backstory:
        backstory=backstory
    else:
        backstory=input("In a few sentences, explain why it is/was needed\n")
    if 'requirements.txt' in os.listdir(foldername):
        libraries=os.path.join(foldername,'requirements.txt')
        with open (libraries,'r') as f:
            lines=f.readlines()
            libs=', '.join([line.split("=")[0] for line in lines])
    else:
        libs=""
    if prework:
        prework=prework
    else:
        prework=input('Is there anything a user needs to do prior to running? If yes, write that out below.\n')
    
    if frequency:
        frequency=frequency
    else:
        freq=['Continuously','Daily','Weekly','Monthly','As Needed']
        freqdict={str(ix):i for ix,i in enumerate(freq)}
        #TODO replace with stdout, add exception handling here
        print("How often is this intended to be run?")
        for ix,i in enumerate(freq):
            print(f'{ix}. {i}')
        frequency=freqdict[input('Please enter your selection number.\n')]
    #TODO include fancy formatting later
    readme1="## The purpose of this project is as follows:"
    readme2="## Here's some back story on why I needed to build this:"
    if len(libs)>1:
        readme3="## This project leverages the following libraries:"
    else: readme3="## This project uses only python built-in functions and data types."
    if len(prework)>2:
        readme4="## In order to use this, you'll first need do the following:"
        
    else:
        readme4="## This project does not require any special setup steps."
        prework=""
    readme5="## The expected frequency for running this code is as follows:"
    bre="\n"
    readme=[readme1,bre,purpose,bre,readme2,bre,backstory,bre,readme3,
            bre,libs,bre,readme4,bre,prework,bre,readme5,bre,frequency]
    readme_file=os.path.join(foldername,"README.md")
    with open(readme_file,'w') as f:
        f.writelines(readme)
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
    

def phase3(infolder,outfolder): #takes downstream arges, creates readme, push
    foldername=phase1(infolder,outfolder)
    foldername=phase2(infolder,outfolder,foldername)
    repo_create(foldername)
    readme_writer(foldername)
    repo_update(os.path.abspath(foldername))
    project=foldername.split('\\')[-1]
    print(f"Updated {project}")



if __name__=="__main__":
    infolder=r'C:\Users\shane\Desktop\Projects\Programs'   #this is the folder containing the working code
    outfolder=r'C:\Users\shane\Desktop\Programming'  #this is the project folder to be updated and pushed
    phase3(infolder,outfolder)