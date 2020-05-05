import graphviz as gv
import copy


def add_edges(graph, edges):
    """Add edge(s) to graph

    Args:
        graph (Graph): Graph to add edge(s) to
        edges (list): List of edges

    Returns:
        Graph: Return the modified graph

    """
    for e in edges:
        if isinstance(e[0], tuple):
            graph.edge(*e[0], **e[1])
        else:
            graph.edge(*e)
    return graph



class Drawer():
    def __init__(self, class_list):
        self.subgraph = gv.Digraph(name='test')
        self.class_list = class_list
        self.edge_list = []

    def run(self, outputlocation):
        self.add_nodes_to_graph()
        self.add_edges_to_graph()

        #self.print_graph_source()
        self.get_graph_view(outputlocation)

    def add_nodes_to_graph(self):
        for n in self.class_list:
            self.subgraph.node('%s %s'%(n['from_class'], n['from_method']),'class_name:%s, method_name:%s, (%s,%s)'%(n['from_class'], n['from_method'], n['from_line'], n['dst_line']))

    def add_edges_to_graph(self):
        for n in self.class_list:
            temp = [item for item in self.class_list if item != n]
            current_edge = {}
            for item in temp:
                match = self.check_relationships(n,item)
                if match:
                    current_edge['from_class'] = n['from_class']
                    current_edge['from_method'] = n['from_method']
                    current_edge['to_class'] = item['from_class']
                    current_edge['to_method'] = item['from_method']

                    from_name = current_edge['from_class'] + ' ' + current_edge['from_method']
                    to_name = current_edge['to_class'] + ' ' + current_edge['to_method']

                    check = self.check_duplicate_edge(current_edge,self.edge_list)
                    if not check:
                        self.subgraph.edge(from_name, to_name)
                        self.edge_list.append(copy.deepcopy(current_edge))

    def check_relationships(self, a, b):
        if a['from_class']==b['dst_class'] and a['from_method']==b['dst_method']:
            return True
        return False

    def check_duplicate_edge(self, current, edge_list):
        if edge_list == []:
            return False
        for item in edge_list:
            if current['from_class'] == item['from_class'] and current['from_method'] == item['from_method'] and current['to_class'] == item['to_class'] and current['to_method'] == item['to_method']:
                return True
        return False

    def print_graph_source(self):
        print(self.subgraph.source)

    def get_graph_view(self,output_location):
        self.subgraph.render('%s/test-table.gv'%output_location, view=True)

