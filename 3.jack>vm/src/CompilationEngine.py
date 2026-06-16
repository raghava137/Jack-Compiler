import os
from SymbolTable import SymbolTable
from VMWriter import VMWriter

BINOPS = {
    '+': 'add',
    '-': 'sub',
    '*': 'call Math.multiply 2',
    '/': 'call Math.divide 2',
    '&': 'and',
    '|': 'or',
    '<': 'lt',
    '>': 'gt',
    '=': 'eq'
}

UNOPS = {
    '-': 'neg',
    '~': 'not'
}

SEG_MAP = {
    'static':   'static',
    'field':    'this',
    'argument': 'argument',
    'local':    'local'
}

class CompilationEngine:
    def __init__(self, tokens, src):
        self.toks = tokens
        self.cur = 0
        self.lines = []
        self.table = SymbolTable()
        stem = os.path.splitext(os.path.basename(src))[0]
        self.writer = VMWriter(stem + '.vm')
        self.xml_path = stem + '.xml'
        self.cname = ''
        self.lbl = 0

    def _peek(self):
        if self.cur < len(self.toks):
            return self.toks[self.cur]
        return None

    def _next(self):
        t = self.toks[self.cur]
        self.cur += 1
        return t

    def _eat(self, expected=None, kind=None):
        return self._next()

    def _fresh_label(self):
        tag = f'LABEL{self.lbl}'
        self.lbl += 1
        return tag

    def _xval(self, tag, content):
        safe = (content
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;'))
        self.lines.append(f'<{tag}> {safe} </{tag}>')

    def _open(self, tag):
        self.lines.append(f'<{tag}>')

    def _close(self, tag):
        self.lines.append(f'</{tag}>')

    def compile_class(self):
        self._open('class')
        self._xval('keyword', self._eat()[1])
        self.cname = self._peek()[1]
        self._xval('identifier', self._eat()[1])
        self._xval('symbol', self._eat()[1])
        while self._peek() and self._peek()[1] in ('static', 'field'):
            self._class_var()
        while self._peek() and self._peek()[1] in ('constructor', 'function', 'method'):
            self._subroutine()
        self._xval('symbol', self._eat()[1])
        self._close('class')
        with open(self.xml_path, 'w') as f:
            f.write('\n'.join(self.lines) + '\n')
        self.writer.close()

    def _class_var(self):
        self._open('classVarDec')
        kind = self._peek()[1]
        self._xval('keyword', self._eat()[1])
        typ, tkind = self._peek()[1], self._peek()[0]
        if tkind == 'keyword':
            self._xval('keyword', self._eat()[1])
        else:
            self._xval('identifier', self._eat()[1])
        nm = self._peek()[1]
        self._xval('identifier', self._eat()[1])
        self.table.define(nm, typ, kind)
        while self._peek() and self._peek()[1] == ',':
            self._xval('symbol', self._eat()[1])
            nm = self._peek()[1]
            self._xval('identifier', self._eat()[1])
            self.table.define(nm, typ, kind)
        self._xval('symbol', self._eat()[1])
        self._close('classVarDec')

    def _subroutine(self):
        self._open('subroutineDec')
        self.table.reset_sub()
        stype = self._peek()[1]
        self._xval('keyword', self._eat()[1])
        if self._peek()[0] == 'keyword':
            self._xval('keyword', self._eat()[1])
        else:
            self._xval('identifier', self._eat()[1])
        sname = self._peek()[1]
        self._xval('identifier', self._eat()[1])
        self._xval('symbol', self._eat()[1])
        if stype == 'method':
            self.table.define('this', self.cname, 'argument')
        self._param_list()
        self._xval('symbol', self._eat()[1])
        self._open('subroutineBody')
        self._xval('symbol', self._eat()[1])
        while self._peek() and self._peek()[1] == 'var':
            self._var_dec()
        nloc = self.table.var_count('local')
        self.writer.write_function(f'{self.cname}.{sname}', nloc)
        if stype == 'constructor':
            nf = self.table.var_count('field')
            self.writer.write_push('constant', nf)
            self.writer.write_call('Memory.alloc', 1)
            self.writer.write_pop('pointer', 0)
        elif stype == 'method':
            self.writer.write_push('argument', 0)
            self.writer.write_pop('pointer', 0)
        self._statements()
        self._xval('symbol', self._eat()[1])
        self._close('subroutineBody')
        self._close('subroutineDec')

    def _param_list(self):
        self._open('parameterList')
        while self._peek() and self._peek()[1] != ')':
            typ, tkind = self._peek()[1], self._peek()[0]
            if tkind == 'keyword':
                self._xval('keyword', self._eat()[1])
            else:
                self._xval('identifier', self._eat()[1])
            nm = self._peek()[1]
            self._xval('identifier', self._eat()[1])
            self.table.define(nm, typ, 'argument')
            if self._peek() and self._peek()[1] == ',':
                self._xval('symbol', self._eat()[1])
        self._close('parameterList')

    def _var_dec(self):
        self._open('varDec')
        self._xval('keyword', self._eat()[1])
        typ, tkind = self._peek()[1], self._peek()[0]
        if tkind == 'keyword':
            self._xval('keyword', self._eat()[1])
        else:
            self._xval('identifier', self._eat()[1])
        nm = self._peek()[1]
        self._xval('identifier', self._eat()[1])
        self.table.define(nm, typ, 'local')
        while self._peek() and self._peek()[1] == ',':
            self._xval('symbol', self._eat()[1])
            nm = self._peek()[1]
            self._xval('identifier', self._eat()[1])
            self.table.define(nm, typ, 'local')
        self._xval('symbol', self._eat()[1])
        self._close('varDec')

    def _statements(self):
        self._open('statements')
        dispatch = {
            'let':    self._let,
            'if':     self._if,
            'while':  self._while,
            'do':     self._do,
            'return': self._return
        }
        while self._peek() and self._peek()[1] in dispatch:
            dispatch[self._peek()[1]]()
        self._close('statements')

    def _let(self):
        self._open('letStatement')
        self._xval('keyword', self._eat()[1])
        nm = self._peek()[1]
        self._xval('identifier', self._eat()[1])
        arr = False
        if self._peek() and self._peek()[1] == '[':
            arr = True
            self._xval('symbol', self._eat()[1])
            seg = SEG_MAP.get(self.table.kind_of(nm), 'local')
            self.writer.write_push(seg, self.table.index_of(nm))
            self._expression()
            self.writer.write_arithmetic('add')
            self._xval('symbol', self._eat()[1])
        self._xval('symbol', self._eat()[1])
        self._expression()
        self._xval('symbol', self._eat()[1])
        if arr:
            self.writer.write_pop('temp', 0)
            self.writer.write_pop('pointer', 1)
            self.writer.write_push('temp', 0)
            self.writer.write_pop('that', 0)
        else:
            seg = SEG_MAP.get(self.table.kind_of(nm), 'local')
            self.writer.write_pop(seg, self.table.index_of(nm))
        self._close('letStatement')

    def _if(self):
        self._open('ifStatement')
        else_lbl = self._fresh_label()
        end_lbl  = self._fresh_label()
        self._xval('keyword', self._eat()[1])
        self._xval('symbol', self._eat()[1])
        self._expression()
        self._xval('symbol', self._eat()[1])
        self.writer.write_arithmetic('not')
        self.writer.write_if(else_lbl)
        self._xval('symbol', self._eat()[1])
        self._statements()
        self._xval('symbol', self._eat()[1])
        self.writer.write_goto(end_lbl)
        self.writer.write_label(else_lbl)
        if self._peek() and self._peek()[1] == 'else':
            self._xval('keyword', self._eat()[1])
            self._xval('symbol', self._eat()[1])
            self._statements()
            self._xval('symbol', self._eat()[1])
        self.writer.write_label(end_lbl)
        self._close('ifStatement')

    def _while(self):
        self._open('whileStatement')
        top_lbl  = self._fresh_label()
        exit_lbl = self._fresh_label()
        self.writer.write_label(top_lbl)
        self._xval('keyword', self._eat()[1])
        self._xval('symbol', self._eat()[1])
        self._expression()
        self._xval('symbol', self._eat()[1])
        self.writer.write_arithmetic('not')
        self.writer.write_if(exit_lbl)
        self._xval('symbol', self._eat()[1])
        self._statements()
        self._xval('symbol', self._eat()[1])
        self.writer.write_goto(top_lbl)
        self.writer.write_label(exit_lbl)
        self._close('whileStatement')

    def _do(self):
        self._open('doStatement')
        self._xval('keyword', self._eat()[1])
        nm = self._peek()[1]
        self._xval('identifier', self._eat()[1])
        self._call(nm)
        self._xval('symbol', self._eat()[1])
        self.writer.write_pop('temp', 0)
        self._close('doStatement')

    def _return(self):
        self._open('returnStatement')
        self._xval('keyword', self._eat()[1])
        if self._peek() and self._peek()[1] != ';':
            self._expression()
        else:
            self.writer.write_push('constant', 0)
        self._xval('symbol', self._eat()[1])
        self.writer.write_return()
        self._close('returnStatement')

    def _expression(self):
        self._open('expression')
        self._term()
        while self._peek() and self._peek()[1] in BINOPS:
            op = self._peek()[1]
            self._xval('symbol', self._eat()[1])
            self._term()
            instr = BINOPS[op]
            if instr.startswith('call'):
                parts = instr.split()
                self.writer.write_call(parts[1], int(parts[2]))
            else:
                self.writer.write_arithmetic(instr)
        self._close('expression')

    def _term(self):
        self._open('term')
        t = self._peek()
        if t is None:
            self._close('term')
            return
        kind, val = t
        if kind == 'integerConstant':
            self._xval('integerConstant', self._eat()[1])
            self.writer.write_push('constant', int(val))
        elif kind == 'stringConstant':
            self._eat()
            self._xval('stringConstant', val)
            self.writer.write_push('constant', len(val))
            self.writer.write_call('String.new', 1)
            for ch in val:
                self.writer.write_push('constant', ord(ch))
                self.writer.write_call('String.appendChar', 2)
        elif kind == 'keyword' and val in ('true', 'false', 'null', 'this'):
            self._xval('keyword', self._eat()[1])
            if val == 'true':
                self.writer.write_push('constant', 0)
                self.writer.write_arithmetic('not')
            elif val in ('false', 'null'):
                self.writer.write_push('constant', 0)
            else:
                self.writer.write_push('pointer', 0)
        elif val == '(':
            self._xval('symbol', self._eat()[1])
            self._expression()
            self._xval('symbol', self._eat()[1])
        elif val in ('-', '~'):
            self._xval('symbol', self._eat()[1])
            self._term()
            self.writer.write_arithmetic(UNOPS[val])
        elif kind == 'identifier':
            nm = val
            self._xval('identifier', self._eat()[1])
            nxt = self._peek()
            if nxt and nxt[1] == '[':
                self._xval('symbol', self._eat()[1])
                seg = SEG_MAP.get(self.table.kind_of(nm), 'local')
                self.writer.write_push(seg, self.table.index_of(nm))
                self._expression()
                self.writer.write_arithmetic('add')
                self.writer.write_pop('pointer', 1)
                self.writer.write_push('that', 0)
                self._xval('symbol', self._eat()[1])
            elif nxt and nxt[1] in ('(', '.'):
                self._call(nm)
            else:
                k = self.table.kind_of(nm)
                if k:
                    self.writer.write_push(SEG_MAP.get(k, 'local'), self.table.index_of(nm))
        self._close('term')

    def _call(self, nm):
        argc = 0
        if self._peek() and self._peek()[1] == '.':
            self._xval('symbol', self._eat()[1])
            mname = self._peek()[1]
            self._xval('identifier', self._eat()[1])
            k = self.table.kind_of(nm)
            if k:
                self.writer.write_push(SEG_MAP.get(k, 'local'), self.table.index_of(nm))
                full = f'{self.table.type_of(nm)}.{mname}'
                argc = 1
            else:
                full = f'{nm}.{mname}'
        else:
            full = f'{self.cname}.{nm}'
            self.writer.write_push('pointer', 0)
            argc = 1
        self._xval('symbol', self._eat()[1])
        argc += self._expr_list()
        self._xval('symbol', self._eat()[1])
        self.writer.write_call(full, argc)

    def _expr_list(self):
        self._open('expressionList')
        n = 0
        if self._peek() and self._peek()[1] != ')':
            self._expression()
            n += 1
            while self._peek() and self._peek()[1] == ',':
                self._xval('symbol', self._eat()[1])
                self._expression()
                n += 1
        self._close('expressionList')
        return n
