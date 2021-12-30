from html import entities
from sys import stderr
from flask import Flask, render_template, request
import subprocess as sb
import os
import shutil

from werkzeug.utils import redirect

app = Flask(__name__, template_folder='templates')

copied_files_global = []
copied_files_path_global = []

def ls():
    output = sb.check_output(['ls', '-a'], stderr = sb.STDOUT, shell=True)
    output = str(output).split('\\n')
    output[0] = output[0][2:]
    del output[len(output)-1]
    
    return output

@app.route('/')
def explorer():
    
    output = ls()

    return render_template('home.html',len = len(output), ls = output, folder_name = os.path.basename(os.getcwd()), path = os.getcwd())

@app.route('/action', methods=['POST'])
def action():
    print(list(request.form.to_dict().keys()))
    if len(list(request.form.to_dict().keys())) == 1:
        work = cd(list(request.form.to_dict().keys())[0])
        if work == True:
            return redirect('/')
        else:
            return render_template('error.html', error = work)

    elif 'rm' == list(request.form.to_dict().keys())[len(list(request.form.to_dict().keys()))-1]:
        remove(list(request.form.to_dict().keys()))
        return redirect('/')
    elif 'copy' == list(request.form.to_dict().keys())[len(list(request.form.to_dict().keys()))-1]:
        copy(list(request.form.to_dict().keys()))
        return redirect('/')
    elif 'rename' == list(request.form.to_dict().keys())[len(list(request.form.to_dict().keys()))-1]:
        return render_template('rename.html', name = list(request.form.to_dict().keys())[0])

    elif 'authorization' == list(request.form.to_dict().keys())[len(list(request.form.to_dict().keys()))-1]:
        return render_template('authorization.html', name = list(request.form.to_dict().keys())[0])


def copy(copied_files):
    copied_files.pop()
    copied_files_path = []
    for item in copied_files:
        copied_file_path = sb.check_output('readlink -f {}'.format(item), stderr = sb.STDOUT, shell=True)
        copied_file_path = str(copied_file_path).split('\\n')
        copied_file_path[0] = copied_file_path[0][2:]
        del copied_file_path[len(copied_file_path)-1]
        
        if len(copied_file_path) != 1:
            copied_2 = copied_file_path[1].split('/')
            copied_file_path = str(copied_file_path[0]) + " " + str(copied_2[len(copied_2)-1])
        else:
            copied_file_path = str(copied_file_path[0])
        
        copied_files_path.append(copied_file_path)

    for i in copied_files:
        copied_files_global.append(i)

    for i in copied_files_path:
        copied_files_path_global.append(i)

    return redirect('/')

@app.route('/paste', methods=['POST'])
def paste():
    if len(copied_files_global) != 0 and len(copied_files_path_global) != 0:
        for file, path in zip(copied_files_global,copied_files_path_global):
            if path != os.getcwd()+ '/' + file:
                try:
                    shutil.copy2(path,os.getcwd()+ '/' + file)
                except IsADirectoryError:
                    shutil.copytree(path, os.getcwd()+ '/' + file)
                
            else:
                try:
                    shutil.copy2(path,os.getcwd()+ '/' + file +'_copy')
                except IsADirectoryError:
                    shutil.copytree(path, os.getcwd()+ '/' + file +'_copy')

        copied_files_global.clear()
        copied_files_path_global.clear()
    return redirect('/')

@app.route('/back', methods=['POST'])
def back():
    os.chdir('..')
    os.path.basename(os.getcwd())

    return redirect('/')


def remove(rm):
    rm.pop()
    print(rm)
    for item in rm:
        try:
            shutil.rmtree(item)
        except:
            os.remove(item)

    return redirect('/')

@app.route('/authorization_active', methods=['POST'])
def authorization_active():
    owner_work = 0
    group_work = 0
    other_work = 0
    for mod in list(request.form.to_dict().keys()):
        if mod == 'owner_read':
            owner_work += 4
        elif mod == 'owner_write':
            owner_work += 2
        elif mod == 'owner_execute':
            owner_work += 1

        if mod == 'group_read':
            group_work += 4
        elif mod == 'group_write':
            group_work += 2
        elif mod == 'group_execute':
            group_work += 1

        if mod == 'other_read':
            other_work += 4
        elif mod == 'other_write':
            other_work += 2
        elif mod == 'other_execute':
            other_work += 1

    work = owner_work * 64 + group_work * 8 + other_work
    os.chmod(list(request.form.to_dict().keys())[len(request.form.to_dict().keys())-1], work)
    return redirect('/')

@app.route('/rename_active', methods=['POST'])
def rename_active():
    name = list(request.form.to_dict().keys())[1]
    rename = request.form.get('rename_input')
    os.rename(name,rename)
    
    return redirect('/')

@app.route('/new_folder', methods=['POST'])
def new_folder():
    folder = 'New Folder'
    if os.path.exists(folder):
        i = 0
        while True:
            if os.path.exists(folder+str(i)):
                i+=1
            else:
                os.makedirs(folder+str(i))
                break
    else:
        os.makedirs(folder)

    return redirect('/')


def cd(ls_next):
    
    try:
        os.chdir(ls_next)
        return True
        
    except Exception as e:
        return str(e)
    

    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)