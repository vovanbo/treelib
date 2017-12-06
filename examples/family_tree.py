#!/usr/bin/env python
# Example usage of ttree
#
# Author: chenxm
#
__author__ = 'chenxm'

from ttree import Tree


def create_family_tree():
    # Create the family tree
    tree = Tree()
    tree.create_node("Harry", "harry")  # root node
    tree.create_node("Jane", "jane", parent="harry")
    tree.create_node("Bill", "bill", parent="harry")
    tree.create_node("Diane", "diane", parent="jane")
    tree.create_node("Mary", "mary", parent="diane")
    tree.create_node("Mark", "mark", parent="jane")
    return tree


def example(text):
    print(f'\n{" " + text + " ":-^80}\n')


if __name__ == '__main__':
    tree = create_family_tree()

    example("Tree of the whole family")
    tree.print(key=lambda x: x.tag, reverse=True, ascii_mode='em')

    example("All family members in DEPTH mode")
    print(', '.join([tree[node].tag for node in tree.expand_tree()]))

    example("All family members (with identifiers) but Diane's sub-family")
    tree.print(id_hidden=False, filtering=lambda x: x.id != 'diane')

    example("Let me introduce Diane family only")
    tree.subtree('diane').print()

    example("Children of Diane")
    for child in tree.is_branch('diane'):
        print(tree[child].tag)

    example("New members join Bill's family")
    new_tree = Tree()
    new_tree.create_node("n1", 1)  # root node
    new_tree.create_node("n2", 2, parent=1)
    new_tree.create_node("n3", 3, parent=1)
    tree.paste('bill', new_tree)
    tree.print()

    example("They leave after a while")
    tree.remove_node(1)
    tree.print()

    example("Now Mary moves to live with grandfather Harry")
    tree.move_node('mary', 'harry')
    tree.print()

    example("A big family for Mark to send message to the oldest Harry")
    print(', '.join([tree[node].tag for node in tree.rsearch('mark')]))
