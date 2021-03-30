from git import Repo
import subprocess
import os


path = os.getcwd()
git_tmp_path = path + '/.git-tmp'
static_path = path + '/static'
templates_path = path + '/templates'


Repo.clone_from("https://github.com/LUXROBO/smart-ai-dashboard-build.git", git_tmp_path)

proc_templates = subprocess.Popen(["sudo", "mv", git_tmp_path+'/index.html', templates_path])
proc_templates.wait()

proc_statics = subprocess.Popen(f"sudo cp -rf {git_tmp_path}/* {static_path}", shell=True)
proc_statics.wait()

proc_erase = subprocess.Popen(f"sudo rm -r {git_tmp_path}/* {git_tmp_path}/.??*", shell=True)
