# This program is for generating the result vector as well as the corresponding address

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
result_start_addr = []
inputbuffer_depth = 32

def result_addr_generate(result_val, block_num, row_num, fisrt_row_of_the_block):
    #print("block_num=",block_num)
    index = row_num - fisrt_row_of_the_block
    block_start_addr = int(block_num*blocksize+result_offset)
    addr_t = block_start_addr + index*8 # a result vector needs to store the value and row 
    return row_num, result_val, addr_t, block_num   

def readin(file_name):
    matrix_block_data = []
    #vector_total_Data = []
    vector_row_value_dict = {} # dictionary
    vector_row_addr_dict = {} # dictionary
    first_row_in_block = []
    file_name_without_extension=file_name.split(".")[0]
    for i in range(0,channel_num):
        matrix_file_path = "../proceeded_data_sets/" + file_name_without_extension
        vector_file_path = "../proceeded_data_sets/" + file_name_without_extension
        matrix_file = open(matrix_file_path+"/"+file_name_without_extension+"_"+str(i)+".txt", mode='r')
        vector_file = open(vector_file_path+"/"+file_name_without_extension+"_vector"+"_"+str(i)+".txt", mode='r')
        temp_matrix_block = []
        lines=matrix_file.read().splitlines()
        for line in lines:
            lineData=line.split(' ')    # split by " ", r_c_addr
            nums=[int(num) for num in lineData]
            temp_matrix_block.append(nums) # r_c_addr
        matrix_block_data.append(temp_matrix_block)

        lines=vector_file.read().splitlines()    
        for line in lines:
            lineData=line.split(' ')    # split by " ", r_c_addr
            nums=[int(num) for num in lineData]
            #vector_total_Data.append(lineData)  # r_v_addr
            vector_row_value_dict[nums[0]] = nums[1]
            vector_row_addr_dict[nums[0]] = nums[2]
    firstrowinblock_file = open("../proceeded_data_sets/"+file_name_without_extension+"/"+file_name_without_extension+"_firstrowinblock.txt", mode='r')
    lines=firstrowinblock_file.read().splitlines()
    for line in lines:
            nums=int(line)    # split by " ", r_c_addr
            first_row_in_block.append(nums)    
    # read files finished
    matrix_file.close()
    vector_file.close()
    firstrowinblock_file.close()
    return matrix_block_data, vector_row_value_dict, vector_row_addr_dict, first_row_in_block


def process_element(matrix_block_data, vector_row_value_dict, vector_row_addr_dict, fisrt_row_of_blocks):
    total_row_num = len(vector_row_value_dict)
    matrix_ptr = 0 # matrix data index in each block

    last_row = [-1 for i in range(channel_num)] # record last row in block 0~15
    current_row = [0 for i in range(channel_num)] # record current row in block 0~15
    result_val = [0 for i in range(total_row_num)] # record result vector
    result_row_finish = [0 for i in range(total_row_num)] # record whether the result of the row is finished
    finished_channel = [0 for i in range(total_row_num)] # avoid repetition subtraction
    result_out = []
    not_finished = 1
    while not_finished:
        buffered_matrix_data = [] # r_c_addr
        result_out = []
        for i in range(inputbuffer_depth):    
            if(not_finished==0):
                break
            #else:
            has_data = 0
            one_entry_matrix_data_of_channels = []
            for j in range(0,channel_num):
                if(len(matrix_block_data[j])>matrix_ptr): # not beyond the end
                    one_entry_matrix_data_of_channels.append(matrix_block_data[j][matrix_ptr]) # gather matrix data from all blocks
                    has_data += 1
                else:
                    one_entry_matrix_data_of_channels.append([-1, -1, -1]) # indicate the block is finishedi
            buffered_matrix_data.append(one_entry_matrix_data_of_channels)
            if has_data: 
                matrix_ptr += 1 # for next cycle
            else:
                not_finished = 0 # no matrix data fetched, end the data access
        vector_addr = [] # record the vector address request
        vector_value = [] # record the corresponding vector element value
        for i in range(len(buffered_matrix_data)): 
            for j in range(0,channel_num):
                temp_row = buffered_matrix_data[i][j][0]
                if(temp_row != -1): # if the row exists
                    current_row[j] = temp_row # record the current row in the blocks
                    vec_value_temp = vector_row_value_dict[temp_row] # get the corresponding data
                    vec_addr_temp = vector_row_addr_dict[temp_row] # get the corresponding addr
                    vector_value.append(vec_value_temp)
                    if vec_addr_temp not in vector_addr:
                        vector_addr.append(vec_addr_temp)
                    result_val[temp_row] += vec_value_temp*1 # because the non-zero matrix value is "1"
                    if( (current_row[j]!=last_row[j])and(last_row[j]!=-1) ): # if current_row != last_row and last_row exist
                        result_row_finish[last_row[j]] = 1 # since the last row is not the same as the current row
                        print("result_val=",result_val[last_row[j]])
                        result_out.append(result_addr_generate(result_val[last_row[j]], j, last_row[j], fisrt_row_of_blocks[j]))
                else: # if the row doesn't exist
                    if(result_row_finish[last_row[j]]==0):
                        result_row_finish[last_row[j]] = 1
            for j in range(0,channel_num): # detect the last row in each block
                if( (current_row[j]==last_row[j]) and last_row[j]!=-1):
                    if(result_row_finish[last_row[j]]==1 and finished_channel[j]==0):
                        finished_channel[j] = 1
                        #print("block ",i," is finished at row",last_row[i])
                        print("result_val=",result_val[last_row[j]])
                        result_out.append(result_addr_generate(result_val[last_row[j]], j, last_row[j], fisrt_row_of_blocks[j]))
            last_row = current_row[:] #shallow copy
            print("result_out=",result_out)
    return result_out


def output_generated_results(file_name, row_value_addr_channel):
    file_name_without_extension=file_name.split(".")[0]
    output_dir = "../proceeded_data_sets/"+file_name_without_extension
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file_name = output_dir+"/"+file_name_without_extension+"_result_inputbuffer.txt"    
    out_file = open(output_file_name, mode='w')
    for data in row_value_addr_channel:
        print(data[0], data[1], data[2], data[3], file=out_file)
    out_file.close()
    return 0



def get_matrix_data_operation(matrix_block_data, matrix_ptr_in):
    matrix_ptr = matrix_ptr_in # matrix data index in each channel
    not_finished = 1
    buffered_matrix_data = [] # r_c_addr
    for i in range(inputbuffer_depth):    
        if(not_finished==0):
            break
        #else:
        has_data = 0
        one_entry_matrix_data_of_channels = []
        for j in range(0,channel_num):
            if(len(matrix_block_data[j])>matrix_ptr): # not beyond the end
                one_entry_matrix_data_of_channels.append(matrix_block_data[j][matrix_ptr]) # gather matrix data from all blocks
                has_data += 1
            else:
                one_entry_matrix_data_of_channels.append([-1, -1, -1]) # indicate the block is finishedi
        buffered_matrix_data.append(one_entry_matrix_data_of_channels)
        if has_data: 
            matrix_ptr += 1 # for next cycle
        else:
            not_finished = 0 # no matrix data fetched, end the data access
    return buffered_matrix_data, matrix_ptr, not_finished # matrix_ptr for next time use, buffered_matrix_data for memory trace generate and get_vector_data_operation
        
def get_vector_data_operation(buffered_matrix_data, vector_row_value_dict, vector_row_addr_dict, fisrt_row_of_blocks, last_row_in, result_val, result_row_finish_in, finished_channel_in):
    vector_addr = [] # record the vector address request
    result_out = []
    current_row = last_row_in[:] # record current row in channel 0~15
    last_row = last_row_in[:]
    result_row_finish = result_row_finish_in # record whether the result of the row is finished
    finished_channel = finished_channel_in
    for i in range(len(buffered_matrix_data)): 
        #if(len(buffered_matrix_data)!=32):
        #    print("!!!!!!!")
        for j in range(0,channel_num):
            temp_row = buffered_matrix_data[i][j][0]
            vec_row = buffered_matrix_data[i][j][1]
            #if(temp_row == 1003):
            #    print("!!!!")
            if(temp_row != -1): # if the row exists
                current_row[j] = temp_row # record the current row in the blocks
                vec_value_temp = vector_row_value_dict[vec_row] # get the corresponding data
                vec_addr_temp = vector_row_addr_dict[vec_row] # get the corresponding addr
                if vec_addr_temp not in vector_addr:
                    vector_addr.append(vec_addr_temp)
                result_val[temp_row] += vec_value_temp*1 # because the non-zero matrix value is "1"
                if( (current_row[j]!=last_row[j])and(last_row[j]!=-1) ): # if current_row != last_row and last_row exist
                    result_row_finish[last_row[j]] = 1 # since the last row is not the same as the current row
                    #print("result_val=",result_val[last_row[j]])
                    result_out.append(result_addr_generate(result_val[last_row[j]], j, last_row[j], fisrt_row_of_blocks[j]))
            else: # if the row doesn't exist
                if(result_row_finish[last_row[j]]==0):
                    result_row_finish[last_row[j]] = 1
                    result_out.append(result_addr_generate(result_val[last_row[j]], j, last_row[j], fisrt_row_of_blocks[j]))
        last_row = current_row[:] #shallow copy
        #print("last_row=",last_row)
    return result_out, last_row, result_val, result_row_finish, finished_channel



def main():
    file_name = "email-Eu-core.txt"
    m_data, v_r_value_dict, v_r_addr_dict, fisrt_row_of_blocks = readin(file_name)
    total_row_num = len(v_r_value_dict)
    results_vec = []
    not_read_over = 1
    ptr_in_channel = 0
    last_row_global = [-1 for i in range(channel_num)] # record last row in channel 0~15
    result_val_channels_global = [0 for i in range(total_row_num)] # record result vector
    result_row_finish = [0 for i in range(total_row_num)] # record whether the result of the row is finished
    finished_channel = [0 for i in range(total_row_num)] # avoid repetition subtraction
    while (not_read_over):
        buffered_matrix_data, ptr_in_channel, not_read_over = get_matrix_data_operation(m_data, ptr_in_channel)
        result_t, last_row_global, result_val_channels_global, result_row_finish, finished_channel = get_vector_data_operation(buffered_matrix_data, v_r_value_dict, v_r_addr_dict, fisrt_row_of_blocks, last_row_global, result_val_channels_global, result_row_finish, finished_channel)
        results_vec+=result_t
    results_vec = sorted(results_vec)
    output_generated_results(file_name, results_vec)


if __name__ == '__main__':
    main()

