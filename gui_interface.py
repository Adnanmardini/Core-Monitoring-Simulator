import tkinter as tk
from tkinter import ttk
from threading import Thread, Event
from core_simulator import start_cores, core_results
from monitor import monitor_and_quarantine, faulty_cores, successful_tasks
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class CoreMonitoringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Core Monitoring System")
        self.root.geometry("800x600")
        self.threads = []
        self.stop_events = {}
        self.monitor_thread = None
        self.simulation_end_event = Event()
        self.simulation_duration = 10  # Simulation duration in seconds
        self.paused = False

        # Header
        ttk.Label(root, text="Core Monitoring System", font=("Arial", 18)).pack(pady=10)

        # Buttons
        self.start_button = ttk.Button(root, text="Start Simulation", command=self.start_simulation)
        self.start_button.pack(pady=10)

        self.stop_button = ttk.Button(root, text="Stop Simulation", command=self.stop_simulation)
        self.stop_button.pack(pady=10)
        self.stop_button.config(state=tk.DISABLED)

        self.pause_button = ttk.Button(root, text="Pause Simulation", command=self.pause_simulation)
        self.pause_button.pack(pady=5)

        self.resume_button = ttk.Button(root, text="Resume Simulation", command=self.resume_simulation)
        self.resume_button.pack(pady=5)
        self.resume_button.config(state=tk.DISABLED)

        self.summary_button = ttk.Button(root, text="Show Summary", command=self.display_summary)
        self.summary_button.pack(pady=10)
        self.summary_button.config(state=tk.DISABLED)

        # New Simulation Button
        self.new_simulation_button = ttk.Button(root, text="Run New Simulation", command=self.run_new_simulation)
        self.new_simulation_button.pack(pady=10)
        self.new_simulation_button.config(state=tk.DISABLED)  # Disable initially

        # User Input for simulation parameters
        ttk.Label(root, text="Number of Cores:").pack(pady=5)
        self.num_cores_entry = ttk.Entry(root)
        self.num_cores_entry.pack(pady=5)
        self.num_cores_entry.insert(0, "5")

        # Widgets for specifying the number of cores and the speed of the simulation
        ttk.Label(root, text="Simulation Time:").pack(pady=5)
        self.speed_slider = ttk.Scale(
            root, 
            from_=1, 
            to_=60,  # Adjust the range to represent seconds (e.g., 1 to 60 seconds)
            orient="horizontal", 
            command=self.update_simulation_duration  # Bind the slider to the update method
        )
        self.speed_slider.pack(pady=5)
        self.speed_slider.set(self.simulation_duration)  # Set initial slider value to match the default duration

        # Log Display A text widget to display real-time log messages about the simulation.
        ttk.Label(root, text="Activity Log:", font=("Arial", 18)).pack(anchor="w", padx=10)
        self.log_text = tk.Text(root, height=20, width=130, state=tk.DISABLED)
        self.log_text.pack(pady=10)

        # Graph Display Button (Ensure it is visible)
        self.plot_button = ttk.Button(root, text="Show Task Graph", command=self.plot_graph)
        self.plot_button.pack(pady=10)  # Adding this button and ensuring it is below other buttons

    def start_simulation(self):
        """Start the simulation."""
        self.log("Starting simulation...")
        num_cores = int(self.num_cores_entry.get())  # Get the user input for number of cores
        self.stop_events, self.threads = start_cores(num_cores)

        # Start monitoring thread
        self.monitor_thread = Thread(target=self.monitor_cores)
        self.monitor_thread.start()

        # Enable Stop button and disable Start button
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.summary_button.config(state=tk.DISABLED)
        self.new_simulation_button.config(state=tk.DISABLED)  # Disable "New Simulation" button during simulation

        # Automatically stop the simulation after the duration
        Thread(target=self.auto_stop_simulation).start()

    def stop_simulation(self):
        """Stop the simulation."""
        self.log("Stopping simulation...")
        self.simulation_end_event.set()
        for stop_event in self.stop_events.values():
            stop_event.set()
        for thread in self.threads:
            thread.join()
        if self.monitor_thread:
            self.monitor_thread.join()

        # Enable Start button and disable Stop button
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.summary_button.config(state=tk.NORMAL)
        self.new_simulation_button.config(state=tk.NORMAL)  # Enable "New Simulation" button

        self.log("Simulation stopped.")

    def auto_stop_simulation(self):
        """Automatically stop the simulation after the updated duration."""
        while not self.simulation_end_event.is_set():
            remaining_time = self.simulation_duration  # Use the updated duration
            self.simulation_end_event.wait(timeout=remaining_time)
            if not self.simulation_end_event.is_set():
                self.log(f"Simulation completed after {remaining_time} seconds.")
                self.stop_simulation()

    def monitor_cores(self):
        """Monitor cores for faults and successful tasks."""
        monitor_and_quarantine(self.stop_events, self.simulation_end_event)

    def plot_graph(self):
        """Open a new window to show the graph."""
        # Create a new Toplevel window for the graph
        graph_window = tk.Toplevel(self.root)
        graph_window.title("Core Task Graph")
        graph_window.geometry("800x600")  # Set size of the new window

        # Create a Matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 6))  # Increase figure size for better visibility
        ax.bar(successful_tasks.keys(), successful_tasks.values(), color='green')
        ax.bar(faulty_cores, [successful_tasks.get(core, 0) for core in faulty_cores], color='red')

        ax.set_xlabel('Core ID')
        ax.set_ylabel('Number of Tasks')
        ax.set_title('Core Task Summary')
        ax.legend()

        # Embed the plot into the new window
        canvas = FigureCanvasTkAgg(fig, graph_window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=20)
        canvas.draw()

    def display_summary(self):
        """Display a summary of the simulation results."""
        self.log("\n--- Detailed Simulation Summary ---")
        self.log("Cores Completed Tasks:")
        for core_id, task_count in successful_tasks.items():
            self.log(f"Core {core_id}: {task_count} successful tasks")

        self.log("\nFaulty Cores Quarantined:")
        for core_id in faulty_cores:
            self.log(f"Core {core_id}")

        # Minimized Summary
        total_quarantined = len(faulty_cores)
        non_quarantined_cores = [core_id for core_id in successful_tasks if core_id not in faulty_cores]
        average_successful_tasks = (
            sum(successful_tasks[core_id] for core_id in non_quarantined_cores) / len(non_quarantined_cores)
            if non_quarantined_cores else 0
        )

        self.log("\n--- Minimized Summary ---")
        self.log(f"Total Cores Quarantined: {total_quarantined}")
        self.log(f"Average Successful Tasks (Non-Quarantined): {average_successful_tasks:.2f}")

    def pause_simulation(self):
        """Pause the simulation by setting the paused flag to True."""
        self.paused = True
        self.log("Simulation paused.")
        self.pause_button.config(state=tk.DISABLED)
        self.resume_button.config(state=tk.NORMAL)

    def resume_simulation(self):
        """Resume the simulation by clearing the paused flag."""
        self.paused = False
        self.log("Simulation resumed.")
        self.pause_button.config(state=tk.NORMAL)
        self.resume_button.config(state=tk.DISABLED)

    def run_new_simulation(self):
        """Run a new simulation after resetting data."""
        self.reset_simulation_data()
        self.log("Running a new simulation...")
        self.start_simulation()  # Start the new simulation

    def reset_simulation_data(self):
        """Clear previous simulation results and reset the GUI."""
        successful_tasks.clear()
        faulty_cores.clear()
        self.stop_events = {}
        self.threads = []
        self.simulation_end_event.clear()
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)  # Clear the log window
        self.log_text.config(state=tk.DISABLED)

    def log(self, message):
        """Log messages to the activity log."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def update_simulation_duration(self, value):
        """Update simulation duration based on the slider's value."""
        self.simulation_duration = int(float(value))  # Convert slider value to an integer
        self.log(f"Simulation duration updated to {self.simulation_duration} seconds.")


if __name__ == "__main__":
    root = tk.Tk()
    app = CoreMonitoringApp(root)
    root.mainloop()
