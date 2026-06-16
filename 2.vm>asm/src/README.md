1. Make sure Python 3 is installed.
2. Place hackvm.py and main.py in the same folder.
3. Put your .vm file(s) in any folder (e.g., the same folder as the scripts, or a subfolder).

To translate a single .vm file:
    python main.py path/to/yourfile.vm
    Output .asm file is created next to the input file.

To translate a folder containing multiple .vm files:
    python main.py path/to/folder/
    All .vm files in that folder are processed together.
    Bootstrap code is added automatically.
    Output .asm file is placed inside that folder.