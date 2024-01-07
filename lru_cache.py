
import time
import sys
from typing import cast


class CacheNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.size = 0

        if self.value is not None:
            self.size = sys.getsizeof(self.value)

        self.next = None
        self.previous = None
        # mark creation time as "first touch"
        self.last_touched = int(time.time_ns()/1000)


class LRUCache:
    def __init__(self):
        self.cache = dict()
        self.head = None
        self.tail = None
        self.size = 0

    def get_num_objects_in_cache(self):
        return len(self.cache)

    def get_cache_size(self):
        return self.size

    def get(self, key):
        cache_item = self.cache.get(key, 'No Key')
        if cache_item is None or cache_item == 'No Key':
            return None
        else:
            cache_item = cast(CacheNode, cache_item)
            self.remove_node(cache_item)
            self.touch_node(cache_item)
            return cache_item

    def purge(self):
        node = self.head
        while node.next is not None:
            next_node = node.next
            self.remove_node(node)
            node = next_node

    '''
        Removes a list of nodes from both the cache and the linked list,
        typically called from the cache eviction monitor
    '''
    def remove_nodes(self, nodes_to_remove):
        for node in nodes_to_remove:
            self.remove(node)

    '''
        Removes single node from both the cache and the linked list
    '''
    def remove(self, node: CacheNode):
        if node is None:
            return None

        cache_item = self.cache.get(node.key, 'No Key')
        if cache_item is None or cache_item == 'No Key':
            # nothing to remove
            return None
        else:
            cache_item = cast(CacheNode, cache_item)
            self.remove_node(cache_item)
            cache_item = self.cache.pop(cache_item.key)
            self.size -= cache_item.size
            return cache_item

    def put(self, node: CacheNode):
        cache_item = self.cache.get(node.key, 'No Key')
        if cache_item is None or cache_item == 'No Key':
            self.touch_node(node)
            self.cache.update({node.key: node})
        else:
            # remove the existing cached node with the same key
            self.remove(cast(CacheNode, cache_item))
            # replace with what may or may not be the same data
            self.touch_node(node)
            self.cache.update({node.key: node})
        self.size += node.size

    '''
        Removes a node from the last touched linked-list
    '''
    def remove_node(self, node: CacheNode):
        if node is None:
            return

        if node.previous is not None:
            node.previous.next = node.next
        else:
            self.head = node.next

        if node.next is not None:
            node.next.previous = node.previous
        else:
            self.tail = node.previous

    '''
        Places the node to the tail-end of the doubly linked list
        because it was recently read or written, update time stamp
    '''
    def touch_node(self, node: CacheNode):
        if node is None:
            return

        if self.head is None:
            self.tail = node
            self.head = node
        else:
            self.tail.next = node
            node.previous = self.tail
            node.next = None
            self.tail = node

        self.tail.last_touched = int(time.time_ns()/1000)
