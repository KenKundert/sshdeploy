SSH Keys
========

Introduction
++++++++++++

SSH Keys is used to distribute your private ssh keys and generate your 
authorized keys files. It assumes that you have one directory (KeyDir) where you 
keep your private keys and their associated public keys. It also assumes 
a config file (ConfigFile) that contains the name of the keys and servers to be 
managed.

You distribute your keys using by running the command directly from its source 
directory (it is not installed)::

   ./sshkeys

You can specify particular servers to update using the --update (or -u) command 
line option::

   ./sshkeys --update earth

You can specify particular servers to skip using the --skip (or -s) command line 
option::

   ./sshkeys --skip mercury

With either --update or --skip you can specify multiple servers using a comma 
separated list of keys::

   ./sshkeys --skip jupiter,mercury


Configuration
+++++++++++++

The configuration files is a python file named 'config' that should exist in the 
same directory as the executable that contains a hierarchical collection of 
dictionaries name 'Keys'.  Here is a typical configuration file::

    Keys = {
        'earth': {
            'purpose': 'This key allows access from earth (primary laptop)',
            'servers': {
                'earth': {'send': ['private-key', 'authorized-keys']},
                'mercury': {
                    'description': 'Access is funneled through Jupiter',
                    'restrictions': ['from=jupiter']
                },
                'jupiter': {},
            },
        },
        'phone': {
            'purpose': "This key allows access from the phone",
            'servers': {
                'jupiter': {
                    'description': 'Only allows access to mail ports',
                    'restrictions': [
                        'no-agent-forwarding',
                        'no-pty',
                        'no-X11-forwarding',
                        'permitopen="pubmail:587"',
                        'permitopen="pubmail:993"',
                    ],
                },
            },
        },
        'backups': {
            'purpose': "This key allows sftp access to jupiter for backups.",
            'servers': {
                'earth': {'send': 'private-key'},
                'mercury': {'send': 'private-key'},
                'jupiter': {
                    'description': 'This key is not protected with a passphrase!',
                    'restrictions': [
                        'from="192.168.1.0/24"',
                        'no-agent-forwarding',
                        'no-port-forwarding',
                        'no-pty',
                        'no-X11-forwarding',
                        'command=".ssh/only-sftp.sh"',
                    ],
                },
            }
        },
    }


The keys of the first level of dictionaries should be the filenames for the 
private keys. The values should be dictionaries that may contain the keys 
'purpose' and 'servers'.

Purpose
-------
The purpose if given is simple a textual description of the purpose of the key.  
It will be added as a comment above the public key when it is added to the 
authorized key file.

Servers
-------
The servers key contains a dictionary where its keys would be the SSH name of 
the servers that should receive the key.  The value of the servers key is also 
a dictionary that may be empty or may contain the following keys: 'description', 
'send', 'restrictions'.

Description
'''''''''''
The description is simply a second level of textual description for the public 
key (generally explains the restrictions).

Send
''''
The value of send may either be 'authorized-keys', 'private-key' or a list that 
contains either or both of the values. If not given, it is assumed to be 
'authorized-keys'. If the value contains 'authorized-keys', an updated 
authorized_keys file is sent to that server.  If it contains 'private-key', the 
private key and its corresponding public key is copied to the server.

Restrictions
''''''''''''
The value of restrictions is a list of SSH key restrictions. These restrictions 
are comma joined and placed before the public key in the authorized key file.
