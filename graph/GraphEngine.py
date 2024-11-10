import yaml
from nodes.InputNode import InputNode
from nodes.LlmNode import LlmNode
from nodes.VlmNode import VlmNode

class GraphEngine:
    def __init__(self, yaml_path):
        self.nodes = {}
        self.input_node = None
        
        with open(yaml_path, 'r') as f:
            self.graph = yaml.load(f, Loader=yaml.FullLoader)
            for node in self.graph['nodes']:
                type = node['type']
                if type == 'LlmNode':
                    self.nodes[node['name']] = LlmNode(**node)
                elif type == 'VlmNode':
                    self.nodes[node['name']] = VlmNode(**node)
                elif type == 'InputNode':
                    self.input_node = InputNode(**node)
                    self.nodes[node['name']] = self.input_node
                else:
                    raise ValueError(f'Unknown node type: {type}')

            if self.input_node is None:
                raise ValueError('No input node found in the graph')

            for edge in self.graph['edges']:
                source = edge[0]
                target = edge[1]
                source_node = self.nodes[source]
                target_node = self.nodes[target]
                source_node.register_output_callback(target_node.set_input)
    def set_input(self, **kwargs):
        self.input_node.set_input(**kwargs)

    def run(self):
        for node in self.nodes.values():
            node.run()

    def stop(self):
        for node in self.nodes.values():
            node.stop()

if __name__ == '__main__':

    yaml_path = 'pipeline/3_argu.yaml'

    graph = GraphEngine(yaml_path)

    graph.run()

    init_input = {"user_prompt":'给我讲一个笑话'}
    graph.set_input(**init_input)
