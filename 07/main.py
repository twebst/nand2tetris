#!/usr/bin/python
import os
import sys
import traceback

class Stack:
    def __init__(self, output):
        self.out = output

        # init the SP to 256 with the following hack instructions
        self.out.writelines([
            '// init SP to 256\n',
            '@256\n',
            'D=A\n',
            '@SP\n',
            'M=D\n'
        ])

        self.segments = {
            'local': 'LCL',
            'argument': 'ARG',
            'this': 'THIS',
            'that': 'THAT',
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

        self.comp_opp = {
            'eq': 'JNE',
            'gt': 'JLE',
            'lt': 'JGE'
        }

        self.unop = set(['neg', 'not'])

        self.label_count = 0

    def generate_label(self):
        l = self.label_count
        self.label_count += 1
        return 'L{}'.format(l)

    def inc_sp(self):
        self.out.writelines([
            '// increment sp\n',
            '@SP\n',
            'M=M+1\n'
        ])

    def dec_sp(self):
        self.out.writelines([
            '// decrement sp\n',
            '@SP\n',
            'M=M-1\n'
        ])

    def push(self, seg, i):
        if seg == 'constant':
            self.out.writelines([
                # load a constant into the current SP RAM location
                '\n// push constant\n',
                '@{}\n'.format(i),
                'D=A\n',
                '@SP\n',
                'A=M\n',
                'M=D\n'
            ])

        elif seg in self.segments:
            self.out.writelines([
                # offset with the segment address, load value into data register
                '\n// push segment: {} + {}\n'.format(seg, i),
                '@{}\n'.format(self.segments[seg]),
                'D=A\n',
                '@{}\n'.format(i),
                'A=A+D\n',
                'D=M\n',
                # load into SP location
                '@SP\n',
                'A=M\n',
                'M=D\n'
            ])

        elif seg == 'static': # assembly variables are static (16-255)
            self.out.writelines([
                '\n// push static\n',
                '@static.{}\n'.format(i),
                'D=M\n',
                '@SP\n',
                'A=M\n',
                'M=D\n'
            ])

        elif seg == 'pointer': # pointer 0 and 1 are aliases to THIS and THAT respectively
            if i == '0': seg = 'this'
            elif i == '1': seg = 'that'
            else: print('Invalid pointer segment, expected 0 (THIS) or 1 (THAT)!')
            self.out.writelines([
                '\n// push pointer THIS or THAT\n',
                '@{}\n'.format(self.segments[seg]),
                'D=M\n',
                '@SP\n',
                'A=M\n',
                'M=D\n'
            ])

        else: print('Invalid push! Got: ', seg, i)

        self.inc_sp()

    def pop(self, seg, i):
        if seg in self.segments:
            # there might be a more efficient way to do this, but for now use the virtual register R13 to store seg + i
            self.out.writelines([
                '\n// pop to segment: {} + {}\n'.format(seg, i),
                # calculate offseted segment location, and then store for later
                '@{}\n'.format(i),
                'D=A\n',
                '@{}\n'.format(self.segments[seg]),
                'D=D+A\n',
                '@R13\n',
                'M=D\n',
                # load value from SP
                '@SP\n',
                'A=M\n',
                'D=M\n',
                # retrieve and use address previously calculated
                '@R13\n',
                'A=M\n',
                'M=D\n'
            ])

        elif seg == 'static': # assembly variables are static (16-255)
            self.out.writelines([
                '\n// pop to static\n',
                '@SP\n',
                'A=M\n',
                'D=M\n',
                '@static.{}\n'.format(i),
                'M=D\n'
            ])

        elif seg == 'pointer': # pointer 0 and 1 are aliases to THIS and THAT respectively
            if i == '0': seg = 'this'
            elif i == '1': seg = 'that'
            else: print('Invalid pointer segment, expected 0 (THIS) or 1 (THAT)!')
            self.out.writelines([
                '\n// pop to pointer THIS or THAT\n',
                '@SP\n',
                'A=M\n',
                'D=M\n',
                '@{}\n'.format(self.segments[seg]),
                'M=D\n'
            ])

        self.dec_sp()

    def operation(self, op):
        if op in self.arops:
            self.out.writelines([
                '\n// {}\n'.format(op),
                '@SP\n',
                'M=M-1\n',
                'A=M\n',
                'D=M\n',
                'A=A-1\n',
            ])

            if op == 'sub': self.out.writelines(['D=M-D\n'])
            else: self.out.writelines(['D=D{}M\n'.format(self.arops[op])])
            self.out.writelines(['M=D\n'])

        elif op in self.comp:
            # x < y, x > y, and x == y are all JMP instructions, based on the result of x - y
            l1 = self.generate_label()
            l2 = self.generate_label()
            self.out.writelines([
                '\n// {}\n'.format(op),
                '@SP\n',
                'M=M-1\n',
                'A=M\n',
                'D=M\n',
                'A=A-1\n',
                'D=M-D\n',
                '@SP\n',
                'A=M-1\n',
                'M=0\n',
                '@{}\n'.format(l1),
                'D;{}\n'.format(self.comp_opp[op]),
                '@SP\n',
                'M=M-1\n',
                '({})\n'.format(l1),
            ])

        elif op in self.unop:
            self.out.writelines([
                '\n// {}\n'.format(op),
                '@SP\n',
                'A=M-1\n',
                'M={}M\n'.format('!' if op == 'not' else '-'),
            ])

        else: print('INVALID OP!', op)

    def translate_line(self, line):
        # self.out.writelines("// {}".format(line)); # add a comment for each vm instruction
        tokens = line.split()
        if tokens[0] == 'push':
            self.push(tokens[1], tokens[2])
        elif tokens[0] == 'pop':
            self.pop(tokens[1], tokens[2])
        else:
            self.operation(tokens[0])

    def infinite_loop(self):
        l = self.generate_label()
        self.out.writelines([
            '\n// END (infinite loop)\n',
            '@{}\n'.format(l),
            '({})\n'.format(l),
            '0;JMP\n'
        ])

if __name__ == '__main__':
    def ignore(line): return not line or line.startswith('//')

    if len(sys.argv) < 2:
        print('Input file expected! Received no arguments.')
    else:
        try:
            in_path = os.path.abspath(sys.argv[1])
            out_path = '{}.asm'.format(in_path.split('.')[0])
            inp = open(in_path, 'r')
            out = open(out_path, 'w')

            s = Stack(out)
            l_num = 0
            lines = list(filter(lambda l: not ignore(l), map(lambda l: l.strip(), inp.readlines())))
            inp.close()

            for line in lines:
                s.translate_line(line)
                l_num += 1
            s.infinite_loop()

            # with inp as f:
            #     while True:
            #         line = f.readline().strip()
            #         if not line: break
            #         if not line.startswith('//'): s.translate_line(line)
            #         l_num += 1
            #     s.infinite_loop()

            out.close()
        except Exception as e:
            print('Failed at line:', l_num, line)
            traceback.print_exception(type(e), e, e.__traceback__)
        finally:
            if inp: inp.close()
            if out: out.close()
