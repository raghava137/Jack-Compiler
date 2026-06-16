class VMWriter:
    def __init__(self, dest):
        self.out = open(dest, 'w')

    def write_push(self, seg, n):
        self.out.write(f'push {seg} {n}\n')

    def write_pop(self, seg, n):
        self.out.write(f'pop {seg} {n}\n')

    def write_arithmetic(self, op):
        self.out.write(op + '\n')

    def write_label(self, lbl):
        self.out.write(f'label {lbl}\n')

    def write_goto(self, lbl):
        self.out.write(f'goto {lbl}\n')

    def write_if(self, lbl):
        self.out.write(f'if-goto {lbl}\n')

    def write_call(self, fn, argc):
        self.out.write(f'call {fn} {argc}\n')

    def write_function(self, fn, nlocals):
        self.out.write(f'function {fn} {nlocals}\n')

    def write_return(self):
        self.out.write('return\n')

    def close(self):
        self.out.close()
