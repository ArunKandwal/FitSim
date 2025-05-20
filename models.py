# models.py

class MemoryBlock:
    def __init__(self, size):
        self.size = size
        self.original_size = size
        self.is_free = True
        self.allocated_to = None

    def allocate(self, process):
        if self.is_free and self.size >= process.size:
            self.size -= process.size
            self.is_free = False
            self.allocated_to = process.name
            return True
        return False

    def reset(self):
        self.size = self.original_size
        self.is_free = True
        self.allocated_to = None


class Process:
    def __init__(self, name, size):
        self.name = name
        self.size = size
