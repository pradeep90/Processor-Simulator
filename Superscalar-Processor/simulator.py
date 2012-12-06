from processor import Processor
import sys

def main():
    try:
        source_code_file_name = sys.argv[1]
    except:
        print 'using default test file'
        source_code_file_name = './sample_Code/testcase-3-in-hex.txt'

    code_file = file(source_code_file_name, 'r')
    initial_values_file = file('./initial_values.txt', 'r')
    processor = Processor(code_file, initial_values_file)
    processor.run()

if __name__ == "__main__":
    main()
