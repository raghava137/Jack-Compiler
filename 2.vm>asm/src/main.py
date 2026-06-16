import sys
import os
from hackvm import HackVM

def run(path):
    vm = HackVM()
    path = path.rstrip('/')

    if os.path.isdir(path):
        vm.bootstrap()
        files = [os.path.join(path,f) for f in os.listdir(path) if f.endswith('.vm')]
        if not files:
            print("no .vm files found")
            return
        for f in sorted(files):
            vm.load_file(f)
        out = os.path.join(path, os.path.basename(path)+'.asm')
    else:
        if not path.endswith('.vm'):
            print("not a .vm file")
            return
        vm.load_file(path)
        out = path[:-3] + '.asm'

    open(out,'w').write(vm.result())
    print(f"wrote {out}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("usage: python main.py <file.vm or folder>")
        sys.exit(1)
    run(sys.argv[1])
