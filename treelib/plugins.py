#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This is a public location to maintain contributed
   utilities to extend the basic Tree class.
"""
from treelib.common import TraversalMode


def export_to_dot(tree, filename, shape='circle', graph='digraph'):
    """Exports the tree in the dot format of the graphviz software"""
        
    nodes, connections = [], []
    if tree.nodes:        
        
        for node in tree.expand_tree(mode=TraversalMode.WIDTH):
            node_id = tree[node].id
            state = f'"{node_id}" [label="{tree[node].tag}", shape={shape}]'
            nodes.append(state)

            for child in tree.children(node_id):
                connections.append(f'"{node_id}" -> "{child.id}"')

    # write nodes and connections to dot format
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f'{graph} tree {{\n')

        for node in nodes:
            f.write(f'\t{node}\n')

        f.write('\n')

        for child in connections:
            f.write(f'\t{child}\n')

        f.write('}')
