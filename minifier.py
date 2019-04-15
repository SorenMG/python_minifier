from __future__ import division
import os, sys
from stat import *
from distutils.dir_util import copy_tree

def walktree(top, callback):
    '''recursively descend the directory tree rooted at top,
       calling the callback function for each regular file'''

    for f in os.listdir(top):
        pathname = os.path.join(top, f)
        mode = os.stat(pathname)[ST_MODE]
        if S_ISDIR(mode):
            # Ignore .git
            if os.path.basename(pathname) == '.git':
                continue

            # It's a directory, recurse into it
            walktree(pathname, callback)
        elif S_ISREG(mode):
            # It's a file, call the callback function
            callback(pathname)
        else:
            # Unknown file type, print a message
            print('Skipping ', pathname)

def compressHTML(file):
    # Open file
    with open(file, 'r') as f:
        isDOM = False
        isText = False
        isComment = False
        lines = []
        for line in f:
            newline = ''
            for i, c in enumerate(line):
                # Delete comments
                if line[i:i+4] == '<!--':
                    isComment = True
                elif isComment and line[i-3:i] == '-->':
                    isComment = False

                if isComment:
                    continue

                if c == '<':
                    isDOM = True
                    isText = False
                elif c == '>':
                    isDOM = False
                    isText = False

                if not isDOM and not (c in [' ', '\n', '>']):
                    isText = True
                # print('DOM:', isDOM, ', Text:', isText, 'Char:', c)
                if not isDOM and not isText:
                    if c == ' ' or c == '\n':
                        continue

                newline += c
            lines.append(newline)

    lines = [line.replace('\n', '') for line in lines]

    # Write to file
    with open(file, 'w') as f:
        f.writelines(lines)

def compressCSS(file):
    # Open file
    with open(file, 'r') as f:
        isComment = False
        isNested = False
        lines = []
        for line in f:
            newline = ''
            for i, c in enumerate(line):
                # Delete comments
                if line[i:i+2] == '/*':
                    isComment = True
                elif isComment and line[i-2:i] == '*/':
                    isComment = False

                if isComment:
                    continue

                if c == '{':
                    isNested = True
                elif c == '}':
                    isNested = False

                if isNested:
                    if c == ' ' or c == '\n':
                        continue

                newline += c
            lines.append(newline)

    lines = [line.replace('\n', '') for line in lines]

    # Write to file
    with open(file, 'w') as f:
        f.writelines(lines)

def compressJavascript(file):
    # Open file
    with open(file, 'r') as f:
        isComment = False
        isString = False
        isDeclaration = False
        lines = []
        for line in f:
            newline = ''
            for i, c in enumerate(line):
                # Delete comments
                if line[i:i+2] == '//':
                    isComment = True
                elif isComment and c == '\n':
                    isComment = False

                if line[i:i+2] == '/*':
                    isComment = True
                elif isComment and line[i-2:i] == '*/':
                    isComment = False

                if isComment:
                    continue

                if line[i:i+3] == 'var':
                    isDeclaration = True
                elif isDeclaration and line[i-1:i] == ' ':
                    isDeclaration = False

                if c == '\'' or c == "\"":
                    isString = not isString

                if not isString and not isDeclaration:
                    if c == ' ' or c == '\n':
                        continue

                newline += c
            lines.append(newline)

    lines = [line.replace('\n', '') for line in lines]

    # Write to file
    with open(file, 'w') as f:
        f.writelines(lines)

def compressfile(file):
    size = os.path.getsize(file)
    if file.endswith(".html"):
        compressHTML(file)
    elif file.endswith(".css"):
        compressCSS(file)
    elif file.endswith('.js'):
        compressJavascript(file)
    else:
        return

    compressString = 'Compressed ' + os.path.basename(file) + '\t' + str(int(round(100 - (os.path.getsize(file) / size * 100)))) + '%'
    print(compressString)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Please specify a project folder and copy path')
        sys.exit()

    projectpath = sys.argv[1]
    copypath = sys.argv[2]

    copyfoldername = os.path.basename(projectpath) + '.min'
    fullcopypath = os.path.join(copypath, copyfoldername)

    try:
        # Copy project to copypath
        os.mkdir(fullcopypath)
        copy_tree(projectpath, fullcopypath)
    except OSError:
        print ("Could not copy project. The copied project might already exist in the given directory.")
        sys.exit()
    else:
        print ("Copied the directory to %s" % fullcopypath)

    # Compress copied project
    walktree(fullcopypath, compressfile)
