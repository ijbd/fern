'''
what is true of ferns?

a fern is made of leaves, branches, and smaller ferns.
all ferns are related in space.
relations describe perceived position, orientation, and scale.
'''
from __future__ import annotations
from collections import namedtuple

Leaf = namedtuple(
    typename="Leaf",
    field_names=["x", "y"]
)

Branch = namedtuple(
    typename="Branch",
    field_names=["x", "y"]
)

Relation = namedtuple(
    typename="Relation",
    field_names=[
        "x",
        "y",
        "xs",
        "ys",
        "theta"
    ]
)

def relate_leaf(leaf, relation):
    pass

def relate_leaf(branch, relation):
    pass


class Fern:
    def __init__(self):
        self.ferns = []
        self.relations = []

    def plant(self, fern: Fern, relation: Relation):
        """plant a new fern"""
        self.ferns.append(fern)
        self.relations.append(relation)        

    def resolve(self) -> list[Leaf | Branch]:
        """return a list of perceived leaves and branches"""
        perspective = []
        for fern, relation in zip(self.ferns, self.relations):
            # base case
            if isinstance(fern, [Leaf, Branch]):
                perspective += self.apply(relation, fern)
            # recurse
            perspective += fern.resolve()
        
        return perspective