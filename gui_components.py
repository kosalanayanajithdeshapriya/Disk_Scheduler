"""
GUI Components for Disk Scheduler
Modular GUI components for better organization
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class InputFrame:
    """Input parameter frame component"""

    def __init__(self, parent):
        self.frame = tk.LabelFrame(
            parent,
            text="Input Parameters",
            font=('Arial', 12, 'bold'),
            bg='#ffffff',
            padx=20,
            pady=20
        )

        self.create_widgets()

    def create_widgets(self):
        """Create input widgets"""
        # Request Queue
        tk.Label(
            self.frame, 
            text="Request Queue (comma-separated):", 
            font=('Arial', 10), 
            bg='#ffffff'
        ).grid(row=0, column=0, sticky='w', pady=5)

        self.request_entry = tk.Entry(self.frame, width=50, font=('Arial', 10))
        self.request_entry.grid(row=0, column=1, pady=5, padx=10)
        self.request_entry.insert(0, "82, 170, 43, 140, 24, 16, 190")

        # Head Start Position
        tk.Label(
            self.frame, 
            text="Initial Head Position:", 
            font=('Arial', 10), 
            bg='#ffffff'
        ).grid(row=1, column=0, sticky='w', pady=5)

        self.head_entry = tk.Entry(self.frame, width=20, font=('Arial', 10))
        self.head_entry.grid(row=1, column=1, sticky='w', pady=5, padx=10)
        self.head_entry.insert(0, "50")

        # Disk Size
        tk.Label(
            self.frame, 
            text="Disk Size (cylinders):", 
            font=('Arial', 10), 
            bg='#ffffff'
        ).grid(row=2, column=0, sticky='w', pady=5)

        self.disk_size_entry = tk.Entry(self.frame, width=20, font=('Arial', 10))
        self.disk_size_entry.grid(row=2, column=1, sticky='w', pady=5, padx=10)
        self.disk_size_entry.insert(0, "200")

        # Direction
        tk.Label(
            self.frame, 
            text="Initial Direction:", 
            font=('Arial', 10), 
            bg='#ffffff'
        ).grid(row=3, column=0, sticky='w', pady=5)

        self.direction_var = tk.StringVar(value='right')
        direction_frame = tk.Frame(self.frame, bg='#ffffff')
        direction_frame.grid(row=3, column=1, sticky='w', pady=5, padx=10)

        tk.Radiobutton(
            direction_frame, 
            text="Right", 
            variable=self.direction_var, 
            value='right', 
            bg='#ffffff'
        ).pack(side='left', padx=5)

        tk.Radiobutton(
            direction_frame, 
            text="Left", 
            variable=self.direction_var, 
            value='left', 
            bg='#ffffff'
        ).pack(side='left', padx=5)

    def get_values(self):
        """Get all input values"""
        return {
            'requests': self.request_entry.get(),
            'head': self.head_entry.get(),
            'disk_size': self.disk_size_entry.get(),
            'direction': self.direction_var.get()
        }

    def clear(self):
        """Clear all inputs"""
        self.request_entry.delete(0, tk.END)
        self.head_entry.delete(0, tk.END)
        self.disk_size_entry.delete(0, tk.END)
        self.direction_var.set('right')


class ResultsDisplay:
    """Results display component"""

    def __init__(self, parent):
        self.frame = tk.LabelFrame(
            parent,
            text="Algorithm Results & Comparison",
            font=('Arial', 12, 'bold'),
            bg='#ffffff',
            padx=10,
            pady=10
        )

        self.create_widgets()

    def create_widgets(self):
        """Create results display widgets"""
        text_frame = tk.Frame(self.frame, bg='#ffffff')
        text_frame.pack(fill='both', expand=True)

        # Scrollbar
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')

        # Text widget
        self.text_widget = tk.Text(
            text_frame,
            height=25,
            width=60,
            font=('Courier', 9),
            yscrollcommand=scrollbar.set,
            wrap='word',
            bg='#f9f9f9'
        )
        self.text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.text_widget.yview)

        # Configure tags for colored text
        self.text_widget.tag_config('header', font=('Courier', 10, 'bold'), foreground='#2196F3')
        self.text_widget.tag_config('best', font=('Courier', 9, 'bold'), foreground='#4CAF50')
        self.text_widget.tag_config('metric', foreground='#FF5722')

    def display_text(self, text):
        """Display text in the widget"""
        self.text_widget.delete('1.0', tk.END)
        self.text_widget.insert(tk.END, text)

    def clear(self):
        """Clear display"""
        self.text_widget.delete('1.0', tk.END)


class VisualizationPanel:
    """Visualization panel component"""

    def __init__(self, parent):
        self.frame = tk.LabelFrame(
            parent,
            text="Head Movement Visualization",
            font=('Arial', 12, 'bold'),
            bg='#ffffff',
            padx=10,
            pady=10
        )

        self.current_canvas = None
        self.create_widgets()

    def create_widgets(self):
        """Create visualization widgets"""
        # Algorithm selection
        control_frame = tk.Frame(self.frame, bg='#ffffff')
        control_frame.pack(pady=5)

        tk.Label(
            control_frame, 
            text="Select Algorithm:", 
            font=('Arial', 10), 
            bg='#ffffff'
        ).pack(side='left', padx=5)

        self.algo_var = tk.StringVar(value='FCFS')
        self.algo_combo = ttk.Combobox(
            control_frame,
            textvariable=self.algo_var,
            values=['FCFS', 'SCAN', 'C-SCAN', 'LOOK', 'C-LOOK'],
            state='readonly',
            width=15
        )
        self.algo_combo.pack(side='left', padx=5)

        # Canvas frame
        self.canvas_frame = tk.Frame(self.frame, bg='#ffffff')
        self.canvas_frame.pack(fill='both', expand=True, pady=10)

    def visualize(self, algo_name, result, head_start):
        """Create visualization for selected algorithm"""
        # Clear previous canvas
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        # Create figure
        fig = Figure(figsize=(7, 5), dpi=100)
        ax = fig.add_subplot(111)

        sequence = result['sequence']
        x_pos = list(range(len(sequence)))

        # Plot head movement
        ax.plot(x_pos, sequence, 'b-o', linewidth=2.5, markersize=8, 
                label='Head Movement', markerfacecolor='#2196F3', 
                markeredgecolor='white', markeredgewidth=1.5)

        # Initial position line
        ax.axhline(y=head_start, color='red', linestyle='--', 
                   linewidth=1.5, alpha=0.7, label=f'Initial Position ({head_start})')

        # Styling
        ax.set_xlabel('Sequence Order', fontsize=12, fontweight='bold')
        ax.set_ylabel('Cylinder Number', fontsize=12, fontweight='bold')
        ax.set_title(
            f'{algo_name} Algorithm\nTotal Seek: {result["seek_count"]} cylinders | ' +
            f'Avg: {result["avg_seek_time"]:.2f} cylinders/request',
            fontsize=12, fontweight='bold', pad=15
        )
        ax.grid(True, alpha=0.3, linestyle=':', linewidth=1)
        ax.legend(loc='best', fontsize=10)

        # Annotate start
        ax.annotate('START', xy=(0, sequence[0]), 
                   xytext=(0, sequence[0] + 15),
                   fontsize=10, ha='center', color='green', 
                   fontweight='bold',
                   arrowprops=dict(arrowstyle='->', color='green', lw=2))

        # Annotate end
        ax.annotate('END', xy=(len(sequence)-1, sequence[-1]), 
                   xytext=(len(sequence)-1, sequence[-1] - 15),
                   fontsize=10, ha='center', color='red', 
                   fontweight='bold',
                   arrowprops=dict(arrowstyle='->', color='red', lw=2))

        # Add cylinder labels at key points
        for i in [0, len(sequence)-1]:
            ax.text(i, sequence[i], f'  {sequence[i]}', 
                   fontsize=9, va='center', fontweight='bold')

        fig.tight_layout()

        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
        self.current_canvas = canvas

    def clear(self):
        """Clear visualization"""
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()


class ComparisonChart:
    """Comparison chart component"""

    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg='#ffffff')

    def create_bar_chart(self, results):
        """Create bar chart comparing all algorithms"""
        fig = Figure(figsize=(8, 4), dpi=100)
        ax = fig.add_subplot(111)

        algorithms = list(results.keys())
        seek_counts = [results[algo]['seek_count'] for algo in algorithms]

        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
        bars = ax.bar(algorithms, seek_counts, color=colors, edgecolor='black', linewidth=1.5)

        # Highlight best algorithm
        best_idx = seek_counts.index(min(seek_counts))
        bars[best_idx].set_color('#4CAF50')
        bars[best_idx].set_edgecolor('#2E7D32')
        bars[best_idx].set_linewidth(3)

        # Labels and title
        ax.set_xlabel('Algorithms', fontsize=12, fontweight='bold')
        ax.set_ylabel('Total Seek Count (cylinders)', fontsize=12, fontweight='bold')
        ax.set_title('Algorithm Performance Comparison', fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3, linestyle='--')

        # Add value labels on bars
        for i, (bar, count) in enumerate(zip(bars, seek_counts)):
            height = bar.get_height()
            label = f'{count}'
            if i == best_idx:
                label += '\n★ BEST'
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   label, ha='center', va='bottom', fontweight='bold', fontsize=9)

        fig.tight_layout()

        # Embed in frame
        canvas = FigureCanvasTkAgg(fig, master=self.frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

        return canvas