"""A Graph of Nodes."""
from __future__ import print_function
from __future__ import absolute_import

from ascii_canvas.canvas import Canvas
from ascii_canvas.item import Item
from ascii_canvas.item import Line

from .node import INode
__all__ = ['Graph']


class Graph(INode):
    """A graph of Nodes."""

    def __init__(self, name=None, nodes=None):
        """Initialize the list of Nodes."""
        super(Graph, self).__init__(name=name)
        self.nodes = nodes or []

    def __unicode__(self):
        """Display the Graph."""
        canvas = Canvas()
        x = 0
        for i, row in enumerate(self.evaluation_matrix):
            y = 0
            x_diff = 0
            for j, node in enumerate(row):
                item = Item(str(node), [x, y])
                node.item = item
                x_diff = item.bbox[2] - item.bbox[0] + 4 if item.bbox[2] - item.bbox[0] + 4 > x_diff else x_diff
                y += item.bbox[3] - item.bbox[1]
                canvas.add_item(item)
            x += x_diff

        for node in self.nodes:
            for j, plug in enumerate(node.outputs):
                for connection in node.outputs[plug].connections:
                    dnode = connection.node
                    start = [node.item.position[0] + node.item.bbox[2],
                             node.item.position[1] + 3 + len(node.inputs) + j]
                    end = [dnode.item.position[0],
                           dnode.item.position[1] + 3 + dnode.inputs.values().index(connection)]
                    canvas.add_item(Line(start, end), 0)
        return canvas.render()

    @property
    def is_dirty(self):
        """Test whether any of the given nodes needs evaluation."""
        return True in [n.is_dirty for n in self.nodes]

    @property
    def dirty_nodes(self):
        """Test whether any of the given nodes needs evaluation."""
        return [n for n in self.nodes if n.is_dirty]

    @property
    def all_nodes(self):
        """Return all nodes, also from subgraphs."""
        all_nodes = list()
        for node in self.nodes:
            if isinstance(node, Graph):
                all_nodes.append(node)
            elif isinstance(node, INode):
                all_nodes.append(node)
        return all_nodes

    @property
    def evaluation_matrix(self):
        """Sort nodes into a 2D grid based on their dependency.

        Rows affect each other and have to be evaluated in sequence.
        The Nodes on each row however can be evaluated in parallel as
        they are independent of each other.
        The amount of Nodes in each row can vary.

        Returns:
            (list of list of INode): Each sub list represents a row.
        """
        levels = dict()

        for node in self.all_nodes:
            self._sort_node(node, levels, level=0)

        grid = list()
        for level in sorted(list(set(levels.values()))):
            row = list()
            for node in [n for n in levels if levels[n] == level]:
                row.append(node)
            grid.append(row)

        return grid

    @property
    def evaluation_sequence(self):
        """Sort Nodes into a sequential, flat execution order.

        Returns:
            (list of INode): A one dimensional representation of the
                evaluation grid.
        """
        return [node for row in self.evaluation_matrix for node in row]

    def compute(self, **args):
        """Evaluate all sub nodes."""
        for node in self.evaluation_sequence:
            node.evaluate()

    def serialize(self):
        """Serialize the graph in it's grid form."""
        data = super(Graph, self).serialize()
        data['nodes'] = [node.serialize() for node in self.nodes]
        return data

    @staticmethod
    def deserialize(data):
        """De-serialize from the given json data."""
        graph = INode.deserialize(data)
        graph.nodes = []
        for node in data['nodes']:
            graph.nodes.append(INode.deserialize(node))
        for node in data['nodes']:
            this = [n for n in graph.nodes if n.identifier == node['identifier']][0]
            for name, input_ in node['inputs'].items():
                for identifier, plug in input_['connections'].items():
                    upstream = [n for n in graph.nodes if n.identifier == identifier][0]
                    upstream.outputs[plug] >> this.inputs[name]
        return graph

    def _sort_node(self, node, parent, level):
        """Sort the node into the correct level."""
        if node in parent.keys():
            if level > parent[node]:
                parent[node] = level
        else:
            parent[node] = level

        for downstream_node in node.downstream_nodes:
            self._sort_node(downstream_node, parent, level=level + 1)