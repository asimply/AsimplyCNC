Asimply CNC Software
--------------------
www.asimply.com

ABOUT ASIMPLY CNC
-----------------
This software is born to modify, control and send a gcode file to a CNC
machine based on an Arduino board.
This Arduino board must be charged with the "cnc_arduino.ino" file, also
provided. The recommended method of charging is by the Arduino software.
Asimply CNC has been written in Python 3 code using Eclipse, and the GUI
has been designed in GTK+3 using the Open Source software called Glade.
It allows to load .gcode files generated (from pyCAM for example) and
customized the order or depths before sending to the CNC.
Asimply CNC allows also send the orders to the Arduino board.

The whole program is in spanish language, but it will be soon translated.
Meanwhile, the helping notes written inside the python files are in english.

ABOUT THIS RELEASE
------------------
This is a preview release. Try it out on your project and let me know
what requirements you have. I greatly appreciate every contribution.

WARNING
-------
This is an early release and the software is not yet stable. We welcome
your bug reports.  Also please be aware that file formats may change 
as we move closer to a final release, so there's no guarantee that your
sketch files will open in future releases.

Requeriments
------------
Asimply CNC has been developed in a linux machine and hasen't been tested in
others machines yet. Nevertheless, it's hoped to run under Windows or Mac.

1. Python 3 installed.
	www.python.org
2. GTK+3 and Cairo installed
    In linux you can installed by typing:
        sudo apt-get install python3-gi
	sudo apt-get install python3-gi-cairo
	sudo apt-get install python3-gi-dbg
    For others machine like Windows, Mac Os X, or other Linux distributions see:
	http://www.gtk.org/download/index.php
3. Execute the cnc.py (Probably, it must be needed using root permissions)

LICENSING
---------
The source code of Asimply CNC is licensed under GNU GPL v3, the documentation 
and part designs under Creative Commons Attribution-ShareALike 3.0 Unported.
The full text of these licenses are shipped with this download.

This means that you can create your own variation of Asimply CNC, as long as
you credit me and also publish it under GPL. Similarly, you may re-publish
my documentation, as long as you credit me, and publish it under the same 
license.


For updated versions and news feel free to visit http://www.asimply.com

Thank you for participation,


********************************************************************************
I hope you will find this software useful and enjoy its functionality.
********************************************************************************
