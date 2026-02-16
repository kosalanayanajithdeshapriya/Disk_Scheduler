"""
Disk Scheduling Algorithm Visualizer
Main Application File

This application compares 5 disk scheduling algorithms:
- FCFS (First Come First Serve)
- SCAN (Elevator Algorithm)
- C-SCAN (Circular SCAN)
- LOOK
- C-LOOK

Author: Educational Project
Date: 2026
"""

import tkinter as tk
from tkinter import messagebox, Menu
import sys

# Import custom modules
from algorithms import DiskScheduler
from utils import validate_input, format_result_text, calculate_statistics, export_results_to_csv
from gui_components import InputFrame, ResultsDisplay, VisualizationPanel, ComparisonChart


class DiskSchedulerApp:
    """Main application class"""

    def __init__(self, root):
        self.root = root
        self.root.title("Disk Scheduling Algorithm Visualizer")
        self.root.geometry("1400x850")
        self.root.configure(bg='#f0f0f0')

        # Try to set window icon (optional)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass

        # Data storage
        self.results = {}
        self.current_inputs = {}

        # Create menu bar
        self.create_menu()

        # Create GUI
        self.create_widgets()

        # Center window
        self.center_window()

    def create_menu(self):
        """Create menu bar"""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Results (CSV)", command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Help menu
        help_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Algorithm Info", command=self.show_algorithm_info)

    def create_widgets(self):
        """Create all GUI widgets"""
        # Title
        title_frame = tk.Frame(self.root, bg='#2196F3', height=60)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="🖴 Disk Scheduling Algorithm Visualizer 🖴",
            font=('Arial', 22, 'bold'),
            bg='#2196F3',
            fg='white'
        )
        title_label.pack(expand=True)

        # Input Frame
        self.input_frame = InputFrame(self.root)
        self.input_frame.frame.pack(padx=20, pady=10, fill='x')

        # Buttons Frame
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(pady=10)

        # Calculate Button
        self.calc_button = tk.Button(
            button_frame,
            text="⚡ Calculate All Algorithms",
            command=self.calculate_all,
            font=('Arial', 12, 'bold'),
            bg='#4CAF50',
            fg='white',
            padx=25,
            pady=12,
            cursor='hand2',
            relief='raised',
            bd=3
        )
        self.calc_button.pack(side='left', padx=5)

        # Visualize Button
        self.viz_button = tk.Button(
            button_frame,
            text="📊 Visualize Selected",
            command=self.visualize_selected,
            font=('Arial', 12, 'bold'),
            bg='#2196F3',
            fg='white',
            padx=25,
            pady=12,
            cursor='hand2',
            relief='raised',
            bd=3
        )
        self.viz_button.pack(side='left', padx=5)

        # Comparison Chart Button
        self.compare_button = tk.Button(
            button_frame,
            text="📈 Show Comparison",
            command=self.show_comparison,
            font=('Arial', 12, 'bold'),
            bg='#FF9800',
            fg='white',
            padx=25,
            pady=12,
            cursor='hand2',
            relief='raised',
            bd=3
        )
        self.compare_button.pack(side='left', padx=5)

        # Clear Button
        self.clear_button = tk.Button(
            button_frame,
            text="🗑️ Clear All",
            command=self.clear_all,
            font=('Arial', 12, 'bold'),
            bg='#f44336',
            fg='white',
            padx=25,
            pady=12,
            cursor='hand2',
            relief='raised',
            bd=3
        )
        self.clear_button.pack(side='left', padx=5)

        # Main content area
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(padx=20, pady=10, fill='both', expand=True)

        # Results Display (Left)
        self.results_display = ResultsDisplay(main_frame)
        self.results_display.frame.pack(side='left', fill='both', expand=True, padx=(0, 10))

        # Visualization Panel (Right)
        self.viz_panel = VisualizationPanel(main_frame)
        self.viz_panel.frame.pack(side='right', fill='both', expand=True)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=('Arial', 9),
            bg='#e0e0e0',
            anchor='w',
            relief='sunken',
            bd=1
        )
        status_bar.pack(side='bottom', fill='x')

    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def calculate_all(self):
        """Calculate all algorithms"""
        try:
            self.status_var.set("Calculating...")
            self.root.update()

            # Get inputs
            inputs = self.input_frame.get_values()

            # Validate
            requests, head_start, disk_size = validate_input(
                inputs['requests'],
                inputs['head'],
                inputs['disk_size']
            )

            # Store inputs
            self.current_inputs = {
                'requests': requests,
                'head_start': head_start,
                'disk_size': disk_size,
                'direction': inputs['direction']
            }

            # Create scheduler and calculate
            scheduler = DiskScheduler(
                requests, 
                head_start, 
                disk_size, 
                inputs['direction']
            )
            self.results = scheduler.get_all_results()

            # Display results
            self.display_results()

            # Update algorithm combo
            self.viz_panel.algo_combo.set('FCFS')

            self.status_var.set(f"✓ Calculated {len(self.results)} algorithms successfully")
            messagebox.showinfo(
                "Success", 
                f"All algorithms calculated successfully!\n\n" +
                f"Requests: {len(requests)}\n" +
                f"Best Algorithm: {scheduler.get_best_algorithm()[0]}"
            )

        except ValueError as e:
            self.status_var.set("Error in input validation")
            messagebox.showerror("Input Error", str(e))
        except Exception as e:
            self.status_var.set("Calculation error")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def display_results(self):
        """Display calculation results"""
        if not self.results:
            return

        # Get best algorithm
        best_algo = min(self.results.items(), key=lambda x: x[1]['seek_count'])

        # Build output text
        output = "=" * 70 + "\n"
        output += "INPUT PARAMETERS\n"
        output += "=" * 70 + "\n"
        output += f"Request Queue: {self.current_inputs['requests']}\n"
        output += f"Initial Head Position: {self.current_inputs['head_start']}\n"
        output += f"Disk Size: {self.current_inputs['disk_size']} cylinders\n"
        output += f"Direction: {self.current_inputs['direction'].upper()}\n\n"

        # Results for each algorithm
        for algo_name, result in self.results.items():
            is_best = (algo_name == best_algo[0])
            output += format_result_text(algo_name, result, is_best)

        # Summary
        stats = calculate_statistics(self.results)
        output += "=" * 70 + "\n"
        output += "STATISTICAL SUMMARY\n"
        output += "=" * 70 + "\n"
        output += f"Best Performance: {best_algo[0]} ({best_algo[1]['seek_count']} cylinders)\n"
        output += f"Worst Performance: {max(self.results.items(), key=lambda x: x[1]['seek_count'])[0]} "
        output += f"({stats['max_seek']} cylinders)\n"
        output += f"Average Seek Count: {stats['avg_seek']:.2f} cylinders\n"
        output += f"Performance Range: {stats['range']} cylinders\n\n"

        output += "RECOMMENDATION:\n"
        output += f"Use {best_algo[0]} algorithm for optimal performance!\n"

        # Display
        self.results_display.display_text(output)

    def visualize_selected(self):
        """Visualize selected algorithm"""
        if not self.results:
            messagebox.showwarning("No Data", "Please calculate algorithms first!")
            return

        try:
            algo_name = self.viz_panel.algo_var.get()
            result = self.results[algo_name]

            self.viz_panel.visualize(
                algo_name, 
                result, 
                self.current_inputs['head_start']
            )

            self.status_var.set(f"Visualized {algo_name} algorithm")

        except Exception as e:
            messagebox.showerror("Visualization Error", str(e))

    def show_comparison(self):
        """Show comparison chart"""
        if not self.results:
            messagebox.showwarning("No Data", "Please calculate algorithms first!")
            return

        try:
            # Create new window
            compare_window = tk.Toplevel(self.root)
            compare_window.title("Algorithm Comparison Chart")
            compare_window.geometry("900x500")

            # Create comparison chart
            chart = ComparisonChart(compare_window)
            chart.frame.pack(fill='both', expand=True, padx=20, pady=20)
            chart.create_bar_chart(self.results)

            self.status_var.set("Comparison chart displayed")

        except Exception as e:
            messagebox.showerror("Chart Error", str(e))

    def export_results(self):
        """Export results to CSV"""
        if not self.results:
            messagebox.showwarning("No Data", "Please calculate algorithms first!")
            return

        try:
            filename = f"disk_scheduler_results.csv"
            export_results_to_csv(self.results, filename)
            messagebox.showinfo("Export Success", f"Results exported to {filename}")
            self.status_var.set(f"Results exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    def clear_all(self):
        """Clear all data and reset"""
        self.input_frame.clear()
        self.results_display.clear()
        self.viz_panel.clear()
        self.results = {}
        self.current_inputs = {}
        self.status_var.set("All data cleared")

    def show_about(self):
        """Show about dialog"""
        about_text = """
        Disk Scheduling Algorithm Visualizer
        Version 1.0

        A comprehensive tool to compare and visualize
        5 disk scheduling algorithms.

        Algorithms Implemented:
        • FCFS (First Come First Serve)
        • SCAN (Elevator Algorithm)
        • C-SCAN (Circular SCAN)
        • LOOK
        • C-LOOK

        Created for educational purposes.
        © 2026
        """
        messagebox.showinfo("About", about_text)

    def show_algorithm_info(self):
        """Show algorithm information"""
        info_window = tk.Toplevel(self.root)
        info_window.title("Algorithm Information")
        info_window.geometry("700x600")

        text_widget = tk.Text(info_window, wrap='word', font=('Arial', 10), padx=20, pady=20)
        text_widget.pack(fill='both', expand=True)

        info_text = """
DISK SCHEDULING ALGORITHMS - DETAILED INFORMATION

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. FCFS (First Come First Serve)
   • Simple queue-based approach
   • Services requests in arrival order
   • Advantages: Fair, no starvation
   • Disadvantages: High seek time, inefficient
   • Best for: Light loads, fairness critical

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2. SCAN (Elevator Algorithm)
   • Moves head in one direction to disk end
   • Reverses direction and continues
   • Advantages: Better than FCFS for heavy loads
   • Disadvantages: Unnecessary travel to disk end
   • Best for: Heavy loads with uniform distribution

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3. C-SCAN (Circular SCAN)
   • Moves to disk end, jumps to start
   • Services requests in one direction only
   • Advantages: Uniform waiting time
   • Disadvantages: Long return journey
   • Best for: Systems requiring consistent response

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4. LOOK
   • Like SCAN but reverses at last request
   • More efficient than SCAN
   • Advantages: No unnecessary disk end travel
   • Disadvantages: Variable waiting times
   • Best for: General purpose systems

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5. C-LOOK
   • Like C-SCAN but jumps from last to first request
   • Most efficient algorithm
   • Advantages: Lowest seek time, best throughput
   • Disadvantages: Slight implementation complexity
   • Best for: Most scenarios (usually optimal)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PERFORMANCE RANKING (Typical):
1. C-LOOK ★★★★★ (Best)
2. LOOK ★★★★☆
3. C-SCAN ★★★☆☆
4. SCAN ★★☆☆☆
5. FCFS ★☆☆☆☆ (Worst)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """

        text_widget.insert('1.0', info_text)
        text_widget.config(state='disabled')


def main():
    """Main entry point"""
    root = tk.Tk()
    app = DiskSchedulerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()