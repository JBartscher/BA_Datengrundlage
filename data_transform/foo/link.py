from .node import Node


class Link:

    def __init__(self, source: Node, target: Node, value: int):
        self._source = source
        self._target = target
        self._value = value

    def get_source(self) -> Node:
        return self._source

    def get_target(self) -> Node:
        return self._target

    def get_value(self) -> int:
        return self._value

    def set_value(self, new_value: int):
        self._value = new_value

    def __hash__(self):
        return hash((self._target.get_keyword(), self._target.get_keyword()))

    def __eq__(self, other):
        # TODO this does not account for diffrences in value
        return isinstance(other, Link) and (
                (self.get_source() == other.get_source() and self.get_target() == other.get_target()) or (
                self.get_source() == other.get_target() and self.get_target() == other.get_source()))

    def __repr__(self):
        return f'{self._source} --> {self._target} : {self._value}'

    def merge_links(self, other: 'Link'):
        self._value += other.get_value()
