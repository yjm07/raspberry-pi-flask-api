from git import Repo
import subprocess
import os


path = os.getcwd()
git_tmp_path = path + '/.git-tmp'
templates_path = path + '/templates'
static_path = path + '/static'

# Remove templates and static
proc_erase_templates_static = subprocess.Popen(f"sudo rm -r {templates_path}/* {static_path}/*", shell=True)
proc_erase_templates_static.wait()

# Clone git repository
Repo.clone_from("https://github.com/LUXROBO/smart-ai-dashboard-build.git", git_tmp_path)

# Move to right directories
proc_templates = subprocess.Popen(["sudo", "cp", git_tmp_path+'/index.html', templates_path])
proc_templates.wait()

proc_statics = subprocess.Popen(f"sudo cp -rf {git_tmp_path}/* {static_path}", shell=True)
proc_statics.wait()

# Remove .git-tmp
proc_erase_git_tmp = subprocess.Popen(f"sudo rm -r {git_tmp_path}/* {git_tmp_path}/.??*", shell=True)
