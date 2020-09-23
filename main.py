import glob
import urllib.request
import os
import shutil
import zipfile

from pip._vendor import requests


class Test:

    data = []

    def start(self, packName):
        if os.path.exists(packName + 'test/'):
            shutil.rmtree(packName + 'test/')
            os.makedirs(packName + 'test/')
        else:
            os.makedirs(packName + 'test/')
        loadplace = "file.txt"
        baseq = 'https://pypi.org/simple/'
        baseq += packName
        try:
            urllib.request.urlretrieve(baseq, 'text.txt')
        except urllib.error.HTTPError:
            print("Package " + packName + " not found")
            return
        f = open('text.txt', 'r')
        line = f.read()
        f.close()
        while True:
            line1 = line
            i = line.rfind('<a href=')
            line = line[i+9:]
            ii = line.rfind('#sha')
            line = line[:ii]
            if i == -1:
                return
            if line[len(line) - 1] != 'z':
                break
            else:
                line = line1[:i]
        f = open(r'tester' + packName + '.whl', "wb")
        ufr = requests.get(line)
        f.write(ufr.content)
        f.close()
        try:
            z = zipfile.ZipFile('tester' + packName + '.whl', 'r')
            z.extractall(packName + 'test/')
            z.close()
        except OSError:
            return
        filename = 'METADATA'
        buf = ''
        for root, dirnames, filenames in os.walk(packName + 'test/'):
            for file in filenames:
               if file == filename:
                    buf = root + '\\' + file
        if buf == '':
            return
        buf = buf.replace('/', '\\')
        f = open(buf, 'r')
        line = f.read()
        f.close()
        #os.remove('tester' + packName + ".whl")
        line = line.replace('\n\n', '\n')
        while len(line) > 0:
            i = line.find('Requires-Dist:')
            line = line[i:]
            j = line.find('(')
            j1 = line.find("\n")
            j2 = line.find(';')
            j3 = line.find('[')
            j4 = line.find('extra')
            if i == -1:
                return
            if j4 != -1 and j4 < j1:
                return
            if j3 < j and j3 != -1 and j3 < j1:
                bufline = line[15:j3]
            elif j != -1 and j < j1:
                bufline = line[15:j-1]
            elif j2 != -1 and j2 < j1:
                if line[j2-1] != ' ':
                    bufline = line[15:j2]
                else:
                    bufline = line[15:j2 - 1]

            else:
                bufline = line[15:j1]

            if bufline == '':
                return

            res = "\"" + packName + "\"" + '->' + "\"" + bufline + "\"" + ';'
            if res in self.data:
                bufline
            else:
                print(res)
                self.data.append(res)
                self.start(bufline)

            line = line[j1+1:]
            if i == -1:
                break

    def __init__(self):
        packName = input()
        self.start(packName)
        Fout = open("output.txt", "w")
        for packName in self.data:
            Fout.write(packName + "\n")
        Fout.close()

    def __del__(self):
        for f in glob.iglob(os.path.join("*test")):
            try:
                shutil.rmtree(f)
            except OSError as exc:
                print (exc)
        for f in glob.iglob(os.path.join("*.whl")):
            try:
                os.remove(f)
            except OSError as exc:
                print (exc)

a = Test()