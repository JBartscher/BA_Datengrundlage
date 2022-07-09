from data_transform import Link


class Node:
    _count = 1

    _links: list[Link]

    def __init__(self):
        self._links = []

    def get_links(self) -> list[Link]:
        return self._links

    def get_count(self) -> int:
        return self._count

    def set_count(self, new_value: int):
        self._count = new_value

    def add_link(self, link: Link) -> None:
        return self._links.append(link)

    def update_link_value(self, link: Link, value: int):
        if link not in self._links:
            raise KeyError("link not existing in zhis nodes link list")
        i = self._links.index(link)
        self._links[i].set_value(value)
