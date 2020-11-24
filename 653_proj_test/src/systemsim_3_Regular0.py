import operator
import os
import time

# This program is for system simulation as well as generate the memory trace

addition_info = "_regular_0"
# This is to add some info to the trace file name
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
inputbuffer_depth = 32

class Cache_entry: # for one entry
    entry_sets_valuestorage = []
    entry_sets_rowindex = []
    entry_valid = []
    entry_visit_time = []
    def __init__(self, dosa, cache_width): # create a cache line

        self.entry_sets_valuestorage = [0 for i in range(dosa)]
        self.entry_sets_rowindex = [0 for i in range(dosa)]
        self.entry_valid = [0 for i in range(dosa)]
        self.entry_visit_time = [-1 for i in range(dosa)]
        
    def check(self, vec_row):
        if (vec_row  in self.entry_sets_rowindex):
            vec_index = self.entry_sets_rowindex.index(vec_row) 
            if (self.entry_valid[vec_index]):
                return 1 
                # if the row can be find and valid
        return 0

    def replacement(self): # LRU
        if(0 in self.entry_valid): # if there are void place
            loc = self.entry_valid.index(0) 
            return loc  # return the first void place
        else:
            earlist_t = min(self.entry_visit_time) 
            loc = self.entry_visit_time.index(earlist_t) #return the least recent used location
            return loc

            #least_degree = min(self.entry_degree)
            #loc = self.entry_degree.index(earlist_t)
            #return loc
            #完全按degrees

            #普通的【0.。。31】LRU hot的 【0。。4】degree
            #24 ： 8
            #28 ： 4
            #16 ： 16

    def read(self, vec_row, visit_time):
        if (self.check(vec_row)==1):
            r_loc = self.entry_sets_rowindex.index(vec_row) 
            value_t = self.entry_sets_valuestorage[r_loc]
            self.entry_visit_time[r_loc] = visit_time
            return value_t
        return 0
                      
    def write(self, vec_row, vec_value, visit_time): # should be used only when the value is not found in the cache
        if (self.check(vec_row)==1): # the cache has the value already
            return 0
        else: # need to be written into the cache
            w_loc = self.replacement()
            self.entry_sets_rowindex[w_loc] = vec_row
            self.entry_sets_valuestorage[w_loc] = vec_value
            self.entry_valid[w_loc] = 1
            self.entry_visit_time[w_loc] = visit_time
        return 0

    
class Cache: # for one entry
    checkoutputfile = "check_cache_output.txt"
    cache_memory = [] # to store entries
    #cache_scheduled_events = [] # for requests and delayed operation, format [[row_index, value, read/write, time step that should finish]..]
    cache_scheduled_events = {} # for requests and delayed operation, format time step that should finish : [(row_index, value, read/write)( )( )..]
    source_vector_row_num = 0
    block_size = 0
    read_delay = 1 # 1 cycles
    write_delay = 2 # 2 cycles
    def __init__(self, dosa, cache_depth, cache_width, total_row_num):
        for i in range(cache_depth):
            cache_entry_ut = Cache_entry(dosa, cache_width)
            self.cache_memory.append(cache_entry_ut)
            self.source_vector_row_num = total_row_num
            file_handle=open(self.checkoutputfile,mode='w')
            file_handle.write("")
            file_handle.close() #initialize the file
        if(total_row_num <= cache_depth): # if source_vector_row_num is small, use directed mapping
            self.block_size = 1 # directed mapping  
        else:         
            for i in range(0,32):
                upperbound = (1<<i)
                if( total_row_num <= upperbound ): # find the 2^n that just bigger than the number of rows
                    self.block_size = upperbound // cache_depth # set associative mapping
                    break
            print("upperbound=",upperbound, "self.block_size=",self.block_size)
    
    def find_entry(self, vec_row): # give a row number, find the right entry index
        entry_index = vec_row // self.block_size
        return entry_index

    def check(self, vec_row):
        entry_index = self.find_entry(vec_row)
        entry_obj = self.cache_memory[entry_index]
        return entry_obj.check(vec_row)
         
    def read(self, vec_row, vec_value, visit_time): # should be used after check
        vec_row_in_mem = -1
        entry_index = self.find_entry(vec_row)
        entry_obj = self.cache_memory[entry_index]
        #file_handle=open(self.checkoutputfile,mode='a')
        if(entry_obj.check(vec_row)):
            value_t = entry_obj.read(vec_row, visit_time)
            #print("vec row",vec_row,"=",value_t, vec_value)
        else: # if not find the value
            vec_row_in_mem = vec_row
        #file_handle.close()
        return vec_row_in_mem # return the row that needs to be find in the memory
        

    def write(self, vec_row, vec_value, visit_time): # only when read from the memory, write is needed
        entry_index = self.find_entry(vec_row)
        entry_obj = self.cache_memory[entry_index]
        entry_obj.write(vec_row, vec_value, visit_time)
        return 0

    def events_run(self, time_step):
        vec_row_need_trace = []
        if time_step in self.cache_scheduled_events:
            for event in self.cache_scheduled_events[time_step]:
                row_t = event[0]
                value_t = event[1]
                operation_type = event[2]
                visit_time_t = time_step
                if(operation_type == "read"):
                    vec_row_in_mem_t = self.read( row_t, value_t, visit_time_t)
                    if(vec_row_in_mem_t != -1): # if cache miss
                        vec_row_need_trace.append(vec_row_in_mem_t)
                elif(operation_type == "write"):
                    self.write(row_t, value_t, visit_time_t)
            del self.cache_scheduled_events[time_step] # This is to improve performance and reduce the cost of time and memory space
        return vec_row_need_trace

    def request_handler(self, request_list, time_step):
        if not (time_step+self.read_delay in self.cache_scheduled_events):
            self.cache_scheduled_events[time_step+self.read_delay] = []
        if not (time_step+self.write_delay in self.cache_scheduled_events):
            self.cache_scheduled_events[time_step+self.write_delay] = []
        for request in request_list:
            vec_row = request[0]
            vec_value = request[1]
            operation_type = request[2]
            if(operation_type=="read"):
                self.cache_scheduled_events[time_step+self.read_delay].append((vec_row, vec_value, operation_type)) # use current timestep +delay
            elif(operation_type=="write"):
                self.cache_scheduled_events[time_step+self.write_delay].append((vec_row, vec_value, operation_type))
        return 0

# class Memorytrace:
#     trace_list = [] # address W/R
#     outputfile = ""
#     def __init__(self, inputfilename):
#         file_name_without_extension=inputfilename.split(".")[0] # eg. email-Eu-core
#         self.outputfile = "../proceeded_data_sets/"+file_name_without_extension+"/"+file_name_without_extension+"_memorytrace.txt"
#         file_handle=open(self.outputfile,mode='w')
#         file_handle.write("")
#         file_handle.close() #initialize the file

#     def appendtrace(self, tracelist_in):
#         for one_trace in tracelist_in:
#             self.trace_list.append(one_trace)
#         return 0
#     def dec_to_hex(self, decnum):
#         hex_str = "0x"+("00000000" + hex(decnum)[2:])[-8:]
#         return hex_str

#     def print_traces_to_file(self):
#         file_handle=open(self.outputfile,mode='w')
#         for one_trace in self.trace_list:
#             dec_to_hex_t = self.dec_to_hex(one_trace[0]) # 0x12345680 
#             print(dec_to_hex_t, one_trace[1], file=file_handle)
#         file_handle.close()
#         return 0

class Memorytrace: # per channel
    trace_list = [] # address W/R
    outputfile = ""
    outputfile2 = ""
    average_req_len_in_channel = 0.0
    max_req_len_in_channel = 0.0    
    def __init__(self, inputfilename):
        file_name_without_extension=inputfilename.split(".")[0] # eg. email-Eu-core
        output_dir = "../trace_results/"+file_name_without_extension
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self.outputfile = output_dir+"/"+file_name_without_extension+"_"+addition_info+".trace"
        self.outputfile2 = output_dir+"/"+file_name_without_extension+addition_info+"_unbalance.txt"
        file_handle=open(self.outputfile,mode='w')
        file_handle.write("")
        file_handle.close() #initialize the file
        self.trace_list = [ [] for i in range(channel_num)]
    
    def findchannel(self, one_trace):
        ans = one_trace[0] // blocksize
        return ans

    def appendtrace(self, tracelist_in):
        trace_temp_list = [ [] for i in range(channel_num)]
        for one_trace in tracelist_in:
            channel_index = self.findchannel(one_trace)
            self.trace_list[channel_index].append(one_trace)
            trace_temp_list[channel_index].append(one_trace)
        self.average_req_len_in_channel += len(tracelist_in)
        tmax = 0
        for i in range(channel_num):
            tmax = max(tmax, len(trace_temp_list[i]))
        self.max_req_len_in_channel += tmax*16
        return 0

    def dec_to_hex(self, decnum):
        hex_str = "0x"+("00000000" + hex(decnum)[2:])[-8:]
        return hex_str

    def print_traces_to_file(self):
        file_handle=open(self.outputfile,mode='w')
        file_handle2=open(self.outputfile2,mode='w')
        for i in range(channel_num):
            for one_trace in self.trace_list[i]:
                dec_to_hex_t = self.dec_to_hex(one_trace[0]) # 0x12345680 
                print(dec_to_hex_t, one_trace[1], file=file_handle)
        print("the unbalance among channel=", self.max_req_len_in_channel/ self.average_req_len_in_channel)
        print("the unbalance among channel=", self.max_req_len_in_channel/ self.average_req_len_in_channel, file = file_handle2)
        file_handle.close()
        file_handle2.close()        
        return 0
    

class Output_buffer:
    buffer =[]
    def __init__(self, inputfilename):
        self.buffer =[-1 for i in range(channel_num)] # initially buffer is empty
        #file_name_without_extension=inputfilename.split(".")[0] # eg. email-Eu-core
        #result_file_name = "../proceeded_data_sets/"+file_name_without_extension+"/"+file_name_without_extension+"_result.txt"
        #in_file = open(result_file_name, mode='r')
        #lines=in_file.readlines()
        #for line in lines:
        #    lineData=line.split(' ')    # split by " "
        #    row_value_addr_channel = (lineData[0], lineData[1], lineData[2], lineData[3])
        #    buffer.append(row_value_addr_channel)
        #in_file.close()

    def push_to_buffer(self, row_value_addr_channel_list): 
    # receive the data of the result row    
    # return memory traces if possible
        w_trace = []
        for row_value_addr_channel in row_value_addr_channel_list:
            addr_t = row_value_addr_channel[2]
            channel_t = row_value_addr_channel[3]
            if(self.buffer[channel_t] != -1): # the buffered values needed to be written to the memory
                for i in range(channel_num):
                    addr_i = self.buffer[i] 
                    if(addr_i != -1):
                        w_trace.append((addr_i, "W")) 
                        self.buffer[i] = -1
            self.buffer[channel_t] = addr_t # put the address needed to be write to the buffer
        return w_trace
        
#--------------class define end--------------#


def readin_source(file_name):
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

def readin_result(file_name):
    result_row_to_rvac_dict = {} # dictionary
    file_name_without_extension=file_name.split(".")[0]
    result_file = open("../proceeded_data_sets/"+file_name_without_extension+"/"+file_name_without_extension+"_result.txt", mode='r')
    lines=result_file.read().splitlines()
    for line in lines:
            lineData=line.split(' ')    # split by " ", 
            nums=(int(lineData[0]), int(lineData[1]), int(lineData[2]), int(lineData[3]) ) # row, value, addr, channel
            result_row_to_rvac_dict[nums[0]] = nums # row : address  
    # read files finished
    result_file.close()
    return result_row_to_rvac_dict  


def output_generated_results(file_name, row_value_addr_channel):
    file_name_without_extension=file_name.split(".")[0]
    output_dir = "../proceeded_data_sets/"+file_name_without_extension
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file_name = output_dir+"/"+"_system_sim_result.txt"    
    out_file = open(output_file_name, mode='w')
    for data in row_value_addr_channel:
        print(data[0], data[1], data[2], data[3], file=out_file)
    out_file.close()
    return 0

def get_matrix_data_operation(matrix_block_data, matrix_ptr_in):
    matrix_ptr = matrix_ptr_in # matrix data index in each channel
    not_finished = 1
    buffered_matrix_data = [] # r_c_addr
    matrix_memory_row_addr_req = []
    for i in range(inputbuffer_depth):    
        if(not_finished==0):
            break
        #else:
        has_data = 0
        one_entry_matrix_data_of_channels = []
        for j in range(0,channel_num):
            if(len(matrix_block_data[j])>matrix_ptr): # not beyond the end
                one_entry_matrix_data_of_channels.append(matrix_block_data[j][matrix_ptr]) # gather matrix data from all blocks
                matrix_memory_row_addr_req.append((matrix_block_data[j][matrix_ptr][0], matrix_block_data[j][matrix_ptr][2]))
                has_data += 1
            else:
                one_entry_matrix_data_of_channels.append([-1, -1, -1]) # indicate the block is finishedi
        buffered_matrix_data.append(one_entry_matrix_data_of_channels)
        if has_data: 
            matrix_ptr += 1 # for next cycle
        else:
            not_finished = 0 # no matrix data fetched, end the data access
    return buffered_matrix_data, matrix_ptr, not_finished, matrix_memory_row_addr_req # matrix_ptr for next time use, buffered_matrix_data for memory trace generate and get_vector_data_operation
        
def get_vector_data_operation(buffered_matrix_data, vector_row_value_dict, res_row_to_rvac_dict, last_row, result_val, result_row_finish_in):
    vec_row_need_addr = [] # record the vector address request
    result_out = []
    current_row = last_row[:] # record current row in channel 0~15
    result_row_finish = result_row_finish_in # record whether the result of the row is finished
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
                if vec_row not in vec_row_need_addr:
                    vec_row_need_addr.append(vec_row)
                result_val[temp_row] += vec_value_temp*1 # because the non-zero matrix value is "1"
                if( (current_row[j]!=last_row[j])and(last_row[j]!=-1) ): # if current_row != last_row and last_row exist
                    result_row_finish[last_row[j]] = 1 # since the last row is not the same as the current row
                    #print("result_val=",result_val[last_row[j]])
                    #row_value_addr_channel
                    result_out.append(res_row_to_rvac_dict[last_row[j]])

            else: # if the row doesn't exist
                if(result_row_finish[last_row[j]]==0):
                    result_row_finish[last_row[j]] = 1
                    result_out.append(res_row_to_rvac_dict[last_row[j]])
        last_row = current_row[:] #shallow copy
        #print("last_row=",last_row)
    return result_out, last_row, vec_row_need_addr

def from_vec_row_gen_read_trace(row_list, vec_row_addr_dict): # from the vec row number generate the trace format
    trace_list = []
    for row in row_list:
        addr_t = vec_row_addr_dict[row]
        trace_list.append((addr_t, "R"))
    return trace_list

def from_matrix_row_gen_read_trace(row_addr_list): # from the vec row number generate the trace format
    trace_list = []
    for row_addr in row_addr_list:
        addr_t = row_addr[1]
        trace_list.append((addr_t, "R"))    
    return trace_list

def from_vec_row_gen_cache_read_req(row_list, vec_row_value_dict):
    cache_req_list = []
    for row in row_list:
        val_t = vec_row_value_dict[row]
        cache_req_list.append((row, val_t,"read"))
    return cache_req_list

def from_vec_row_gen_cache_write_req(row_list, vec_row_value_dict):
    cache_req_list = []
    for row in row_list:
        val_t = vec_row_value_dict[row]
        cache_req_list.append((row, val_t,"write"))
    return cache_req_list

def System_sim():
    file_name = "roadNet-CA.txt"
    m_data, vec_row_value_dict, vec_row_addr_dict, fisrt_row_of_blocks = readin_source(file_name)
    total_row_num = len(vec_row_addr_dict) # total exist row in matrix, which is also possible row number of the result
    res_row_to_rvac_dict = readin_result(file_name) # res_row_to_row_value_addr_channel_dict

    memorytrace_u0 = Memorytrace(file_name)
    cache_u0 = Cache(dosa, cache_depth, cache_width, total_row_num)
    output_buffer_u0 = Output_buffer(file_name)


    results_vec = []
    not_read_over = 1
    ptr_in_channel = 0
    last_row_channels = [-1 for i in range(channel_num)] # record last row in channel 0~15
    result_val_channels = [0 for i in range(total_row_num)] # record result vector
    result_row_finish = [0 for i in range(total_row_num)] # record whether the result of the row is finished
    time_step = 0
    while (not_read_over):
        if (time_step % 1000 == 0):
            print("time_step=", time_step)
        buffered_matrix_data, ptr_in_channel, not_read_over, matrix_row_addr_req = get_matrix_data_operation(m_data, ptr_in_channel)
        matrix_row_read_trace = from_matrix_row_gen_read_trace(matrix_row_addr_req)
        memorytrace_u0.appendtrace(matrix_row_read_trace)   # add the matrix read traces
        
        result_t, last_row_channels, vec_row_readin = get_vector_data_operation(buffered_matrix_data, vec_row_value_dict, res_row_to_rvac_dict, last_row_channels, result_val_channels, result_row_finish)
        results_vec+=result_t        
        vec_row_cache_read_req = from_vec_row_gen_cache_read_req(vec_row_readin, vec_row_value_dict)
        cache_u0.request_handler(vec_row_cache_read_req, time_step)
        vec_row_req_mem = cache_u0.events_run(time_step)
        r_trace_t = from_vec_row_gen_read_trace(vec_row_req_mem, vec_row_addr_dict)
        memorytrace_u0.appendtrace(r_trace_t)
        
        vec_row_cache_write_req = from_vec_row_gen_cache_write_req(vec_row_req_mem, vec_row_value_dict)
        cache_u0.request_handler(vec_row_cache_write_req, time_step+memory_random_delay) # 5 is the memory access delay estimate
        w_trace_t = output_buffer_u0.push_to_buffer(result_t)
        memorytrace_u0.appendtrace(w_trace_t)
        
        time_step += 1

    for i in range(50):
        vec_row_req_mem = cache_u0.events_run(time_step)
        r_trace_t = from_vec_row_gen_read_trace(vec_row_req_mem, vec_row_addr_dict)
        memorytrace_u0.appendtrace(r_trace_t)

        vec_row_cache_write_req = from_vec_row_gen_cache_write_req(vec_row_req_mem, vec_row_value_dict)
        cache_u0.request_handler(vec_row_cache_write_req, time_step+memory_random_delay) # 5 is the memory access delay estimate
        time_step += 1

    results_vec = sorted(results_vec)
    output_generated_results(file_name, results_vec)
    memorytrace_u0.print_traces_to_file()


def main():
    start_t = time.time()
    print("Processing Start")
    System_sim()
    end_t = time.time()
    time_s = int(end_t - start_t)
    print("Processing end, time consume=", time_s, "s")
    input("Press <enter>")
    


if __name__ == '__main__':
    main()
