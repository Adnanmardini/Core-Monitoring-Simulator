import threading
import random
import time

core_results = {}  # Shared dictionary for core results
completed_cores = []  # List to track cores that successfully complete tasks

def core_task(core_id, stop_event):
    task_count = 0  # Track how many tasks a core completes
    while not stop_event.is_set():
        # Simulate task with a higher fault probability
        result = random.randint(1, 100)
        if random.random() < 0.3:  # 30% chance of fault
            result = -1  # Simulated error
        core_results[core_id] = result

        if result != -1:
            task_count += 1  # Increment successful task count

        #Processing Delay: The time.sleep call simulates the time a core 
        #takes to process a task, adding randomness to the simulation.
        time.sleep(random.uniform(0.5, 1.5))  # Simulate processing time

    # Add core to completed_cores when done
    completed_cores.append((core_id, task_count))

def start_cores(num_cores):
    stop_events = {}
    threads = []
    for i in range(num_cores):
        stop_event = threading.Event()
        stop_events[i] = stop_event
        thread = threading.Thread(target=core_task, args=(i, stop_event))
        threads.append(thread)
        thread.start()
    return stop_events, threads
