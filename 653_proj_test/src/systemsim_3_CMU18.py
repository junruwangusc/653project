# This program is for calculate the stream trace length of the CMU method
# And output the equivalent trace
# 11.23.2020

import operator
import os
import time
import math


# Memory parameters
channel_num = 16 #define the channel num according to HBM
# every channel is 512MB 
# 512M = 536870912
# 512M * 30/32 = 503316480
# 512M * 31/32 = 520093696
blocksize = 536870912
vector_offset = blocksize * 30 // 32
result_offset = blocksize * 31 // 32
memory_random_delay = 5
#---------------------------------------------------------
# Cache parameters
dosa = 32 # DoSA >= 32 is needed for fast replacement of up to 32 entrys
cache_depth = 1 << 17 # set field is 17 bits, cache depth = 2^17
cache_width = 64 # vector element value + vector element row num
#---------------------------------------------------------
# inputbuffer (issue queue) parameters
cache_volumn = cache_depth*dosa

class Memorytrace:
    trace_list = [] # address W/R
    outputfile = ""
    def __init__(self, inputfilename):
        file_name_without_extension=inputfilename.split(".")[0] # eg. email-Eu-core
        self.outputfile = "../trace_results/"+file_name_without_extension+"/"+file_name_without_extension+"_CMU18.trace"
        file_handle=open(self.outputfile,mode='w')
        file_handle.write("")
        file_handle.close() #initialize the file
        self.trace_list = [ [] for i in range(channel_num)]
    
    def findchannel(self, one_trace):
        ans = one_trace[0] // blocksize
        return ans

    def appendtrace(self, tracelist_in):
        for one_trace in tracelist_in:
            channel_index = self.findchannel(one_trace)
            if(channel_index!=0):
                print("error")
            self.trace_list[channel_index].append(one_trace)
        return 0
    def dec_to_hex(self, decnum):
        hex_str = "0x"+("00000000" + hex(decnum)[2:])[-8:]
        return hex_str

    def print_traces_to_file(self):
        file_handle=open(self.outputfile,mode='w')
        for i in range(channel_num):
            for one_trace in self.trace_list[i]:
                dec_to_hex_t = self.dec_to_hex(one_trace[0]) # 0x12345680 
                print(dec_to_hex_t, one_trace[1], file=file_handle)
        file_handle.close()
        return 0


def readin(file_name):
    matrix_channel_data = []
    vector_channel_data = []
    file_name_without_extension=file_name.split(".")[0]
    num_of_vec_row = 0
    print("read matrix&vector file begin")
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
        matrix_channel_data.append(temp_matrix_block)

        lines=vector_file.read().splitlines()    
        num_of_vec_row += len(lines)
        temp_vector_block = []
        for line in lines:
            lineData=line.split(' ')    # split by " ", r_c_addr
            nums=[int(num) for num in lineData]
            #vector_total_Data.append(lineData)  # r_v_addr
            temp_vector_block.append(nums)
        vector_channel_data.append(temp_vector_block)

    matrix_file.close()
    vector_file.close()
    return matrix_channel_data, vector_channel_data, num_of_vec_row

def readin_result(file_name):
    result_channel_data = [ [] for i in range(channel_num)] # r_v_addr_channel
    file_name_without_extension=file_name.split(".")[0]
    result_file = open("../proceeded_data_sets/"+file_name_without_extension+"/"+file_name_without_extension+"_result.txt", mode='r')
    print("read result file begin")
    lines=result_file.read().splitlines()
    for line in lines:
        lineData=line.split(' ')    # split by " ", 
        nums=[int(num) for num in lineData] # row, value, addr, channel
        result_channel_data[nums[3]].append(nums) # row : address  
    # read files finished
    result_file.close()
    return result_channel_data  

def from_vec_row_gen_read_trace(row_value_addr_list): # from the vec row number generate the trace format
    trace_list = []
    for row_addr in row_value_addr_list:
        addr_t = row_addr[2]
        trace_list.append((addr_t, "R"))
    return trace_list

def from_matrix_row_gen_read_trace(row_col_addr_list): # from the vec row number generate the trace format
    trace_list = []
    for row_addr in row_col_addr_list:
        addr_t = row_addr[2]
        trace_list.append((addr_t, "R"))    
    return trace_list

def from_res_row_gen_write_trace(row_val_addr_chnl_list): # from the vec row number generate the trace format
    trace_list = []
    for row_addr in row_val_addr_chnl_list:
        addr_t = row_addr[2]
        trace_list.append((addr_t, "W"))
    return trace_list

def main():
    file_name = "roadNet-CA.txt"
    memorytrace_u0 = Memorytrace(file_name)
    matrix_channel_data, vector_channel_data, num_of_vec_row = readin(file_name)
    result_channel_data = readin_result(file_name)
    middle_result_num = math.ceil(num_of_vec_row / cache_volumn)
    print("middle_result_num=",middle_result_num)
    for i in range(0, channel_num):
        matrix_row_read_trace = from_matrix_row_gen_read_trace(matrix_channel_data[0])
        memorytrace_u0.appendtrace(matrix_row_read_trace)   # add the matrix read traces
    for i in range(0, channel_num):
        vec_row_read_trace = from_vec_row_gen_read_trace(vector_channel_data[0])
        memorytrace_u0.appendtrace(vec_row_read_trace)
    for i in range(middle_result_num*2 +1):
        for i in range(0, channel_num):
            res_row_write_trace = from_res_row_gen_write_trace(result_channel_data[0])
            memorytrace_u0.appendtrace(res_row_write_trace)
    memorytrace_u0.print_traces_to_file()
    print("Finished")

if __name__ == '__main__':
    main()
    