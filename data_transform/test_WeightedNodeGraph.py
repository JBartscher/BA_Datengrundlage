from unittest import TestCase

from data_transform.WeightedNodeGraph import WeightedNodeGraph


def generate_test_docs():
    docs = [
        {
            'ID': '10.1145/3041957', 'url': 'https://doi.org/10.1145/3041957', 'year': '2017',
            'keywords': 'machine learning, Variability modeling, process model'
        },
        {
            'ID': '10.1145/3041957', 'url': 'https://doi.org/10.1145/3041957', 'year': '2018',
            'keywords': 'customizable process model, Variability modeling, process model'
        },
        {
            'ID': '10.1145/3041957', 'url': 'https://doi.org/10.1145/3041957', 'year': '2017',
            'keywords': 'machine learning, Variability modeling, process model'
        },
        {
            'ID': '10.4123/123545', 'url': 'https://doi.org/10.4123/123545', 'year': '2017',
            'keywords': 'machine learning, process model'
        },

    ]

    return docs


class TestWeightedNodeGraph(TestCase):

    def test_mash_up_duplicate_nodes(self):
        graph = WeightedNodeGraph()

        graph.from_dict(generate_test_docs())
        self.assertEqual(11, len(graph.nodes))
        graph.mash_up_duplicate_nodes()
        self.assertEqual(6, len(graph.nodes))

        self.assertEqual(3, graph.nodes[0].get_count())
        self.assertEqual(2, len(graph.nodes[0].get_links()))

        self.assertEqual(2, graph.nodes[0].get_links()[0].get_value())  # ml -> variability modelling
        self.assertEqual(3, graph.nodes[0].get_links()[1].get_value())  # ml -> process modell

    def test_purify_keywords(self):
        graph = WeightedNodeGraph()
        test_data = 'Machine LeArnIng, Home OffICe'
        expected_data = ['machine learning', 'home office']
        actual_data = graph.purify_keywords(test_data)
        self.assertEqual(expected_data, actual_data)

    def test_reduce_keys(self):
        test_data = generate_test_docs()[0]
        expected_data = {'keywords': ['machine learning', 'variability modeling', 'process model'], 'year': '2017'}

        actual_data = WeightedNodeGraph.reduce_keys(test_data)
        self.assertEqual(expected_data, actual_data)
