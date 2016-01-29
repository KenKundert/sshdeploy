from shlib import Run
from inform import comment, display, fmt
from arrow import now                                                                                                  

# today's date
date = now().format('YYYY-MM-DD')                                                                              

# run a command
def run(cmd, stdin=None, modes=None):
    comment('    running:', *cmd)
    Run(cmd, stdin=stdin, modes=modes)

# run an sftp command
def run_sftp(server, cmds):
    cmd = ['sftp', '-q', '-b', '-', server]
    comment(fmt('    sftp {server}:'), '; '.join(cmds))
    try:
        Run(cmd, stdin='\n'.join(cmds), modes='sOEW')
    except KeyboardInterrupt:
        display('Continuing')
