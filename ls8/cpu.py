import sys
import os

class CPU:
    """Main CPU class."""

    def __init__(self, bits = 8):
        """Construct a new CPU."""
        self.memory_size = pow(2, bits)
        self.max_value = self.memory_size - 1

        #State
        self.running = True

        #Arch
        self.ram = ['0b0'] * self.memory_size

        self.num_registers = bits
        self.reg = [0] * self.num_registers

        #Stack
        self.SP = self.num_registers - 1
        self.reg[self.SP] = 0xf4 #F4 hex

        #PC - Program counter = this will point to 1st byte of running instructions
        self.pc = 0

        self.load()

        self.instructions = {
            0b10000010: "LDI",
            0b01000111: "PRN",
            0b00000001: "HLT",
            0b10100010: "MUL",
            0b01000101: "PUSH",
            0b01000110: "POP"
        }

    def load(self):

        address = 0

        #filepath 
        try:
            filename = sys.argv[1]
        except:
            filename = 'stack.ls8'

        cur_path = os.path.dirname(__file__)

        new_path = os.path.relpath(f'examples/{filename}', cur_path)

        #load
        with open(new_path) as f:
            for line in f:
                line = line.strip()
                temp = line.split()

                if len(temp) == 0:
                    continue
                if temp[0][0] == '#':
                    continue

                try:
                    line = int(temp[0], 2)
                    self.ram[address] = line

                except ValueError:
                    print(f"Bad Num: {temp[0]}")
                except IndexError:
                    print(f"No addy at index {address}")
                address += 1
        for line in self.ram:
            print(line)

       

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] = (self.reg[reg_a] + self.reg[reg_b]) & self.max_value
        elif op == "MUL":
            #255 is max_value mask
            self.reg[reg_a] = (self.reg[reg_a] * self.reg[reg_b]) & self.max_value
        else:
            raise Exception("Unsupported ALU operation")

    def mul(self):
        self.alu("MUL", self.ram_read(self.pc+1), self.ram_read(self.pc+2))


    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ram_read(self, pc): 
        value = self.ram[pc]
        return value

    def ram_write(self, pc, value):
        self.ram[pc] = value
        return (pc, value)

    # def save_reg(self, reg, value):
    #     self.reg[reg] = value
    #     self.pc += 3 

    def current_reg(self):
        return self.ram_read(self.pc + 1)

    # def current_value(self):
    #     return self.ram_read(self.pc + 2)

    def ldi(self):
        int_value = self.ram_read(self.pc + 2)
        self.reg[self.current_reg()] = int_value & self.max_value

    def prn(self):
        print(self.reg[self.current_reg()])


    def hlt(self): 
        self.running = False

    def pop(self):        
        self.reg[self.current_reg()] = self.ram_read(self.reg[self.SP])
        self.reg[self.SP] += 1

    def push(self):        
        self.reg[self.SP] -= 1
        self.ram[self.reg[self.SP]] = self.reg[self.current_reg()]

    def run(self):
        """Run the CPU."""
        while self.running:
            ir = self.ram_read(self.pc)
            #methods move ptr to next instruction
            size = ir >> 6
            shift = size + 1

            if ir in self.instructions:

                instruction = getattr(CPU, self.instructions[self.ram_read(self.pc)].lower())
                instruction(self)
                print(instruction)
                self.pc += shift 

            else:
                print("Bad instructions")
                self.running = False
                self.pc = 0
                return
                
pc = CPU()
pc.trace()
pc.run()