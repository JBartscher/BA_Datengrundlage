from json import JSONEncoder
from typing import List, Any


class Node:
    _count = 1

    _links: list['Link']

    _keyword: str

    _year: int

    def __init__(self, keyword: str, year: int):
        self._links = []
        self._keyword = keyword
        self._year = year

    def get_links(self) -> list['Link']:
        return self._links

    def get_year(self) -> int:
        return self._year

    def get_keyword(self) -> str:
        return self._keyword

    def get_count(self) -> int:
        return self._count

    def set_count(self, new_value: int):
        self._count = new_value

    def add_link(self, link: 'Link') -> None:
        return self._links.append(link)

    def set_links(self, links: List['Link']):
        self._links = links

    def update_link_value(self, link: 'Link', value: int):
        if link not in self._links:
            raise KeyError(f"link{link} not existing in this nodes link list")
        i = self._links.index(link)
        self._links[i].set_value(value)

    def merge_node_into_this_node(self, other: 'Node'):
        self.set_count(self.get_count() + other._count)
        # missing_links = filter(lambda l: l not in self._links, other._links)
        self._links.extend(other._links)
        self.cleanup_links_of_node()

    def cleanup_links_of_node(self):
        seen = set()
        unique_links = list()

        tmp = self.get_links()
        for i, link in enumerate(tmp):

            if link.get_source() == link.get_target():
                continue

            if link in seen:
                index_of_link = unique_links.index(link)
                unique_links[index_of_link].merge_links(link)
                continue

            seen.add(link)
            unique_links.append(link)

        self._links = unique_links

    def __eq__(self, other: 'Node'):
        return isinstance(other, Node) and (self._keyword == other.get_keyword()) and (self._year == other.get_year())

    def __hash__(self):
        return hash((self._keyword, self._year))

    def __repr__(self):
        return f'keyword: {self._keyword}, year {self._year}, count: {self._count}, links: {self._links}'

    def __str__(self):
        return f'keyword: {self._keyword}, year {self._year}, count: {self._count}'

    @staticmethod
    def find_index_of_link_in_list(node, list_of_links: List['Link']):
        for i, v in enumerate(list_of_links):
            if v.get() == node.get_keyword():
                return i
        return -1


class NodeEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        return o.__dict__
