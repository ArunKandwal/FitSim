# algorithms.py
from models import Process

def first_fit(blocks, processes):
    for process in processes:
        for block in blocks:
            if block.allocate(process):
                break
    return blocks

def best_fit(blocks, processes):
    for process in processes:
        best_index = -1
        min_diff = float('inf')
        for i, block in enumerate(blocks):
            if block.is_free and block.size >= process.size:
                diff = block.size - process.size
                if diff < min_diff:
                    min_diff = diff
                    best_index = i
        if best_index != -1:
            blocks[best_index].allocate(process)
    return blocks

def worst_fit(blocks, processes):
    for process in processes:
        worst_index = -1
        max_diff = -1
        for i, block in enumerate(blocks):
            if block.is_free and block.size >= process.size:
                diff = block.size - process.size
                if diff > max_diff:
                    max_diff = diff
                    worst_index = i
        if worst_index != -1:
            blocks[worst_index].allocate(process)
    return blocks

def next_fit(blocks, processes):
    n = len(blocks)
    j = 0
    for process in processes:
        count = 0
        while count < n:
            if blocks[j].allocate(process):
                break
            j = (j + 1) % n
            count += 1
    return blocks

def round_robin(blocks, processes, quantum=100):
    process_queue = processes.copy()
    while process_queue:
        process = process_queue.pop(0)
        allocated = False
        for i in range(len(blocks)):
            if blocks[i].is_free and blocks[i].size >= min(quantum, process.size):
                blocks[i].is_free = False
                blocks[i].allocated_to = process.name
                remaining = process.size - quantum
                if remaining > 0:
                    process_queue.append(Process(f"{process.name}-Q", remaining))
                allocated = True
                break
        if not allocated:
            process_queue.append(process)
    return blocks
