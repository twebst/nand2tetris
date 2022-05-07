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

        self.segments = {
            'local': 'LCL',
            'argument': 'ARG',
            'this': 'THIS',
            'that': 'THAT'
            'temp': 'TEMP'
        }

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
        elif seg in self.segments:
            out.writelines([
                # offset with the segment address, load value into data register
                '@{}'.format(self.segments(seg)),
                'D=A',
                '@{}'.format(i),
                'A=A+D',
                'D=M',
                # load into SP location
                '@SP',
                'M=D'
            ])
        elif seg == 'static': # assembly variables are static (16-255)
            out.writelines([
                '@static.{}'.format(i),
                'D=M',
                '@SP',
                'M=D'
            ])
        elif seg == 'pointer': # pointer 0 and 1 are aliases to THIS and THAT respectively
            if i == '0': seg = 'this'
            elif i == '1': seg = 'that'
            else: print('Invalid pointer segment, expected 0 (THIS) or 1 (THAT)!')
            out.writelines([
                '@{}'.format(self.segments(seg)),
                'D=M',
                '@SP',
                'M=D'
            ])
        else: print('Invalid push! Got: ', seg, i)

        self.inc_sp()

    def pop(seg, i):
        if seg in self.segments:
            # there might be a more efficient way to do this, but for now use the virtual register R13 to store seg + i
            out.writelines([
                # calculate offseted segment location, and then store for later
                '@{}'.format(i),
                'D=A',
                '@{}'.format(self.segments[seg]),
                'D=D+A',
                '@R13',
                'M=D',
                # load value from SP
                '@SP',
                'D=M',
                # retrieve and use address previously calculated
                '@R13',
                'A=M',
                'M=D'
            ])
        elif seg == 'static': # assembly variables are static (16-255)
            out.writelines([
                '@SP',
                'D=M',
                '@static.{}'.format(i),
                'M=D'
            ])
        elif seg == 'pointer': # pointer 0 and 1 are aliases to THIS and THAT respectively
            if i == '0': seg = 'this'
            elif i == '1': seg = 'that'
            else: print('Invalid pointer segment, expected 0 (THIS) or 1 (THAT)!')
            out.writelines([
                '@SP',
                'D=M',
                '@{}'.format(self.segments(seg)),
                'M=D'
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

if __name__ == '__main__':
    result = open(output)
    s = Stack(result)
    with open(file) as f:
        line = f.readline()
        while line:
            s.translate_line(line)

    result.close()
