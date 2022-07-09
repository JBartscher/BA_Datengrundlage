from data_transform.Node import Node


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

    def __eq__(self, other):
        return (self.get_source() == other.get_source() and self.get_target() == other.get_target()) or (
                self.get_source() == other.get_target() and self.get_target() == other.get_source())
