#!/usr/bin/python
class Stack:
    def __init__(self, output):
        self.sp = 256
        self.out = output

        # init the SP to 256 with the following hack instructions
        out.writelines([
            '@256',
            'D=A'
            '@SP'
            'M=D'
        ])

    def inc_sp():
        out.writeline([
            '// increment sp',
            '@SP',
            'M=M+1'
        ])

    def dec_sp():
        out.writeline([
            '// decrement sp',
            '@SP',
            'M=M-1'
        ])

    def push(seg, i):
        if seg == 'constant':
            out.writelines([
                # load a constant into the current SP RAM location
                '@{}'.format(i),
                'D=A',
                '@SP',
                'M=D'
            ])
        else:
            out.writelines([
                # offset with the segment address, load value into data register
                '@{}'.format(get_loc(seg[0])),
                'D=A',
                '@{}'.format(i),
                'A=A+D',
                'D=M',
                # load into SP location
                '@SP',
                'M=D'
            ])
        self.inc_sp()

    def pop(seg, i):
        out.writelines([
            s
        ])
        self.dec_sp()
        

    def operation(op):
        if op == 'add':
            pass
        elif op == 'sub':
            pass
        elif op == 'eq':
            pass
        elif op == 'gt':
            pass
        elif op == 'lt':
            pass
        elif op == 'and':
            pass
        elif op == 'or':
            pass
        elif op == 'neg':
            pass
        elif op == 'not':
            pass
        else:
            print('INVALID OP!', op)

    def translate_line(line):
        self.out.write("// {}".format(line)); # add a comment for each vm instruction
        tokens = line.split()
        if tokens[0] == 'push':
            self.push(tokens[0], tokens[1])
        elif tokens[0] == 'pop':
            self.pop(tokens[0], tokens[1])
        else:
            self.operation(tokens[0))

result = open(output)
s = Stack(result)
with open(file) as f:
    line = f.readline()
    while line:
        s.translate_line(line)

result.close()
