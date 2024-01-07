# Author: m056084 (Mark Bransford)
# Mayo Foundation for Education and Research, copyright 2022

import psutil
import threading
import time
from lru_cache import LRUCache


class LRUEvictionMonitor:
    def __init__(self, cache: LRUCache, percentage_memory_usage=0.25, low_water_mark=0.4):
        # start to evict data from the cache when it comprises 80% of the physical memory
        # but keep the cache filled to be at, or greater than, 60% physical memory
        self.percentage_memory_usage = percentage_memory_usage
        self.low_water_mark = low_water_mark
        self.virtual_memory = psutil.virtual_memory()
        self.physical_memory = psutil.virtual_memory().total
        self.eviction_memory_threshold = percentage_memory_usage * self.physical_memory
        self.eviction_low_water_mark = low_water_mark * self.eviction_memory_threshold
        print('high water mark memory = ' + str(int((self.eviction_memory_threshold / (1024.0 * 1024.0)))))
        print('low water mark memory = ' + str(int(self.eviction_low_water_mark / (1024.0 * 1024.0))))
        self.cache = cache
        self.is_monitoring = True
        self.cache_monitor = None

    def monitor(self):
        while self.is_monitoring:
            time.sleep(10)
            self.inspect_cache()

    def start_monitoring(self):
        self.cache_monitor = threading.Thread(target=self.monitor)
        self.is_monitoring = True
        self.cache_monitor.start()

    def stop_monitoring(self):
        self.is_monitoring = False

    def inspect_cache(self):
        cache_capacity = int((self.eviction_memory_threshold - self.cache.get_cache_size()) / (1024.0 * 1024.0))
        print('remaining Cache capacity (Mb) ' + str(cache_capacity))
        if self.cache.get_cache_size() >= self.eviction_memory_threshold:
            print('cache eviction underway')
            eviction_candidates = self.get_eviction_candidates()
            self.cache.remove_nodes(eviction_candidates)

    def get_eviction_candidates(self):
        candidates = list()
        node = self.cache.head

        if node is None:
            return candidates

        candidates.append(node)
        memory_evicted = node.size

        while self.eviction_memory_threshold - memory_evicted > self.eviction_low_water_mark:
            node = node.next
            if node is None:
                break
            else:
                candidates.append(node)

            memory_evicted += node.size

        return candidates
