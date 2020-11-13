# This program is for generating the result vector as well as the corresponding address


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
cache_depth = 2 << 17 # set field is 17 bits, cache depth = 2^17
cache_width = 64 # vector element value + vector element row num



class Cache_entry:
    memory = [-1 for i in range(32)]
    valid = []
    def check

    def read

    def write

class Cache:

    cache_memory = []

    def check

    def update

    def replace

    


class Process_element: # class element is one per channel

    def getmatrixdata:

    def getvectordata:

    def putresultdata:

    def process_run:









def main():
    file_name = "email-Eu-core.txt"
    row_input, edge_input = readin(file_name)
    #print(memory_start_address())
    #print(data_in)


if __name__ == '__main__':
    main()
