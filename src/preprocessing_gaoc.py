import sys

# read a edge array file and sort it
def sort_graph(input_file, edge_file):
    edges = []
    i = 0
    with open(input_file) as f:
        for line in f:
            i += 1
            l = line.split('\t')
            if len(l) < 2:
              print(i)
            edges += [(int(l[0]), int(l[1]))]
    edges.sort()
    with open(edge_file, 'wt') as f:
        f.write(str(len(edges)) + '\n')
        for e in edges:
            f.write(str(e[0]) + ' ' + str(e[1]) + '\n')
    return edges

###
    #output format:
    #start_edge number_of_outgoing_edge
    #start_edge number_of_outgoing_edge
    #...
    #Nodes that doesn't have any outgoing edge will have a line:
    #-1 0
###
def generate_node_array(sorted_edge, filename):
    max_node = max(max([e[1] for e in sorted_edge]), sorted_edge[-1][0])
    node_array = []
    ptr = 0
    # max_node is also total number of node minus one
    for i in range(max_node+1):
        if ptr >= len(sorted_edge):
            node_array += [(-1, 0)]
            continue
        # when nodes are skipped, i.e. not a source of an edge
        if ptr < len(sorted_edge) and sorted_edge[ptr][0] > i:
            node_array += [(-1, 0)]
            continue
        start = ptr
        count = 0
        # count total number of outgoing edges of a node
        while ptr < len(sorted_edge) and sorted_edge[ptr][0] == i:
            count += 1
            ptr += 1
        node_array += [(start, count)]

    with open(filename, 'wt') as f:
        f.write(str(len(node_array)) + '\n')
        for node in node_array:
            f.write(str(node[0]) + " " + str(node[1]) + '\n')


if (len(sys.argv) != 4):
    print("need three argument")
else:
    sorted_edge = sort_graph(str(sys.argv[1]), str(sys.argv[2]))
    generate_node_array(sorted_edge, str(sys.argv[3]))


