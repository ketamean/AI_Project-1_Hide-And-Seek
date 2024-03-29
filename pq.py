class PriorityQueue:
    """
        entries are typically tuples of the form (priority_number, data)
    """
    
    def __init__(self, entry = None) -> None:
        self.pq = {}
        if entry:
            num, data = entry
            self.pq[num] = [data]
            self.key = [num]

    def push(self, entry):
        from heapq import heappush
        num, data = entry
        if self.pq.get(num) == None:
            self.pq[num] = [data]
        else:
            self.pq[num].append(data)
        heappush(self.key, num)
    
    def pop(self):
        """
            return an entry (prior_num, data) with the smallest priority number
        """
        from heapq import heappop
        if self.key:
            num = heappop(self.key)
            return num, self.pq[num].pop()
        return None, None
    
    def is_empty(self):
        return len(self.key) == 0