import yaml
from graphviz import Digraph

class GraphRenderer:
    def __init__(self, yaml_file):
        self.yaml_file = yaml_file
        self.graph = None
    
    def load_graph(self):
        with open(self.yaml_file, 'r') as file:
            data = yaml.safe_load(file)
            nodes = data.get('nodes', [])
            edges = data.get('edges', [])
            self.graph = Digraph()

            # 添加节点及其属性
            for node in nodes:
                name = node['name']
                label = node.get('label', name)
                color = node.get('color', 'black')
                shape = node.get('shape', 'circle')
                self.graph.node(name, label=label, color=color, shape=shape)

            # 添加边
            for edge in edges:
                if len(edge) == 3:
                    source, target, label = edge
                    self.graph.edge(source, target, label=label)
                else:
                    source, target = edge
                    self.graph.edge(source, target)

    def render_graph(self, output_file='graph.jpg'):
        if self.graph is None:
            raise ValueError("Graph not loaded. Please call load_graph() first.")
        
        # 渲染并保存为 JPG 图像
        self.graph.render(output_file, view=True, format='jpg')

# 使用示例
if __name__ == "__main__":
    renderer = GraphRenderer('graph.yaml')
    renderer.load_graph()
    renderer.render_graph()