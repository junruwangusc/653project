import operator
import os

channel_num = 16 #define the channel num according to HBM
# every channel is 512MB 
# 512M = 536870912
# 512M * 30/32 = 503316480
# 512M * 31/32 = 520093696
blocksize = 536870912
vector_offset = blocksize * 30 // 32
result_offset = blocksize * 31 // 32

def memory_start_address():
    matrix_start_addr = []
    vector_start_addr = []
    result_start_addr = [] # all in decimal
    for i in range(channel_num):
        matrix_start_addr.append(int(i*blocksize))
        vector_start_addr.append(int(i*blocksize+vector_offset))
        result_start_addr.append(int(i*blocksize+result_offset))
    return matrix_start_addr, vector_start_addr, result_start_addr

def output_processed_file(file_name, block_index, r_c_addr):
    output_dir = "../proceeded_data_sets"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file_name = output_dir+"/"+file_name+"_"+str(block_index)+".txt"
    out_file = open(output_file_name, mode='w')
    for data in r_c_addr:
        print(data[0], data[1], data[2], file=out_file)
    return 0


def readin(file_name):
# in_file is string of the dataset file name   
    file_path = "../data_sets/" + file_name
    edges = []
    in_file = open(file_path, mode='r')
    lines=in_file.readlines()
    for line in lines:
        lineData=line.split(' ')    # split by " "
        if( (lineData[0] != "#") and str.isdigit(lineData[0]) ):
            edges.append((int(lineData[0]),int(lineData[1])))
    edges = sorted(edges, key=operator.itemgetter(0,1))
    #sort the edges first by the row then the column
    row_num = edges[len(edges)-1][0]
    row_block_size = row_num // channel_num #round down
    row_thrshld = []
    for i in range(channel_num-1):
        row_thrshld.append((i+1)*row_block_size)
        # totally 15 threshold needed
    print("row_thrshld=",row_thrshld)
    matrix_start_addr, vector_start_addr, result_start_addr = memory_start_address()

    current_block = 0
    r_c_addr = [] # make a new list of row column and address
    accum_count = 0 # the order of the edge in the corresponding block
    for edge in edges: # edge is a tuple
        if(current_block != (channel_num-1)):
            if(edge[0] >= row_thrshld[current_block]):
                #print("current_block=",current_block)
                current_block += 1
                accum_count = 0
                output_processed_file(file_name, current_block, r_c_addr)
                r_c_addr.clear() # clear the block data
        addr_t = accum_count*16 + matrix_start_addr[current_block] # each matrix data needs 16 bytes memory space
        accum_count += 1
        r_c_addr.append((edge[0], edge[1], addr_t))

    return edges

def main():
    file_name = "email-Eu-core.txt"
    data_in = readin(file_name)
    print(memory_start_address())
    #print(data_in)


if __name__ == '__main__':
    main()

