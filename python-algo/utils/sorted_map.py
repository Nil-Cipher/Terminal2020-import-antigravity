# Sorted map based on a priority queue.
# It's designed to have O(log n) insertion and O(log n) weight changing.
class SortedMap:
    def __init__(self, popped=None):
        self.__prev = False
        self.pq = []
        self.entries = {}
        self.popped = popped

    # These two methods below are copied from the heapq module, and modified to return the result position.
    def __siftdown(self, startpos, pos):
        newitem = self.pq[pos]
        # Follow the path to the root, moving parents down until finding a place
        # newitem fits.
        while pos > startpos:
            parentpos = (pos - 1) >> 1
            parent = self.pq[parentpos]
            if newitem < parent:
                self.pq[pos] = parent
                self.entries[parent[1]] = pos
                pos = parentpos
                continue
            break
        self.pq[pos] = newitem
        self.entries[newitem[1]] = pos

    def __siftup(self, pos):
        endpos = len(self.pq)
        startpos = pos
        newitem = self.pq[pos]
        # Bubble up the smaller child until hitting a leaf.
        childpos = 2 * pos + 1    # leftmost child position
        while childpos < endpos:
            # Set childpos to index of smaller child.
            rightpos = childpos + 1
            if rightpos < endpos and not self.pq[childpos] < self.pq[rightpos]:
                childpos = rightpos
            # Move the smaller child up.
            self.pq[pos] = self.pq[childpos]
            self.entries[self.pq[pos][1]] = pos
            pos = childpos
            childpos = 2 * pos + 1
        # The leaf at pos is empty now.  Put newitem there, and bubble it up
        # to its final resting place (by sifting its parents down).
        self.pq[pos] = newitem
        self.entries[newitem[1]] = pos

        # Normally you'd want to start at startpos, but in this case, we always want to both sift up and down.
        self.__siftdown(0, pos)
    
    def __heappop(self):
        lastelt = self.pq.pop()

        if self.pq:
            returnitem = self.pq[0]
            self.pq[0] = lastelt
            self.__siftup(0)
            del self.entries[returnitem[1]]
            return returnitem
        
        del self.entries[lastelt[1]]
        assert not self.entries
        return lastelt

    def __setitem__(self, value, priority):
        if value in self.entries:
            self.pq[self.entries[value]] = (-priority, value)
            self.__siftup(self.entries[value])
        else:
            self.pq.append((-priority, value))
            self.__siftdown(0, len(self.pq) - 1)
        
    
    def __getitem__(self, value):
        return -self.pq[self.entries[value]][0]
    
    def __contains__(self, value):
        return value in self.entries
    
    def __len__(self):
        return len(self.pq)
    
    def __iter__(self):
        self.__prev = False
        return self
    def __next__(self):
        if not self.pq:
            raise StopIteration

        if self.__prev:
            priority, value = self.pq[0]
            self.__heappop()
            if self.popped:
                self.popped(priority, value)

        if not self.pq:
            raise StopIteration

        self.__prev = True
        priority, value = self.pq[0]
        return (-priority, value)