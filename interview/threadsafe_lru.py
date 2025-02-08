from threading import Lock


class ListNode:
    def __init__(self, key=None, val=None, next=None, prev=None):
        self.key = key
        self.val = val
        self.next = next
        self.prev = prev


class LinkedList:
    def __init__(self):
        self.head = ListNode()
        self.tail = ListNode()
        self.head.next = self.tail
        self.tail.prev = self.head

    def append(self, node):
        """Inserts key at most recent position (tail)"""
        prev = self.tail.prev

        # Update current node
        node.prev = prev
        node.next = self.tail

        # Update prev node
        prev.next = node
        self.tail.prev = node

    def pop(self, node):
        """Removes node from LL"""
        node.prev.next = node.next
        node.next.prev = node.prev

    def popleft(self):
        tmp = self.head.next
        self.pop(self.head.next)
        return tmp.key

    def update(self, node):
        self.pop(node)
        self.append(node)


class LRUCache:
    def __init__(self, capacity: int):
        self.key_to_node = {}
        self.ll = LinkedList()
        self.capacity = capacity

    def get(self, key: int) -> int:
        # We need to update the key to be most recent in addition to returning the value
        if key not in self.key_to_node:
            return -1

        node = self.key_to_node[key]
        self.ll.update(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        # If key already in cache, remove it first so it can be readded (with new value and at most recent position)
        if key in self.key_to_node:
            node = self.key_to_node[key]
            self.ll.update(node)
            node.val = value
            return

        # Create new node and add to list
        node = ListNode(key=key, val=value)
        self.ll.append(node)
        self.key_to_node[key] = (
            node  # Note how this overwrites in the case of updating an existing node
        )

        # If list exceeds capacity, remove least recent
        if len(self.key_to_node) > self.capacity:
            del self.key_to_node[self.ll.popleft()]


# Subclass that adds locking
class ThreadSafeLRUCache(LRUCache):
    def __init__(self, capacity: int):
        super().__init__(capacity)
        self._lock = Lock()

    def get(self, key: int) -> int:
        with self._lock:
            return super().get(key)

    def put(self, key: int, value: int) -> None:
        with self._lock:
            super().put(key, value)
