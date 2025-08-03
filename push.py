import subprocess
import os 

current_directory = os.getcwd()
msg = input(' whats the msg? : ').strip()

if msg == '':
    msg = 'Added something - (this msg was written by cmd)'
bash = 'C:/Program Files/Git/git-bash.exe'

subprocess.run([
    bash, '-c', 
    f'cd "{current_directory}" && '
    f'git add . && '
    f'git commit -m "{msg}" && '
    'git push'
])

print('done')