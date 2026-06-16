import sys
import os
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine

def run():
    target = sys.argv[1]
    queue = []
    if os.path.isdir(target):
        for fname in os.listdir(target):
            if fname.endswith('.jack'):
                queue.append(os.path.join(target, fname))
    else:
        queue.append(target)

    for jfile in queue:
        t = JackTokenizer(jfile)
        toks = t.tokenize()
        eng = CompilationEngine(toks, jfile)
        eng.compile_class()
        print(f'compiled: {jfile}')

if __name__ == '__main__':
    run()
