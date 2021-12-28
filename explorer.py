from sys import stderr
from flask import Flask, render_template, request
import subprocess as sb
import os
import shutil
from werkzeug.utils import redirect

app = Flask(__name__, template_folder='templates')

copied = []

def ls():
    output = sb.check_output(['ls', '-a'], stderr = sb.STDOUT, shell=True)
    output = str(output).split('\\n')
    output[0] = output[0][2:]
    del output[len(output)-1]
    
    return output

@app.route('/')
def explorer():
    
    output = ls()

    return render_template('home.html',len = len(output), ls = output, folder_name = os.path.basename(os.getcwd()))

@app.route('/copy', methods=['POST'])
def copy():
    copied_file = list(request.form.to_dict().keys())[0][:-5]
    copied_file_path = sb.check_output('readlink -f {}'.format(copied_file), stderr = sb.STDOUT, shell=True)
    copied_file_path = str(copied_file_path).split('\\n')
    copied_file_path[0] = copied_file_path[0][2:]
    del copied_file_path[len(copied_file_path)-1]
    copied_file_path = str(copied_file_path[0])
    
    copied.append(copied_file_path)
    copied.append(copied_file)

    return redirect('/')

@app.route('/paste', methods=['POST'])
def paste():
    if len(copied) != 0:
        if copied[0] != os.getcwd()+ '/' +copied[1]:
            try:
                shutil.copy2(copied[0],os.getcwd()+ '/' +copied[1])
            except IsADirectoryError:
                shutil.copytree(copied[0], os.getcwd()+ '/' +copied[1])
            
        else:
            try:
                shutil.copy2(copied[0],os.getcwd()+ '/' +copied[1]+'_copy')
            except IsADirectoryError:
                shutil.copytree(copied[0], os.getcwd()+ '/' +copied[1]+'_copy')

        copied.clear()
    return redirect('/')

@app.route('/back', methods=['POST'])
def back():
    os.chdir('..')
    os.path.basename(os.getcwd())

    return redirect('/')

@app.route('/remove', methods=['POST'])
def remove():
    rm = list(request.form.to_dict().keys())[0][:-3]
     
    try:
        shutil.rmtree(rm)
    except:
        os.remove(rm)

    return redirect('/')

@app.route('/rename', methods=['POST'])
def rename():
    rename = list(request.form.to_dict().keys())[0][:-7]
    return render_template('rename.html', name = rename)

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

@app.route('/cd', methods=['POST'])
def cd():
    
    if request.method == "POST":

        ls_next = list(request.form.to_dict().keys())[0]

        try:
            os.chdir(ls_next)
            
        except Exception as e:
            print(e)

        return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)