from collections import defaultdict
import numpy as np

class Node:
    """A class to represent the nodes on our tree structure"""
    def __init__(self, name: str, branch_length: float) -> None:
        self.seq_id = name
        self.branch_length = branch_length
        self.parent_name = name + "_parent"
        self.balded_distances = {}
    
    def update_parent(self, new_parent: str, new_branch_length: float) -> None:
        # why would we use this? When we combine the parent for this node and another
        # we may want update this node to know it's the child of a shared parent idk man
        self.parent = new_parent
        self.branch_length = new_branch_length

    def __repr__(self) -> str:
        """string representation of nodes in such a way that makes Newick representation esier to generate"""
        return f"{self.seq_id[:12]}: {round(self.branch_length, 4)}"


class Tree_Graph:
    """The constructor for our graph structure"""
    def __init__(self, distance_matrix: np.matrix) -> None:
        self.nodes = []  # list of node objects
        self.edges = defaultdict(list)  # dict mapping parent node to list of children nodes
        self.edges_in = defaultdict(int)  # number of edges going in
        self.edges_out = defaultdict(int)  # number of edges going out
        self.leaves = []  # list of terminal nodes
        self.matrix_labels = []  # list of seqIDs in order they appear on the distance matrix
        self.distance_matrix = distance_matrix  # is a numpy matrix so no named rows or columns

    def add_edge(self, parent_node: Node, child_node: Node) -> None:
        # create the association between the parent and child
        self.edges[parent_node].append(child_node)
        # update who the child thinks its parent is
        child_node.parent = parent_node.seq_id
        # update the balances for all the nodes
        self.edges_out[parent_node] += 1
        self.edges_in[child_node] -= 1
    
    def get_branch_length(self, children: list[Node]) -> float | None:
        """
        get the branch length for an internal node, NOT FOR LEAVES
        
        @param leaves: list of nodes, these are the leaves that are descendents of the node
                       for which we're calculating the branch length. Don't try putting in only one leaf I swear to god
        @return: float, the branch length for whatever node is the ancestor to all the leaves in node 
        """
        # TODO: fact-check this, fix variable names, clean this all up
        # TODO: RENAME THIS FUNCTION OMG IT'S ONLY FOR INTERNAL NODES

        # select a node on the distance matrix NOT in the list of nodes (create copy of self.matrix_labels and remove all members of nodes)
        # shallow-copy the list of sequences on the distance matrix
        outgroups = self.leaves.copy()
        # remove the leaves that descend from the node for which we're calculating branch length, as we need an outgroup to calc branch length
        for leaf in children:
            outgroups.remove(leaf)
        # pick ANY outgroup, doesn't matter which
        try:
            outgroup = outgroups[0]
        except IndexError:
            # this only runs if there are no outgroups left to make
            print("Attempted to calculate branch length for an internal node that is ancestral to ALL leaves on the graph. Cannot compute branch length")
            return None

        # ok we set up this shit
        # let's say we have (((A,B),C),D); and we want branch length for ((A,B),C)
        # we want the balded distances for the outgroup, D (which is saved to the node object for D)
        # D.balded_distances[A] + D.balded_distances[C] - distance_matrix[A][C]

        # grab two of the leaves from the param list
        descendent1 = children[0]
        descendent2 = children[-1]

        # get the row and column number for each leaf in the in-group
        des1_idx = self.matrix_labels.index(descendent1.seq_id)
        des2_idx = self.matrix_labels.index(descendent2.seq_id)

        # calcullate branch length for this internal node
        return outgroup.balded_distances[descendent1.seq_id] + outgroup.balded_distances[descendent2.seq_id] - self.distance_matrix[des1_idx][des2_idx]
        
        

    def add_parent(self, children):
        # dude forgive me for what I'm about to do, I'm 16 hours into my day and sleep deprived
        parent_name = []
        for child in children:
            # append the string representation of the child node, which is formatted as a newick string
            parent_name.append(str(child))
        
        # return the newick representation for this new internal node's name
        parent_name = ",".join(parent_name)

        # get the leaves that descend from this node (does this work? Idk man, it's past midnight)
        terminal_descendents = [leaf for leaf in self.leaves if leaf.name in self.matrix_labels]

        # calculate the branch length
        branch_length = self.get_branch_length(terminal_descendents)

        # check that a branch length could be calculated
        # this looks syntactically fucked
        if branch_length is not None:

            # create the node object
            new_parent = Node(parent_name, branch_length)

            # add this node to the graph
            self.nodes.append(new_parent)

            # add the connection between this new ancestor and its children
            for child in children:
                self.add_edge(new_parent, child)

        else:

            # tell the user that this parent can't be made into a node because it doesn't have a branch length
            print("Hey bozo this parent can't be made into a node object because it's ancestral to EVERYTHING ELSE on the tree, so I can't calculate branch length")

    def get_leaves(self):
        # iterate over the nodes on the graph
        for node in self.nodes:
            # do we have more edges going in than out? 
            if self.edges_out[node] == 0:
                self.leaves.append(node)
    
    def get_newick(self):
        # identify in-group
        # for member of in-group, format as 
        pass