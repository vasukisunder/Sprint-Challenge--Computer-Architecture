import sys

program_filename = sys.argv[1]

ADD = 0b10100000
SUB = 0b10100001
MUL = 0b10100010
CMP = 0b10100111
CALL = 0b01010000
RET = 0b00010001
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
HLT = 0b00000001
LDI = 0b10000010
PUSH = 0b01000101
POP = 0b01000110
EQUAL = 0b001
GREATER = 0b010
LESS = 0b100


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc = 0
        self.commands = {
            0b00000001: self.HLT,
            0b10000010: self.LDI,
            0b01000111: self.PRN,
            0b10100010: self.MUL,
            0b01000101: self.PUSH,
            0b01000110: self.POP,
            0b10100000: self.ADD,
            0b01010000: self.CALL,
            0b00010001: self.RET,
            0b10100111: self.CMP,
            0b01010100: self.JMP,
            0b01010101: self.JEQ,
            0b01010110: self.JNE

        }
        self.flag = 0
        self.address = 0
        self.reg[6] = 0xF4
        self.running = True
    
    def HLT(self):
        self.pc += 1
        self.running = False
        sys.exit()

    def LDI(self):
        reg_idx = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)
        self.reg[reg_idx] = value

        self.pc += 3

    def PRN(self):
        reg_idx = self.ram_read(self.pc + 1)
        print(self.reg[reg_idx])

        self.pc += 2

    def ADD(self):
        num_1 = self.reg[self.ram_read(self.pc + 1)]
        num_2 = self.reg[self.ram_read(self.pc + 2)]

        self.reg[self.ram_read(self.pc + 1)] = (num_1 + num_2)

        self.pc += 3

    def SUB(self):
        num_1 = self.reg[self.ram_read(self.pc + 1)]
        num_2 = self.reg[self.ram_read(self.pc + 2)]

        self.reg[self.ram_read(self.pc + 1)] = (num_1 - num_2)

        self.pc += 3

    def MUL(self):
        num_1 = self.reg[self.ram_read(self.pc + 1)]
        num_2 = self.reg[self.ram_read(self.pc + 2)]

        self.reg[self.ram_read(self.pc + 1)] = (num_1 * num_2)

        self.pc += 3

    def PUSH(self):
        self.reg[6] -= 1
        reg_num = self.ram_read(self.pc + 1)
        value_to_push = self.reg[reg_num]
        stack_address = self.reg[6]
        self.ram_write(value_to_push, stack_address)
        self.pc += 2

    def POP(self):
        value_to_pop = self.ram_read(self.reg[6])
        self.reg[6] += 1
        reg_num = self.ram_read(self.pc + 1)
        self.reg[reg_num] = value_to_pop
        self.pc += 2

    def CALL(self):
        return_address = self.pc + 2
        self.reg[6] -= 1
        self.ram[self.reg[6]] = return_address
        self.pc = self.reg[self.ram_read(self.pc + 1)]

    def RET(self):
        self.pc = self.ram[self.reg[6]]
        self.reg[6] += 1

    def CMP(self):
        reg_1 = self.reg[self.ram_read(self.pc + 1)]
        reg_2 = self.reg[self.ram_read(self.pc + 2)]
        if reg_1 < reg_2:
            self.flag = LESS
        elif reg_1 > reg_2:
            self.flag = GREATER
        else:
            self.flag = EQUAL
        self.pc += 3

    def JMP(self):
        jump_to_position = self.ram_read(self.pc + 1)
        self.pc = jump_to_position

    def JEQ(self):
        if self.flag == EQUAL:
            self.pc = self.reg[self.ram_read(self.pc + 1)]
        else:
            self.pc += 2

    def JNE(self):
        if self.flag != EQUAL:
            self.pc = self.reg[self.ram_read(self.pc + 1)]

        else:
            self.pc += 2

    def ram_read(self, MAR):
        return self.ram[MAR]

    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""

        self.address = 0

        try:
            with open(program_filename) as f:

                for line in f:
                    line = line.split('#')
                    line = line[0].strip()
                    if line == '':
                        continue

                    value = int(line, 2)
                    # print(value)

                    self.ram[self.address] = value

                    self.address += 1

        except FileNotFoundError:
            print(
                f"The file {sys.argv[1]} does not exist. Please enter a valid file name.")
            sys.exit()

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] > self.reg[reg_b]:
                self.flag = GREATER
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flag = LESS
            else:
                self.flag = EQUAL
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        while self.running:
            IR = self.ram_read(self.pc)
            if IR in self.commands:
                self.commands[IR]()