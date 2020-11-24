# 11.23.2020
# 这个文件增加了对vector data的degree统计
import operator
import os
import random

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

def output_processed_file(file_name, block_index, r_c_addr, first_row_in_block):
    file_name_without_extension=file_name.split(".")[0]
    output_dir = "../proceeded_data_sets/"+file_name_without_extension
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file_name = output_dir+"/"+file_name_without_extension+"_"+str(block_index)+".txt"
    out_file = open(output_file_name, mode='w')
    for data in r_c_addr:
        print(data[0], data[1], data[2], file=out_file)
    output_file_name = output_dir+"/"+file_name_without_extension+"_firstrowinblock"+".txt"
    out_file = open(output_file_name, mode='w')
    for data in first_row_in_block:
        print(data, file=out_file)
    out_file.close()
    return 0


def sort_graph(input_file):
    edges = []
    i = 0
    with open(input_file) as f:
        for line in f:
            i += 1
            l = line.split('\n')[0].split('\t')
            if len(l) < 2:
              print(i)
            edges.append([int(l[0]), int(l[1])])
    edges.sort()
    # with open(edge_file, 'wt') as f:
    #     f.write(str(len(edges)) + '\n')
    #     for e in edges:
    #         f.write(str(e[0]) + ' ' + str(e[1]) + '\n')
    return edges


def generate_node_array(sorted_edge):
    max_node = max(max([e[1] for e in sorted_edge]), sorted_edge[-1][0])
    node_array = []
    ptr = 0
    i = 0
    j = 0
    # max_node is also total number of node minus one
    for i in range(max_node+1):
        if ptr >= len(sorted_edge):
            node_array.append([-1,0])
            continue
        # when nodes are skipped, i.e. not a source of an edge
        if ptr < len(sorted_edge) and sorted_edge[ptr][0] > i:
            node_array.append([-1,0])
            continue
        start = ptr
        count = 0
        # count total number of outgoing edges of a node
        while ptr < len(sorted_edge) and sorted_edge[ptr][0] == i:
            count += 1
            ptr += 1
        node_array.append([start, count])
#     with open(filename, 'wt') as f:
#         f.write(str(len(node_array)) + '\n')
#         for node in node_array:
#             f.write(str(node[0]) + " " + str(node[1]) + '\n')
    # print(node_array)
    for node in node_array:
        node[0] = j
        j = j + 1
    # print(node_array)
    return node_array

def output_generated_vector(file_name, block_index, r_v_addr):
    file_name_without_extension=file_name.split(".")[0]
    output_dir = "../proceeded_data_sets/"+file_name_without_extension
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file_name = output_dir+"/"+file_name_without_extension+"_vector_"+str(block_index)+".txt"    
    out_file = open(output_file_name, mode='w')
    for data in r_v_addr:
        print(data[0], data[1], data[2], data[3], file=out_file)
    out_file.close()
    return 0


def readin(file_name):
    #first based on the input file, we generate the sorted edge list and sorted node array
    file_path_1 = "../data_sets/" + file_name
    sorted_edges = sort_graph(file_path_1)
    node_array_with_ID_degree = generate_node_array(sorted_edges)

# in_file is string of the dataset file name   
    file_path = "../data_sets/" + file_name
    max_row_of_vec = 0
    edges = []
    in_file = open(file_path, mode='r')
    lines=in_file.readlines()
    for line in lines:
        lineData=line.split('\t')    # split by " "
        if( (lineData[0] != "#") and str.isdigit(lineData[0]) ):
            edges.append((int(lineData[0]),int(lineData[1])))
            max_row_of_vec = max(int(lineData[1]), max_row_of_vec)
    in_file.close()
    edges = sorted(edges, key=operator.itemgetter(0,1))
    #print(edges)
    #sort the edges first by the row then the column
    non_zero_num = len(edges)#edges are also the number of non-zeros
    row_num = edges[len(edges)-1][0] + 1 # 0, 1, .... max row index
    max_row_of_vec = max(max_row_of_vec, row_num)
    row_block_size = non_zero_num // channel_num #round down, number if elements
    vec_block_size = max_row_of_vec // channel_num
    non_zero_thrshld = []
    row_thrshld = []
    for i in range(channel_num-1):
        non_zero_thrshld.append((i+1)*row_block_size)
        row_thrshld.append((i+1)*vec_block_size)
        # totally 15 threshold needed
    print("non_zero_thrshld=",non_zero_thrshld)
    matrix_start_addr, vector_start_addr, result_start_addr = memory_start_address()
    #---------------------------------------------------------------------------------
    # matrix partiton 
    current_block = 0
    r_c_addr = [] # make a new list of row column and address
    accum_count = 0 # the order of the edge in the corresponding block
    accum_non_zero = 0 # the order of the edge among all the non zeros
    last_row = -1 # last row
    first_row_in_block = [0]
    for edge in edges: # edge is a tuple
        if(current_block != (channel_num-1)):
            if(edge[0] != last_row): # the row changes
                if(accum_non_zero >= non_zero_thrshld[current_block]):
                    #print("current_block=",current_block)
                    first_row_in_block.append(edge[0])
                    accum_count = 0
                    output_processed_file(file_name, current_block, r_c_addr, first_row_in_block)
                    r_c_addr.clear() # clear the block data
                    current_block += 1
        accum_non_zero += 1
        addr_t = accum_count*16 + matrix_start_addr[current_block] # each matrix data needs 16 bytes memory space
        accum_count += 1
        r_c_addr.append((edge[0], edge[1], addr_t))
    output_processed_file(file_name, current_block, r_c_addr, first_row_in_block)
    #---------------------------------------------------------------------------------
    # vector generation
    current_block = 0
    r_v_addr = [] # vector element value, row index, address
    accum_count = 0 # the order of the vector element in the corresponding block
    for r in range(max_row_of_vec+1): #0, 1, .... max row index+1-1
        if(current_block != (channel_num-1)):
            if(r >= row_thrshld[current_block]):
                #print("current_block=",current_block)
                accum_count = 0
                output_generated_vector(file_name, current_block, r_v_addr)
                # print(r_v_addr)
                # print("This part is end" + '\n')
                r_v_addr.clear() # clear the block data
                current_block += 1
        addr_t = accum_count*16 + vector_start_addr[current_block] # each matrix data needs 16 bytes memory space
        accum_count += 1
        v_temp = random.randint(1,9) # generate a small int value btw 1~9
        r_v_addr.append((r, v_temp, addr_t, node_array_with_ID_degree[r-1][1]))

        # print(r_v_addr)
        # print("This part is end" + '\n')
    output_generated_vector(file_name, current_block, r_v_addr)
    #---------------------------------------------------------------------------------
    return row_num, edges



def main():
    file_name = "roadNet-CA.txt"
    row_input, edge_input = readin(file_name)
    #print(memory_start_address())
    #print(data_in)


if __name__ == '__main__':
    main()

