# This program is for system simulation as well as generate the memory trace

# Memory parameters
channel_num = 16 #define the channel num according to HBM
# every channel is 512MB 
# 512M = 536870912
# 512M * 30/32 = 503316480
# 512M * 31/32 = 520093696
blocksize = 536870912
vector_offset = blocksize * 30 // 32
result_offset = blocksize * 31 // 32
#---------------------------------------------------------
# Cache parameters
dosa = 32 # DoSA >= 32 is needed for fast replacement of up to 32 entrys
cache_depth = 1 << 17 # set field is 17 bits, cache depth = 2^17
cache_width = 64 # vector element value + vector element row num

class Cache_entry: # for one entry
    entry_sets_valuestorage = []
    entry_sets_rowindex = []
    entry_valid = []
    entry_visit_time = []
    
    def __init__(self, dosa, cache_width): # create a cache line
        self.entry_sets_storage = [0 for i in range(dosa)]
        self.entry_valid = [0 for i in range(dosa)]
        self.entry_sets_rowindex = [0 for i in range(dosa)]
        self.entry_visit_time = [-1 for i in range(dosa)]
        return 0
        
    def check(self, vec_row):
        if (vec_row  in self.entry_sets_rowindex):
            vec_index = self.entry_sets_rowindex.index(vec_row) 
            if (entry_valid[vec_index]):
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
    cache_memory = [] # to store entries
    cache_scheduled_events = [] # for requests and delayed operation, format [[row_index, value, read/write, time step that should finish]..]
    source_vector_row_num = 0
    block_size = 0
    read_delay = 1 # 1 cycles
    write_delay = 2 # 2 cycles
    checkoutputfile = "check_cache_output.txt"
    def __init__(self, dosa, cache_depth, cache_width, total_row_num):
        for i in range(cache_depth):
            cache_entry_ut = Cache_entry(dosa, cache_width)
            self.cache_memory.append(cache_entry_ut)
            self.source_vector_row_num = total_row_num
            file_handle=open(self.checkoutputfile,mode='w')
            file_handle.write("")
            file_handle.close() #initialize the file
        if(total_row_num <= cache_depth): # if source_vector_row_num is small, use directed mapping
            self.blcok_size = 1 # directed mapping  
        else:         
            for i in range(0,32):
                if(total_row_num<=(1<<i)): # find the 2^n that just bigger than the number of rows
                    self.block_size = (1<<i) // cache_depth # set associative mapping
        return 0
    
    def find_entry(self, vec_row): # give a row number, find the right entry index
        entry_index = vec_row // self.block_size
        return entry_index

    def check(self, vec_row):
        entry_index = self.find_entry(vec_row)
        entry_obj = self.cache_memory[entry_index]
        return entry_obj.check(vec_row)
         
    def read(self, entry_index, vec_row, visit_time): # should be used after check
        vec_row_in_mem = -1
        entry_index = self.find_entry(vec_row)
        entry_obj = self.cache_memory[entry_index]
        if(entry_obj.check(vec_row)):
            value_t = entry_obj.read(vec_row, visit_time)
            print("vec row",vec_row,"=",value_t, file=self.checkoutputfile)
        else: # if not find the value
            vec_row_in_mem = vec_row
        return vec_row_in_mem # return the row that needs to be find in the memory
        

    def write(self, vec_row, vec_value, visit_time): # only when read from the memory, write is needed
        entry_index = self.find_entry(vec_row)
        entry_obj = self.cache_memory[entry_index]
        entry_obj.write(vec_row, vec_value, visit_time)
        return 0

    def events_run(time_step):
        vec_row_need_trace = []
        for event in self.cache_scheduled_events:
            if(event[3] == time_step):
                entry_index = find_entry(event[0])
                value_t = event[1]
                operation_type = event[2]
                if(operation_type == "read"):
                    vec_row_in_mem_t = self.read()
                    vec_row_need_trace.append(vec_row_in_mem_t)
                elif(operation_type == "write"):
                    self.write()
        return vec_row_need_trace

    def request_handler(self, request, time_step):
        vec_row = request[0]
        vec_value = request[1]
        operation_type = request[2]
        if(operation_type=="read"):
            self.cache_scheduled_events.append(request[0], request[1], request[2], time_step+self.read_delay) # use current timestep +delay
        elif(operation_type=="write"):
            self.cache_scheduled_events.append(request[0], request[1], request[2], time_step+self.write_delay)
        return 0

class Memorytrace:
    trace_list = []
    outputfile = ""
    def __init__(self, inputfilename):
        file_name_without_extension=inputfilename.split(".")[0] # eg. email-Eu-core
        self.outputfile = "../proceeded_data_sets/"+file_name_without_extension+"/"+file_name_without_extension+"_memorytrace.txt"
        file_handle=open(self.outputfile,mode='w')
        file_handle.write("")
        file_handle.close() #initialize the file
        return 0
    def appendtrace(self, tracelist_in):
        for one_trace in tracelist_in:
            self.trace_list.append(one_trace)
        return 0
    def print_traces_to_file(self):
        for one_trace in self.trace_list:
            print(one_trace[0], one_trace[1], file=self.out_file)
        return 0
    

class Output_buffer:
    buffer =[]
    def __init__(self, inputfilename):
        buffer =[-1 for i in range(channel_num)]
        file_name_without_extension=inputfilename.split(".")[0] # eg. email-Eu-core
        result_file_name = "../proceeded_data_sets/"+file_name_without_extension+"/"+file_name_without_extension+"_result.txt"
        in_file = open(result_file_name, mode='r')
        lines=in_file.readlines()
        for line in lines:
            lineData=line.split(' ')    # split by " "
            row_value_addr_channel = (lineData[0], lineData[1], lineData[2], lineData[3])
            buffer.append(row_value_addr_channel)
        in_file.close()
        return 0
    
    def push_to_buffer(self, row_value_addr_channel): 
    # receive the data of the result row    
    # return memory traces if possible
        w_trace = []
        addr_t = row_value_addr_channel[2]
        channel_t = row_value_addr_channel[3]
        if(self.buffer[channel_t] != -1): # the buffered values needed to be written to the memory
            for i in range(channel_num):
                addr_i = self.buffer[i] 
                if(addr_i != -1):
                    w_trace.append(addr_i) 
                    self.buffer[i] = -1
        self.buffer[channel_t] = addr_t # put the address needed to be write to the buffer
        return w_trace
        
#--------------class define end--------------#

def getmatrixdata():

def getvectordata():

def putresultdata():



def System_sim(): # class element is one per channel
    file_name = "email-Eu-core.txt"
    row_input, edge_input = readin(file_name)
    #print(memory_start_address())
    #print(data_in)    










def main():
    System_sim()


if __name__ == '__main__':
    main()
