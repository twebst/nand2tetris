# init with reserved symbols (virtual registers, pointers and mmio locations)
$symbol_table = {
    'R0' => 0,
    'R1' => 1,
    'R2' => 2,
    'R3' => 3,
    'R4' => 4,
    'R5' => 5,
    'R6' => 6,
    'R7' => 7,
    'R8' => 8,
    'R9' => 9,
    'R10' => 10,
    'R11' => 11,
    'R12' => 12,
    'R13' => 13,
    'R14' => 14,
    'R15' => 15,
    'SP' => 0,
    'LCL' => 1,
    'ARG' => 2,
    'THIS' => 3,
    'THAT' => 4,
    'SCREEN' => 16384,
    'KBD' => 24576
}

# the memory location to start adding new variables at (initially after R15)
$mem_loc = 16

def comp(c)
  case c
  when '0'
    return '0101010'
  when '1'
    return '0111111'
  when '-1'
    return '0111010'
  when 'D'
    return '0001100'
  when 'A'
    return '0110000'
  when 'M'
    return '1110000'
  when '!D'
    return '0001101'
  when '!A'
    return '0110001'
  when '!M'
    return '1110001'
  when '-D'
    return '0001111'
  when '-A'
    return '0110011'
  when '-M'
    return '1110011'
  when 'D+1', '1+D'
    return '0011111'
  when 'A+1', '1+A'
    return '0110111'
  when 'M+1', '1+M'
    return '1110111'
  when 'D-1'
    return '0001110'
  when 'A-1'
    return '0110010'
  when 'M-1'
    return '1110010'
  when 'D+A', 'A+D'
    return '0000010'
  when 'D+M', 'M+D'
    return '1000010'
  when 'D-A'
    return '0010011'
  when 'D-M'
    return '1010011'
  when 'A-D'
    return '0000111'
  when 'M-D'
    return '1000111'
  when 'D&A', 'A&D'
    return '0000000'
  when 'D&M', 'M&D'
    return '1000000'
  when 'D|A', 'A|D'
    return '0010101'
  when 'D|M', 'M|D'
    return '1010101'
  else
    puts "COMP ERROR with comp: %s" % c
    return 'COMP ERROR'
  end
end

def dest(d)
  case d
  when nil
    return '000'
  when 'M'
    return '001'
  when 'D'
    return '010'
  when 'DM', 'MD'
    return '011'
  when 'A'
    return '100'
  when 'AM', 'MA'
    return '101'
  when 'AD', 'DA'
    return '110'
  when 'ADM', 'AMD', 'MAD', 'MDA', 'DAM', 'DMA'
    return '111'
  else
    puts "DEST ERROR with dest: %s" % d
    return 'DEST ERROR'
  end
end

def jump(j)
  case j
  when nil
    return '000'
  when 'JGT'
    return '001'
  when 'JEQ'
    return '010'
  when 'JGE'
    return '011'
  when 'JLT'
    return '100'
  when 'JNE'
    return '101'
  when 'JLE'
    return '110'
  when 'JMP'
    return '111'
  else
    puts "JUMP ERROR with jump: %s" % j
    return 'JUMP ERROR'
  end
end

def translate(ins)
    if ins.match? /@{1}[0-9]+/
      return "%016b" % ins[1..]
    elsif symbol = ins.match(/^@{1}(?<symbol>[a-zA-Z_\.\$:][a-zA-Z\d_\.\$:]*)$/)
      unless $symbol_table[symbol[:symbol]]
        $symbol_table[symbol[:symbol]] = $mem_loc
        $mem_loc += 1
      end
      return "%016b" % $symbol_table[symbol[:symbol]]
    else
        d,c,j = nil

        has_dest = ins.include? '='
        has_jmp = ins.include? ';'

        if has_dest && has_jmp
            instructions = ins.split /[=;]/
            if instructions.length == 3
                d = dest(instructions[0].strip)
                c = comp(instructions[1].strip)
                j = jump(instructions[2].strip)
            else
                puts "ERROR with instruction: %s" % ins
            end
        elsif has_dest
            instructions = ins.split '='
            if instructions.length == 2
                d = dest(instructions[0].strip)
                c = comp(instructions[1].strip)
                j = jump(nil)
            else
                puts "ERROR with instruction: %s" % ins
            end
        elsif has_jmp
            instructions = ins.split ';'
            if instructions.length == 2
                d = dest(nil)
                c = comp(instructions[0].strip)
                j = jump(instructions[1].strip)
            else
                puts "ERROR with instruction: %s" % ins
            end
        else
            d = dest(nil)
            c = comp(ins.strip)
            j = jump(nil)
        end

        return "111%s%s%s" % [c,d,j]
    end
end

def build_sym_table(instructions)
  next_instruction = 0
  instructions.each do |line|
      if label = line.match(/^\s*\((?<label>[a-zA-Z\d_\.\$:]+)\)\s*$/)
        unless $symbol_table[label[:label]]
          $symbol_table[label[:label]] = next_instruction
        else
          puts 'ERROR: label %s already in symbol table' % label[:label]
        end
      else
        next_instruction += 1
      end
  end
end

begin
  input = File.open(ARGV[0])
  # filter out comments and blank lines
  # instructions = input.each_line.select { |line| !((line.match? /^\s*\/{2}.*$/) || (line.match? /^\s*$/)) }
  # strip comments and whitespace, and then filter empty lines
  instructions = input.each_line.map do |line|
    line.gsub(/\s*\/{2}.*/, '').strip
  end
  instructions = instructions.each.select { |line| !line.empty? }
  input.close

  # first pass, label only symbol table
  build_sym_table(instructions)

  # now filter out labels
  instructions.select! { |line| !line.match(/^\s*\([a-zA-Z\d_\.\$:]+\)\s*$/) }

  output = File.open("result.hack", "w+")

  # second pass
  instructions.each do |instruction|
    output.puts translate(instruction.strip)
  end

  output.close
rescue IOError => e
  puts e
ensure
  input.close unless input.nil?
  output.close unless output.nil?
end
