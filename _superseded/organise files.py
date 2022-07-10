from distutils import extension
import os
from posixpath import dirname 
import shutil

dirName=input('Enter Folder Path: ')
li=os.listdir(dirName)

for i in li:
    FileName, extension = os.path.splitext(i)
    extension=extension[1:]
    if extension=="":
        continue
    if os.path.exists(dirName+"/"+extension):
        shutil.move(dirName+"/"+i,dirName+"/"+extension+"/"+i)
    else:
        os.makedirs(dirName+"/"+extension)
        shutil.move(dirName+"/"+i,dirName+"/"+extension+"/"+i)        