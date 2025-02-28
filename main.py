from core_simulator import start_cores, completed_cores
from monitor import monitor_and_quarantine, faulty_cores, successful_tasks
import threading
import time

def main():
    num_cores = 5
    simulation_duration = 10  # Duration in seconds

    # Start core simulation
    print("Starting core simulation...")
    stop_events, threads = start_cores(num_cores)

    # Start monitoring system
    simulation_end_event = threading.Event()
    monitor_thread = threading.Thread(target=monitor_and_quarantine, args=(stop_events, simulation_end_event))
    monitor_thread.start()

    # Run simulation for the specified duration or until manually stopped
    simulation_end_event.wait(timeout=simulation_duration)

    # Stop all threads
    print("Stopping simulation...")
    for stop_event in stop_events.values():
        stop_event.set()
    for thread in threads:
        thread.join()
    monitor_thread.join()

    # Calculate summary statistics
    total_quarantined = len(faulty_cores)
    non_quarantined_cores = [core_id for core_id in successful_tasks if core_id not in faulty_cores]
    average_successful_tasks = (
        sum(successful_tasks[core_id] for core_id in non_quarantined_cores) / len(non_quarantined_cores)
        if non_quarantined_cores else 0
    )

    # Display detailed summary
    print("\n--- Detailed Simulation Summary ---")
    print("Cores Completed Tasks:")
    for core_id, task_count in successful_tasks.items():
        print(f"Core {core_id}: {task_count} successful tasks")

    print("\nFaulty Cores Quarantined:")
    for core_id in faulty_cores:
        print(f"Core {core_id}")

    # Display minimized summary
    print("\n--- Minimized Summary ---")
    print(f"Total Cores Quarantined: {total_quarantined}")
    print(f"Average Successful Tasks (Non-Quarantined): {average_successful_tasks:.2f}")

    print("\nSimulation complete.")

if __name__ == "__main__":
    main()
