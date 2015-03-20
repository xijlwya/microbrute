import argparse

def main():
    parser = argparse.ArgumentParser(description='Manipulate Microbrute *.mbseq files.')
    parser.add_argument('source', type=str, help='the source file that\'s to be manipulated')
    parser.add_argument('-o','--output', type=str, help='The file the manipulation is written to, if omitted, the changes happen in place')
    parser.add_argument('-i', '--index', nargs='*', type=int, help='A list of numbers form 1 to 8 indicating which sequence is to be manipulated')
    parser.add_argument('-t', '--transpose', action='store_true', help='only transposes the sequences and does not equalize them')
    parser.add_argument('-r', '--reference', type=int, help='the MIDI note value to which the sequences will be equalized (or transposed by)')

    args = parser.parse_args()
    source = args.source
    if source.split('.')[-1] != 'mbseq':
        print('Invalid file type. This works with *.mbseq files generated with the MicroBrute Connection software')
        raise IOError
    
    data = read_sequences(source)
        
    if args.output:
        splitted_output = args.output.split('.')
        if len(splitted_output) is 1:
            output = args.output
        elif len(splitted_output) is 2:
            output = splitted_output[0]
        else:
            print('Output must be a *.mbseq file. If no file ending is specified, .msbseq will be added automatically')
            raise IOError
    else:
        output = source

    if args.index:
        temp = list(args.index)
        for k in range(1,9):
            try:
                temp.remove(k)
            except ValueError:
                pass
        if temp:
            print('Invalid sequence choice, must be numbers between 1 to 8, each number only once respectively')
            raise IOError
        else: index = args.index
    else:
        index = range(1,9)
    
    if args.transpose and args.reference:
        reference = args.reference
    elif args.reference:
        if args.reference > 125:
            print('Reference must be smaller than 125')
            raise IOError
        elif args.reference < 1:
            print('Reference must be bigger than 1')
            raise IOError
        else:
            reference = args.reference
    else:
        reference = 60
            
    if args.transpose:
        write_sequences(multi_transpose(data, reference, index), filename=output)
        print('Transpose complete.')
    else:
        write_sequences(multi_equalize(data, reference, index), filename=output)
        print('Equalize complete.')
    

def read_sequences(filename):
    sequences_list = []
    
    with open(filename, 'r') as f:
        for line in f: #read the 8 lists of numbers and x's 
            value_list = line.split(' ')
            value_list[0] = value_list[0][2:] #strip the colon and sequence number
            value_list[-1] = value_list[-1].strip('\r\n') #strip the final line feed
            
            temp_list = []
            for val in value_list:
                try:
                    temp_list.append(int(val))
                except(ValueError):
                    temp_list.append('x')
            sequences_list.append(temp_list)
            
    return tuple(sequences_list)
    
    
    
def multi_transpose(seq_tuple, semitones, index_list=[1,2,3,4,5,6,7,8]):
    return_list = [[] for __ in range(8)]
    
    for tup in enumerate(seq_tuple, 1):
        num, seq = tup
        if num in index_list:
            return_list[num - 1] = transpose(seq, semitones)
        else:
            return_list[num - 1] = seq
    
    return tuple(return_list)
    
def multi_equalize(seq_tuple, reference_note=60, index_list=[1,2,3,4,5,6,7,8]):
    return_list = [[] for __ in range(8)]
    
    for tup in enumerate(seq_tuple, 1):
        num, seq = tup
        if num in index_list:
            try:
                return_list[num - 1] = equalize(seq, reference_note)
            except ValueError as e:
                print('Sequence ' + str(num) + ' unchanged:')
                print(e.message)
                return_list[num - 1] = seq
        else:
            return_list[num - 1] = seq
    
    return tuple(return_list)
    
def equalize(note_list, reference_note=60):
    return transpose(note_list, reference_note - find_first(note_list))

def transpose(note_list, semitones):
    if semitones > 0:
        if 125 - find_highest(note_list) < semitones:
            raise ValueError('Transpose would exceed MIDI value 125')
    else:
        if find_lowest(note_list) - 1 < abs(semitones):
            raise ValueError('Transpose would undercut MIDI value 1')

    temp_list = []
    for val in note_list:
        if val is not 'x':
            temp_list.append(val + semitones)
        else:
            temp_list.append('x')
    return temp_list

def find_first(note_list):
    for val in note_list:
        if val is not 'x':
            return val
    return None

def find_highest(note_list):
    temp = list(note_list) #to avoid in-place manipulation
    temp.sort()
    if 'x' in temp:
        temp = temp[:temp.index('x')]
    return temp[-1]
    
def find_lowest(note_list):
    temp = list(note_list) #to avoid in-place manipulation
    temp.sort()
    if 'x' in temp:
        temp = temp[:temp.index('x')]
    return temp[0]

def write_sequences(sequences, filename='sequences.mbseq'):
    with open(filename,'w') as f:
        for tup in enumerate(sequences, 1):
            num, seq = tup
            f.write(str(num) + ':')
            
            for entry in seq[0:-1]:
                f.write(str(entry) + ' ')
            f.write(str(seq[-1]) + '\r\n')

def file_equalize(filename):
    write_sequences(multi_equalize(read_sequences(filename)),filename)

if __name__ == '__main__':
    main()
