from processor import Processor
import sys

def main():
    try:
        source_code_file_name = sys.argv[1]
    except:
        source_code_file_name = 'human-code.txt'
        # source_code_file_name = 'human-code-2.txt'

    code_file = file(source_code_file_name, 'r')
    initial_values_file = file('./initial_values_matrix.txt', 'r')
    # initial_values_file = file('./initial_values_fibo.txt', 'r')
    processor = Processor(code_file, initial_values_file)
    processor.run()

if __name__ == "__main__":
    main()
