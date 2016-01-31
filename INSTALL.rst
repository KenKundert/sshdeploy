Installation
++++++++++++

If you plan to use SSH Keys without modifying it the preferred way to install it 
for multiple users is::

   pip install --update sshdeploy

Doing so generally requires root permissions. Alternately, you can install it 
just for yourself using::

   pip install --user --update sshdeploy

This does not require root permissions.

If you would like to change the program, you should first clone it's source 
repository and then install it::

   git clone https://github.com/KenKundert/sshdeploy.git
   cd sshdeploy
   python setup.py install --user
