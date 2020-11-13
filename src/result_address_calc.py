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

def result_start_addr_calc():
    result_start_addr = [] # all in decimal
    for i in range(channel_num):
        result_start_addr.append(int(i*blocksize+result_offset))
    return result_start_addr
   

def readin(file_name):
    matrix_block_data = []
    #vector_total_Data = []
    vector_row_value = {} # dictionary
    vector_row_addr = {} # dictionary
    file_name_without_extension=file_name.split(".")[0]
    for i in range(0,channel_num):
        matrix_file_path = "../proceeded_data_sets/" + file_name_without_extension
        vector_file_path = "../proceeded_data_sets/" + file_name_without_extension + "_vector"
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
            vector_row_value[nums[0]] = nums[1]
            vector_row_addr[nums[0]] = nums[2]
    # read files finished
    return matrix_block_data, vector_row_value, vector_row_addr


def process_element(matrix_block_data, vector_row_value, vector_row_addr):
    total_row_num = len(vector_row_value)
    matrix_ptr = 0 # matrix data index in each block

    last_row = [-1 for i in range(channel_num)] # record last row in block 0~15
    current_row = [0 for i in range(channel_num)] # record current row in block 0~15
    result_val = [0 for i in range(total_row_num)] # record result vector
    result_row_finish = [0 for i in range(total_row_num)] # record whether the result of the row is finished
    visited = [0 for i in range(total_row_num)] # avoid repetition subtraction
    
    not_finished = 1
    while not_finished:
        temp_matrix_data = [] # r_c_addr
        has_data = 0
        for i in range(0,channel_num):
            if(len(matrix_block_data[i])>matrix_ptr): # not beyond the end
                temp_matrix_data.append(matrix_block_data[i][matrix_ptr]) # gather matrix data from all blocks
                #print(matrix_block_data[i][matrix_ptr][0])
                current_row[i] = matrix_block_data[i][matrix_ptr][0] # record the current row in the blocks
                #print("current_row[",i,"]=",current_row[i])
                has_data += 1
            else:
                temp_matrix_data.append([-1, -1, -1]) # indicate the block is finishedi
                #print("the block ",i," is read to the end at ", current_row[i])
                #current_row[i] = -1 # indicate the block is finished
        if has_data: 
            matrix_ptr += 1 # for next cycle
        else:
            not_finished = 0 # no matrix data fetched, end the data access

        vector_addr = [] # record the vector address request
        vector_value = [] # record the corresponding vector element value
        for i in range(0,channel_num):
            temp_row = temp_matrix_data[i][0]
            if(temp_row != -1): # if the row exists
                vec_value_temp = vector_row_value[temp_row] # get the corresponding data
                vec_addr_temp = vector_row_addr[temp_row] # get the corresponding addr
                vector_value.append(vec_value_temp)
                if vec_addr_temp not in vector_addr:
                    vector_addr.append(vec_addr_temp)
                result_val[temp_row] += vec_value_temp*1 # because the non-zero matrix value is "1"

                if( (current_row[i]!=last_row[i])and(last_row[i]!=-1) ): # if current_row != last_row and last_row exist
                    result_row_finish[last_row[i]] = 1 # since the last row is not the same as the current row
                    print("result of row ",last_row[i]," is finished,","current_row=",current_row[i],"last_row=",last_row[i])
                    print("result_val=",result_val[last_row[i]])
            else: # if the row doesn't exist
                if(result_row_finish[last_row[i]]==0):
                    result_row_finish[last_row[i]] = 1
                #print("row doesn't exist, current_row[i]=",current_row[i], "last_row[i]=",last_row[i])
                    
        for i in range(0,channel_num): # detect the last row in each block
            if( (current_row[i]==last_row[i]) and last_row[i]!=-1):
                if(result_row_finish[last_row[i]]==1 and visited[i]==0):
                    visited[i] = 1
                    print("block ",i," is finished at row",last_row[i])
                    print("result_val=",result_val[last_row[i]])
        #if matrix_ptr<100:
        #print("random access of vector address: ", vector_addr)
        
        #for i in range(0,channel_num):
        #    last_row[i] = current_row[i] #shallow copy
        last_row = current_row[:] #shallow copy

    # 还没有写计算过程，以及输出结果的address生成

    return 0


def main():
    file_name = "email-Eu-core.txt"
    m_data, v_r_value_dict, v_r_addr_dict = readin(file_name)
    process_element(m_data, v_r_value_dict, v_r_addr_dict)

if __name__ == '__main__':
    main()

