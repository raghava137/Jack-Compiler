import os

class HackVM:
    def __init__(self):
        self.asm = []
        self.lc = 0
        self.fname = ""
        self.fn = ""
        self.cc = 0

    def load_file(self, path):
        self.fname = os.path.basename(path)[:-3]
        raw = open(path).readlines()
        for line in raw:
            line = line.split('//')[0].strip()
            if line:
                self._do(line)

    def _emit(self, *xs):
        for x in xs:
            self.asm.append(x)

    def _push_d(self):
        self._emit('@SP','A=M','M=D','@SP','M=M+1')

    def _pop_d(self):
        self._emit('@SP','AM=M-1','D=M')

    def _do(self, cmd):
        p = cmd.split()
        op = p[0]

        if op in ('add','sub','neg','eq','gt','lt','and','or','not'):
            self._arith(op)
        elif op == 'push':
            self._push(p[1], int(p[2]))
        elif op == 'pop':
            self._pop(p[1], int(p[2]))
        elif op == 'label':
            self._emit(f'({self.fn}${p[1]})')
        elif op == 'goto':
            self._emit(f'@{self.fn}${p[1]}', '0;JMP')
        elif op == 'if-goto':
            self._pop_d()
            self._emit(f'@{self.fn}${p[1]}', 'D;JNE')
        elif op == 'function':
            self._func(p[1], int(p[2]))
        elif op == 'call':
            self._call(p[1], int(p[2]))
        elif op == 'return':
            self._ret()

    def _arith(self, op):
        if op == 'neg':
            self._emit('@SP','A=M-1','M=-M')
            return
        if op == 'not':
            self._emit('@SP','A=M-1','M=!M')
            return

        self._emit('@SP','AM=M-1','D=M','A=A-1')

        if op == 'add': self._emit('M=D+M')
        elif op == 'sub': self._emit('M=M-D')
        elif op == 'and': self._emit('M=D&M')
        elif op == 'or':  self._emit('M=D|M')
        elif op in ('eq','gt','lt'):
            j = {'eq':'JEQ','gt':'JGT','lt':'JLT'}[op]
            t = self.lc
            self.lc += 1
            self._emit(
                'D=M-D',
                f'@_T{t}', f'D;{j}',
                '@SP','A=M-1','M=0',
                f'@_E{t}','0;JMP',
                f'(_T{t})','@SP','A=M-1','M=-1',
                f'(_E{t})'
            )

    def _seg_base(self, seg):
        return {'local':'LCL','argument':'ARG','this':'THIS','that':'THAT'}[seg]

    def _push(self, seg, i):
        if seg == 'constant':
            self._emit(f'@{i}','D=A')
            self._push_d()

        elif seg in ('local','argument','this','that'):
            b = self._seg_base(seg)
            self._emit(f'@{i}','D=A',f'@{b}','A=D+M','D=M')
            self._push_d()

        elif seg == 'temp':
            self._emit(f'@{5+i}','D=M')
            self._push_d()

        elif seg == 'pointer':
            r = 'THIS' if i == 0 else 'THAT'
            self._emit(f'@{r}','D=M')
            self._push_d()

        elif seg == 'static':
            self._emit(f'@{self.fname}.{i}','D=M')
            self._push_d()

    def _pop(self, seg, i):
        if seg in ('local','argument','this','that'):
            b = self._seg_base(seg)
            self._emit(f'@{i}','D=A',f'@{b}','D=D+M','@R13','M=D')
            self._pop_d()
            self._emit('@R13','A=M','M=D')

        elif seg == 'temp':
            self._pop_d()
            self._emit(f'@{5+i}','M=D')

        elif seg == 'pointer':
            r = 'THIS' if i == 0 else 'THAT'
            self._pop_d()
            self._emit(f'@{r}','M=D')

        elif seg == 'static':
            self._pop_d()
            self._emit(f'@{self.fname}.{i}','M=D')

    def _func(self, name, nloc):
        self.fn = name
        self._emit(f'({name})')
        for _ in range(nloc):
            self._emit('@SP','A=M','M=0','@SP','M=M+1')

    def _call(self, name, nargs):
        ret = f'{name}$r{self.cc}'
        self.cc += 1

        self._emit(f'@{ret}','D=A')
        self._push_d()
        for reg in ('LCL','ARG','THIS','THAT'):
            self._emit(f'@{reg}','D=M')
            self._push_d()

        self._emit(f'@{nargs+5}','D=A','@SP','D=M-D','@ARG','M=D')
        self._emit('@SP','D=M','@LCL','M=D')
        self._emit(f'@{name}','0;JMP')
        self._emit(f'({ret})')

    def _ret(self):
        self._emit(
            '@LCL','D=M','@R14','M=D',
            '@5','A=D-A','D=M','@R15','M=D',
        )
        self._pop_d()
        self._emit('@ARG','A=M','M=D')
        self._emit('@ARG','D=M+1','@SP','M=D')
        for reg in ('THAT','THIS','ARG','LCL'):
            self._emit('@R14','AM=M-1','D=M',f'@{reg}','M=D')
        self._emit('@R15','A=M','0;JMP')

    def bootstrap(self):
        self._emit('@256','D=A','@SP','M=D')
        self._call('Sys.init', 0)

    def result(self):
        return '\n'.join(self.asm)
