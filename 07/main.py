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

        self.arops = {
            'add': '+',
            'sub': '-',
            'and': '&',
            'or': '|'
        }

        self.comp = {
            'eq': 'JEQ',
            'gt': 'JGT',
            'lt': 'JLT'
        }

        self.unop = set(['neg', 'not'])

        self.label_count = 0

    def generate_label(self):
        l = self.label_count
        self.label_count += 1
        return 'L{}'.format(l)

    def inc_sp(self):
        self.out.writeline([
            '// increment sp',
            '@SP',
            'M=M+1'
        ])

    def dec_sp(self):
        self.out.writeline([
            '// decrement sp',
            '@SP',
            'M=M-1'
        ])

    def push(self, seg, i):
        if seg == 'constant':
            self.out.writelines([
                # load a constant into the current SP RAM location
                '@{}'.format(i),
                'D=A',
                '@SP',
                'M=D'
            ])

        elif seg in self.segments:
            self.out.writelines([
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
            self.out.writelines([
                '@static.{}'.format(i),
                'D=M',
                '@SP',
                'M=D'
            ])

        elif seg == 'pointer': # pointer 0 and 1 are aliases to THIS and THAT respectively
            if i == '0': seg = 'this'
            elif i == '1': seg = 'that'
            else: print('Invalid pointer segment, expected 0 (THIS) or 1 (THAT)!')
            self.out.writelines([
                '@{}'.format(self.segments(seg)),
                'D=M',
                '@SP',
                'M=D'
            ])

        else: print('Invalid push! Got: ', seg, i)

        self.inc_sp()

    def pop(self, seg, i):
        if seg in self.segments:
            # there might be a more efficient way to do this, but for now use the virtual register R13 to store seg + i
            self.out.writelines([
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
            self.out.writelines([
                '@SP',
                'D=M',
                '@static.{}'.format(i),
                'M=D'
            ])

        elif seg == 'pointer': # pointer 0 and 1 are aliases to THIS and THAT respectively
            if i == '0': seg = 'this'
            elif i == '1': seg = 'that'
            else: print('Invalid pointer segment, expected 0 (THIS) or 1 (THAT)!')
            self.out.writelines([
                '@SP',
                'D=M',
                '@{}'.format(self.segments(seg)),
                'M=D'
            ])

        self.dec_sp()

    def operation(self, op):
        if op in self.arops:
            self.out.writelines([
                '@SP',
                'M=M-1',
                'A=M',
                'D=M',
                'A=A-1',
            ])

            if op == 'sub': self.out.writeline('D=M-D')
            else: self.out.writeline('D=D{}M'.format(self.binops[op]))
            self.out.writeline('M=D')

        elif op in self.cops:
            # x < y, x > y, and x == y are all JMP instructions, based on the result of x - y
            l1 = self.generate_label()
            l2 = self.generate_label()
            self.out.writelines([
                '@SP',
                'M=M-1',
                'A=M',
                'D=M',
                'A=A-1',
                'D=M-D',
                '@{}'.format(l1),
                'D;{}'.format(cops[op]),
                '@SP',
                'A=M',
                'M=0',
                '@{}'.format(l2),
                '0;JMP',
                '({})'.format(l1),
                '@SP',
                'A=M',
                'M=1',
                '({})'.format(l2),
            ])

        elif op in self.unop:
            self.out.writelines([
                '@SP',
                'A=M-1',
                'M={}M'.format('!' if op == 'not' else '-'),
            ])
        else:
            print('INVALID OP!', op)

    def translate_line(self, line):
        # self.out.writeline("// {}".format(line)); # add a comment for each vm instruction
        tokens = line.split()
        if tokens[0] == 'push':
            self.push(tokens[0], tokens[1])
        elif tokens[0] == 'pop':
            self.pop(tokens[0], tokens[1])
        else:
            self.operation(tokens[0))

    def infinite_loop(self):
        l = self.generate_label()
        self.out.writelines([
            '@{}'.format(l),
            '({})'.format(l),
            '0;JMP'
        ])

if __name__ == '__main__':
    result = open(output)
    s = Stack(result)
    with open(file) as f:
        line = f.readline()
        while line:
            s.translate_line(line)
        s.infinite_loop()

    result.close()
