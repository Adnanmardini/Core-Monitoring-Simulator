import threading
import time
from core_simulator import core_results

faulty_cores = []  # Track faulty cores
successful_tasks = {}  # Dictionary to track successful tasks per core

def monitor_and_quarantine(stop_events, simulation_end_event):
    """
    Monitor core results and quarantine faulty cores.
    - Only quarantine cores if they produce a fault and have 0 successful tasks.
    - Only start evaluating cores after they have attempted enough tasks.
    
    Args:
        stop_events (dict): Dictionary of threading.Event() objects for each core.
        simulation_end_event (threading.Event): Event to signal the end of the simulation.
    """
    global successful_tasks

    while not simulation_end_event.is_set():
        for core_id, result in core_results.items():
            # Initialize successful tasks count if not already done
            if core_id not in successful_tasks:
                successful_tasks[core_id] = 0

            # Increment task attempts and check only after 1 task attempt
            if result == -1:  # Fault detected
                if successful_tasks[core_id] < 3 and core_id not in faulty_cores:
                    print(f"Fault detected on Core {core_id} with 0 successful tasks. Quarantining...")
                    faulty_cores.append(core_id)
                    stop_events[core_id].set()  # Stop the faulty core
            else:
                # Increment successful tasks for valid results
                successful_tasks[core_id] += 1

        # Check if all cores are stopped
        if all(event.is_set() for event in stop_events.values()):
            simulation_end_event.set()

        time.sleep(1)  # Periodic check every second
