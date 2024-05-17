import xml.etree.ElementTree as ET

from src.austral.gps.lib.trackmap.graph.node import Node


class XmlNodeMapReader:
    @staticmethod
    def read(file_path):
        critical_node_ids = ['443', '84', '87', '81', '165', '166', '167', '168', '169', '170', '171', '172', '173', '174', '175', '176', '177', '8', '12', '1', '150']
        nodes = {}
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()

        # Namespace dictionary for XPath queries
        ns = {'graphml': 'http://graphml.graphdrawing.org/xmlns'}

        # Find all nodes in the graph
        for node in root.findall('.//graphml:node', ns):
            node_id = node.attrib['id']

            # Find x and y coordinates of the node
            x = None
            y = None
            critical = None
            for data in node.findall('.//graphml:data', ns):
                if data.attrib['key'] == 'd0':
                    x = float(data.text)
                elif data.attrib['key'] == 'd1':
                    y = float(data.text)
                elif data.attrib['key'] == 'd3':
                    critical = data.text

            if x is not None and y is not None:
                nodes[node_id] = Node(node_id, x, y)
                if critical is not None:
                    nodes[node_id].is_critical = True

        # Find all edges in the graph and add successors to nodes
        for edge in root.findall('.//graphml:edge', ns):
            source_id = edge.attrib['source']
            target_id = edge.attrib['target']

            # Add target node as successor to source node
            if source_id in nodes and target_id in nodes:
                source_node = nodes[source_id]
                target_node = nodes[target_id]
                source_node.add_neighbor(target_node)

        return nodes

if __name__ == '__main__':
    nodes = XmlNodeMapReader.read("../xml_node_map.xml")
    for id, node in nodes.items():
        print(f'Node {id} - X: {node.x}, Y: {node.y}')

