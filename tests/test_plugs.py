from __future__ import print_function

import unittest

from flowpipe.node import INode
from flowpipe.plug import InputPlug, OutputPlug


class TestNode(INode):

    def compute(self):
        pass


class TestPlugs(unittest.TestCase):
    """Test the Plugs."""

    def test_connect_and_dicsonnect_nodes(self):
        """Connect and disconnect nodes."""
        n1 = TestNode()
        n2 = TestNode()
        out_plug_a = OutputPlug('out', n1)
        out_plug_b = OutputPlug('out', n1)
        in_plug_a = InputPlug('in', n2)
        in_plug_b = InputPlug('in', n2)

        # Connect the out to the in
        out_plug_a >> in_plug_a
        self.assertEqual(1, len(out_plug_a.connections))
        self.assertEqual(1, len(in_plug_a.connections))

        # Connect the same nodes multiple times
        out_plug_a >> in_plug_a
        self.assertEqual(1, len(out_plug_a.connections))
        self.assertEqual(1, len(in_plug_a.connections))

        # Connect the in to the out
        in_plug_b >> out_plug_a
        self.assertEqual(2, len(out_plug_a.connections))
        self.assertEqual(1, len(in_plug_b.connections))

        # Connect the in to the multiple times
        in_plug_b >> out_plug_a
        self.assertEqual(2, len(out_plug_a.connections))
        self.assertEqual(1, len(in_plug_b.connections))

        # Connecting a different input disconnects the existing one
        self.assertEqual(out_plug_a, in_plug_a.connections[0])
        out_plug_b >> in_plug_a
        self.assertEqual(out_plug_b, in_plug_a.connections[0])

    def test_change_connections_sets_plug_dirty(self):
        """Connecting and disconnecting sets the plug dirty."""
        n1 = TestNode()
        n2 = TestNode()
        out_plug = OutputPlug('in', n1)
        in_plug = InputPlug('in', n2)

        in_plug.is_dirty = False
        out_plug >> in_plug
        self.assertTrue(in_plug.is_dirty)

        in_plug.is_dirty = False
        out_plug << in_plug
        self.assertTrue(in_plug.is_dirty)

    def test_set_value_sets_plug_dirty(self):
        """Connecting and disconnecting sets the plug dirty."""
        n = TestNode()
        in_plug = InputPlug('in', n)

        in_plug.is_dirty = False
        self.assertFalse(in_plug.is_dirty)
        in_plug.value = 'NewValue'
        self.assertTrue(in_plug.is_dirty)

    def test_set_output_pushes_value_to_connected_input(self):
        """OutPlugs push their values to their connected input plugs."""
        n1 = TestNode()
        n2 = TestNode()
        out_plug = OutputPlug('in', n1)
        in_plug = InputPlug('in', n2)

        out_plug.value = 'OldValue'
        self.assertNotEqual(in_plug.value, out_plug.value)

        out_plug >> in_plug
        in_plug.is_dirty = False
        self.assertEqual(in_plug.value, out_plug.value)
        self.assertFalse(in_plug.is_dirty)

        out_plug.value = 'NewValue'
        self.assertTrue(in_plug.is_dirty)
        self.assertEqual(in_plug.value, out_plug.value)

    def test_assign_initial_value_to_input_plug(self):
        """Assign an initial value to an InputPlug."""
        n = TestNode()
        in_plug = InputPlug('in', n)
        self.assertIsNone(in_plug.value)

        in_plug = InputPlug('in', n, 123)
        self.assertEqual(123, in_plug.value)

    def test_serialize(self):
        """Serialize the Plug to json."""
        n1 = TestNode()
        n2 = TestNode()
        out_plug = OutputPlug('out', n1)
        in_plug = InputPlug('in', n2)
        out_plug >> in_plug

        in_serialized = in_plug.serialize()
        out_serialized = out_plug.serialize()

        self.assertEqual(in_plug.name, in_serialized['name'])
        self.assertEqual(in_plug.value, in_serialized['value'])
        self.assertEqual('out', in_serialized['connections'][out_plug.node.identifier])

        self.assertEqual(out_plug.name, out_serialized['name'])
        self.assertEqual(out_plug.value, out_serialized['value'])
        self.assertEqual('in', out_serialized['connections'][in_plug.node.identifier])


if __name__ == '__main__':
    unittest.main()
