# Author: m056084 (Mark Bransford)
# Mayo Foundation for Education and Research, copyright 2022

import unittest
import os
import threading
import random
import time
from lru_cache import LRUCache
from lru_cache import CacheNode
from lru_eviction import LRUEvictionMonitor


class TestLRUDataStructure(unittest.TestCase):

    def fill_data(self, nodes=20, mega_bytes=1):
        num_bytes = mega_bytes * 1024 * 1024
        cache = LRUCache()
        for i in range(nodes):
            key = str(i)
            value = bytearray(os.urandom(num_bytes))
            node = CacheNode(key, value)
            cache.put(node)
            
        self.assertTrue(cache is not None)
        return cache

    def add_data(self, cache=None, nodes=None, mega_bytes=1):
        self.assertTrue(cache is not None)
        num_bytes = mega_bytes * 1024 * 1024
        for i in range(nodes[0], nodes[1]):
            key = str(i)
            value = bytearray(os.urandom(num_bytes))
            node = CacheNode(key, value)
            cache.put(node)

    def test_eviction(self):
        cache = LRUCache()
        LRUEvictionMonitor(cache)

    def test_fill_data(self):
        cache = self.fill_data()
        self.assertEqual(20, cache.get_num_objects_in_cache())

    def test_get_none(self):
        cache = self.fill_data()
        node = cache.get('1000')
        self.assertEqual(node, None)

    def test_remove_none(self):
        cache = self.fill_data()
        node = CacheNode(key='abc', value='123')
        removed_node = cache.remove(node=node)
        self.assertEqual(removed_node, None)

    def test_remove(self):
        cache = self.fill_data()
        node = cache.get('1')
        removed_node = cache.remove(node=node)
        self.assertEqual(removed_node, node)

        node = cache.get('1')
        self.assertEqual(node, None)

        node = cache.head
        next_node = node.next
        self.assertEqual(node.key, '0')
        self.assertEqual(next_node.key, '2')

    def test_get(self):
        cache = self.fill_data()
        node = cache.get(str(0))
        tail = cache.tail
        self.assertEqual(str(0), tail.key)
        self.assertEqual(node, tail)

    def test_lru(self):
        cache = self.fill_data(nodes=100)

        for i in range(1, 100, 2):
            cache.get(str(i))

        node = None
        for i in reversed(range(1, 100, 2)):
            if i == 99:
                node = cache.tail
            else:
                node = node.previous

            self.assertEqual(node.key, str(i))

    def test_data_order(self):
        cache = self.fill_data()

        head = cache.head
        self.assertEqual(str(0), head.key)
        self.assertTrue(head.previous is None)
        tail = cache.tail
        self.assertEqual(str(19), tail.key)
        self.assertTrue(tail.next is None)

        node = None
        for i in range(20):
            if i == 0:
                node = cache.head
                continue

            if i == 19:
                next_node = node.next
                self.assertTrue(next_node.next is None)
                self.assertEqual(str(i), next_node.key)
                self.assertEqual(str(18), next_node.previous.key)
                break

            next_node = node.next
            self.assertEqual(str((i-1)), next_node.previous.key)
            self.assertEqual(str(i), next_node.key)
            self.assertEqual(str((i+1)), next_node.next.key)
            node = next_node

    def test_fill_cache_threaded(self):
        cache = LRUCache()
        tuple_list = list()
        tuple_list.append((0, 1001))
        tuple_list.append((1001, 2001))
        tuple_list.append((2001, 3001))
        tuple_list.append((3001, 4000))
        for a_list in tuple_list:
            cache_thread = threading.Thread(target=self.add_data, args=(cache, a_list,))
            cache_thread.start()
            cache_thread.join()

        indices_touched = list()
        for i in range(1000000):
            index = random.randint(0, 3999)
            indices_touched.append(index)
            cache.get(str(index))

        # join means main thread waits until is full
        while cache.get_num_objects_in_cache() < 4000:
            time.sleep(2)

        self.assertEqual(cache.get_num_objects_in_cache(), 4000)


if __name__ == '__main__':
    unittest.main()
