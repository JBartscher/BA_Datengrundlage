import copy
import pickle
from typing import List, Dict

from data_transform.foo.link import Link
from data_transform.foo.node import Node
from persistence import get_documents_from_firestore


class WeightedNodeGraph:
    nodes: List[Node]

    def __init__(self):
        self.nodes = []

    def from_dict(self, dictionary: List[Dict]) -> 'WeightedNodeGraph':
        for d in map(WeightedNodeGraph.reduce_keys, dictionary):
            for keyword in d.get('keywords'):
                year = d.get('year')
                node = Node(keyword, year)
                node.set_links([create_link(node, Node(other_node, year)) for other_node in d.get('keywords')])
                self.nodes.append(node)

        return self

    def mash_up_duplicate_nodes(self):
        seen = set()
        unique_nodes = list()

        # tmp_nodes = copy.deepcopy(self.nodes)

        for i, n in enumerate(self.nodes):
            if n not in seen:
                seen.add(n)
                unique_nodes.append(n)
            else:
                n = self.nodes[i]
                index = WeightedNodeGraph.find_index_of_node_in_list(n, unique_nodes)
                unique_node = unique_nodes[index]
                unique_node.merge_node_into_this_node(n)
                unique_nodes[index] = unique_node
                print(i)

        self.nodes = unique_nodes

    @staticmethod
    def find_index_of_node_in_list(node, list_of_nodes: List[Node]):
        for i, v in enumerate(list_of_nodes):
            if v.get_keyword() == node.get_keyword():
                return i
        return -1

    @staticmethod
    def reduce_keys(dictionary: Dict) -> Dict:
        x = {'keywords': [], 'year': None}
        keywords = dictionary.get('keywords', "No Keywords")
        x['keywords'] = WeightedNodeGraph.purify_keywords(keywords)
        year = dictionary.get('year', -1)
        x['year'] = year
        return x

    @staticmethod
    def purify_keywords(keyword_str: str) -> List[str]:
        splitted = map(str.strip, keyword_str.split(','))
        lowered = map(str.lower, splitted)
        return list(lowered)


def get_docs() -> List[Dict]:
    all_documents = []
    try:
        all_documents = pickle.load(open("save_documents.p", "rb"))
        print("loaded from pickled obj")
    except FileNotFoundError as e:
        firestore_generator = get_documents_from_firestore("journal-citations")
        for count, document in enumerate(firestore_generator):
            all_documents.append(document.get().to_dict())
            print(count)
        print("loaded from firestore")
        pickle.dump(all_documents, open("save_documents.p", "wb"))
    except EOFError as e:
        print("eehhh")

    return all_documents


def create_link(self: Node, other: Node, value: int = 1) -> Link:
    return Link(self, other, value)


if __name__ == '__main__':
    graph = WeightedNodeGraph()

    docs = get_docs()
    graph.from_dict(docs)
    graph.mash_up_duplicate_nodes()

    print(graph.nodes)
    print("yoo")
