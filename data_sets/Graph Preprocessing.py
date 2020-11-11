
def Graph_mark_with_weight():
    with open('Graph.txt') as f1:
        EdgeNames = f1.readlines()
        for i in range(0, len(EdgeNames)):
            EdgeNames[i] = EdgeNames[i].strip() + ' 1' + '\n'
    with open('Graph.txt', 'w') as f2:
        f2.writelines(EdgeNames)
def Vertex_Writting():
    Graph_size = 36692
    with open('vertex.txt', 'w') as f3:
        for j in range(0, Graph_size):
            Vertex = str(j) + ' 1'  + ' 1'+ '\n'
            f3.writelines(Vertex)
def Graph_Partition():
    Partition_size = 3
    with open('vertex.txt') as f4:
        vertex_info = f4.readlines()
        for i in range (0, Partition_size):
            interval_begin = int (i * (len(vertex_info)/Partition_size))
            interval_end = int((i + 1) * (len(vertex_info)/Partition_size))
            Partition_number = 'Partition '+ str(i) + '.txt'
            # print(Partition_number)
            with open (Partition_number, 'a') as f5:
                for j in range (interval_begin, interval_end):
                    Vertex_information = vertex_info[j]
                    f5.writelines(Vertex_information)
def Edge_Reordering():
    with open('Graph.txt') as f6:
        with open('vertex.txt') as f7:
            vertex_info = f7.readlines()
            EdgeNames = f6.readlines()
            for i in range (0, len(vertex_info)):
                Single_Vertex_list = vertex_info[i].split(" ", 2)
                # print(Single_Vertex_list[0])
                Single_Vertex_address = int(Single_Vertex_list[0])
                # print(Single_Vertex_address)
                for j in range (0, len(EdgeNames)):
                    Single_Edge_list = EdgeNames[j].split(" ", 2)
                    Single_Edge_destination = int(Single_Edge_list[1])
                    if (Single_Edge_destination == Single_Vertex_address):
                        with open('reorder_Graph.txt', 'a') as f8:
                            Edge_Write_Back = Single_Edge_list[0] + ' ' + Single_Edge_list[1] + ' ' + Single_Edge_list[2]
                            f8.writelines(Edge_Write_Back)
def Graph_reorder():
    with open('reorder_graph.txt') as f9:
        with open('vertex.txt') as f10: 
            with open('twice_order_graph.txt', 'w') as f11:
                EdgeNames = f9.readlines()
                Edge_source_list = []
                Edge_destination_list = []
                for i in range (0, len(EdgeNames)):
                    Edge_info = EdgeNames[i].split(" ", 2)
                    # print(Edge_info[0])
                    Edge_source_list.append(int(Edge_info[0]))

                    Edge_destination_list.append(int(Edge_info[1]))
                for j in range(1, len(EdgeNames)):
                    if (Edge_destination_list[j-1] == Edge_destination_list[j]):
                        if (Edge_source_list[j-1] > Edge_source_list[j]):
                            temp = Edge_source_list[j-1]
                            Edge_source_list[j-1] = Edge_source_list[j]
                            Edge_source_list[j] = temp
                # print(Edge_source_list)
                # print(Edge_destination_list)                
                for k in range(0, len(EdgeNames)):
                    Edge_info = EdgeNames[k].split(" ", 2)
                    Edge_Write_Back = str(Edge_source_list[k]) + ' ' + str(Edge_destination_list[k]) + ' ' + '1' + '\n'
                    f11.writelines(Edge_Write_Back)
                # print(Edge_destination_list)
                # print(len(EdgeNames))


def main():
    Graph_mark_with_weight()
    Vertex_Writting()
    Graph_Partition()
    Edge_Reordering()
    # Graph_reorder()
if __name__ == '__main__':
    main()
    
