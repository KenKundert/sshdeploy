"""Generate Keys

Regenerates and distributes SSH keys.

Usage:
    sshpush [options] [<config-file>]

Options:
    -g, --generate-only            only generate new keys
    -d <keydir>, --distribute-only <keydir>
                                   only distribute keys,
                                   use those found in <keydir> instead
    -u <hosts>, --update <hosts>   servers to update
    -s <hosts>, --skip <hosts>     servers to skip
    -n, --narrate                  narrate the process
    -v, --verbose                  narrate the process more verbosely
    -t, --trial-run                trial run (do not override ssh files)
    -k <keys>, --keys <keys>       keys to update (only use with --trial-run)
    -h, --help                     print usage summary
    -m, --manual                   print manual

If <config-file> is not specified, config.sshpush is used'
Keys and servers are specified with a comma separated list (no spaces).
""" 

# Imports {{{1
from .prefs import (
    DefaultKeygenOpts, DefaultAbraxasAccount, DefaultRemoteIncludeFilename
)
from .utils import date
from .key import Key
from .authkeys import AuthKeys
from docopt import docopt
from shlib import to_path, Run, mkdir, cd, rm
from inform import Inform, comment, display, error, fatal, os_error, terminate

def main():
    try:
        # Read command line {{{1
        cmdline = docopt(__doc__)
        keys = cmdline['--keys'].split(',') if cmdline['--keys'] else []
        update = cmdline['--update'].split(',') if cmdline['--update'] else []
        skip = cmdline['--skip'].split(',') if cmdline['--skip'] else []
        Inform(
            narrate=cmdline['--narrate'] or cmdline['--verbose'],
            verbose=cmdline['--verbose'],
            logfile='.sshpush.log',
            prog_name=False
        )
        if cmdline['--distribute-only'] and cmdline['--generate-only']:
            fatal('specify only --distribute-only or --generate-only, not both.')
        if keys and not cmdline['--trial-run']:
            fatal(
                'Using the --keys option results in incomplete authorized_keys files.',
                'It may only be used for testing purposes.',
                'As such, --trial-run must also be specified when using --keys.',
                sep='\n'
            )

        # Generated detailed help {{{1
        if cmdline['--manual']:
            from pkg_resources import resource_string
            try:
                Run(
                    cmd=['less'], modes='soeW0',
                    stdin=resource_string('src', 'manual.rst').decode('utf8')
                )
            except OSError as err:
                error(os_error(err))
            terminate()

        # Read config file {{{1
        try:
            config_file = cmdline.get('<config-file>')
            config_file = config_file if config_file else 'config.sshpush'
            contents = to_path(config_file).read_text()
        except OSError as err:
            fatal(os_error(err))
        code = compile(contents, config_file, 'exec')
        config = {}
        try:
            exec(code, config)
        except Exception as err:
            fatal(err)

        # Move into keydir {{{1
        if cmdline['--distribute-only']:
            keydir = to_path(cmdline['--distribute-only'])
        else:
            keydir = to_path('keys-' + date)
            comment('creating key directory:', keydir)
            rm(keydir)
            mkdir(keydir)
        cd(keydir)

        # determine default values for key options
        defaults = {}
        for name, default in [
            ('keygen-options', DefaultKeygenOpts),
            ('abraxas-account', DefaultAbraxasAccount),
            ('remote-include-filename', DefaultRemoteIncludeFilename),
        ]:
            defaults[name] = config.get(name, default)

        # Process keys {{{1
        for keyname in sorted(config['keys'].keys()):
            data = config['keys'][keyname]
            if keys and keyname not in keys:
                # user did not request this key
                continue

            # get default values for missing key options
            for option in defaults:
                data[option] = data.get(option, defaults[option])

            # process the key
            key = Key(keyname, data, update, skip, cmdline['--trial-run'])
            if not cmdline['--distribute-only']:
                key.generate()
            if not cmdline['--generate-only']:
                key.publish_private_key()
                key.gather_public_keys()

        # Publish authorized_keys files {{{1
        if not cmdline['--generate-only']:
            for each in sorted(AuthKeys.known):
                authkey = AuthKeys.known[each]
                authkey.publish()
                authkey.verify()
    except OSError as err:
        error(os_error(err))
    except KeyboardInterrupt:
        display('Killed by user')
