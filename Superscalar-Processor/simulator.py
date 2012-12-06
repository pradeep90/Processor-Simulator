from Processor import Processor
import sys

def main():
    try:
        file_name = sys.argv[1]
    except:
        print 'using default test file'
        file_name = './sample_Code/testcase-3_reduced.txt'
    hex_code_file = file(file_name, 'r')
    initial_state_file = file('./initial_state.txt', 'r')
    mips_processor = Processor(hex_code_file, initial_state_file)
    mips_processor.run()

if __name__ == "__main__":
    main()
