"""
Utility Functions for Disk Scheduler
Validation, formatting, and helper functions
"""

def validate_input(requests_str, head_str, disk_size_str):
    """
    Validate user inputs

    Args:
        requests_str (str): Comma-separated request queue
        head_str (str): Initial head position
        disk_size_str (str): Disk size

    Returns:
        tuple: (requests_list, head_position, disk_size) or raises ValueError
    """
    errors = []

    # Validate request queue
    try:
        requests = [int(x.strip()) for x in requests_str.split(',') if x.strip()]
        if not requests:
            errors.append("Request queue cannot be empty")
    except ValueError:
        errors.append("Request queue must contain only integers")
        requests = []

    # Validate head position
    try:
        head_start = int(head_str)
    except ValueError:
        errors.append("Initial head position must be an integer")
        head_start = 0

    # Validate disk size
    try:
        disk_size = int(disk_size_str)
        if disk_size <= 0:
            errors.append("Disk size must be positive")
    except ValueError:
        errors.append("Disk size must be an integer")
        disk_size = 0

    # Cross-validation
    if not errors:
        if head_start < 0 or head_start >= disk_size:
            errors.append(f"Head position must be between 0 and {disk_size - 1}")

        for req in requests:
            if req < 0 or req >= disk_size:
                errors.append(f"Request {req} is out of range (0-{disk_size - 1})")
                break

    if errors:
        raise ValueError("\n".join(errors))

    return requests, head_start, disk_size


def format_sequence(sequence, max_per_line=10):
    """
    Format sequence for display

    Args:
        sequence (list): List of cylinder numbers
        max_per_line (int): Maximum numbers per line

    Returns:
        str: Formatted sequence string
    """
    result = []
    for i in range(0, len(sequence), max_per_line):
        chunk = sequence[i:i + max_per_line]
        result.append(" → ".join(map(str, chunk)))
    return "\n".join(result)


def calculate_statistics(results):
    """
    Calculate statistical summary of results

    Args:
        results (dict): Results from all algorithms

    Returns:
        dict: Statistical summary
    """
    seek_counts = [result['seek_count'] for result in results.values()]

    return {
        'min_seek': min(seek_counts),
        'max_seek': max(seek_counts),
        'avg_seek': sum(seek_counts) / len(seek_counts),
        'range': max(seek_counts) - min(seek_counts)
    }


def get_algorithm_description(algo_name):
    """
    Get description of algorithm

    Args:
        algo_name (str): Algorithm name

    Returns:
        str: Description of the algorithm
    """
    descriptions = {
        'FCFS': 'Services requests in the order they arrive (simple but inefficient)',
        'SCAN': 'Moves head in one direction to disk end, then reverses (Elevator)',
        'C-SCAN': 'Moves to disk end, jumps to start, continues (Circular)',
        'LOOK': 'Like SCAN but reverses at last request (more efficient)',
        'C-LOOK': 'Like C-SCAN but jumps between requests (most efficient)'
    }
    return descriptions.get(algo_name, 'Unknown algorithm')


def format_result_text(algo_name, result, is_best=False):
    """
    Format algorithm result for text display

    Args:
        algo_name (str): Algorithm name
        result (dict): Algorithm result
        is_best (bool): Whether this is the best algorithm

    Returns:
        str: Formatted result text
    """
    text = f"{'=' * 60}\n"
    text += f"{algo_name} ALGORITHM"
    if is_best:
        text += " ★ BEST PERFORMANCE ★"
    text += f"\n{'=' * 60}\n\n"

    text += f"Description: {get_algorithm_description(algo_name)}\n\n"
    text += f"Seek Sequence:\n{format_sequence(result['sequence'])}\n\n"
    text += f"Total Seek Count: {result['seek_count']} cylinders\n"
    text += f"Average Seek Time: {result['avg_seek_time']:.2f} cylinders/request\n"
    text += f"Number of Movements: {len(result['sequence']) - 1}\n\n"

    return text

def export_results_to_csv(results, filename='results.csv'):
    """
    Export results to CSV file

    Args:
        results (dict): Results from all algorithms
        filename (str): Output filename
    """
    import csv

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Algorithm', 'Total Seek Count', 'Average Seek Time', 'Sequence Length'])

        for algo_name, result in results.items():
            writer.writerow([
                algo_name,
                result['seek_count'],
                f"{result['avg_seek_time']:.2f}",
                len(result['sequence'])
            ])


def export_results_to_pdf(results, inputs, filename='results.pdf'):
    """
    Export results to a professional PDF report using matplotlib

    Args:
        results (dict): Results from all algorithms
        inputs (dict): Original input parameters
        filename (str): Output filename
    """
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    import datetime

    # Theming (matching the app's dark professional look but optimized for PDF/print)
    primary_color = "#1565C0"  # Professional blue
    accent_color = "#3DDC84"   # Success green
    text_color = "#333333"
    grid_color = "#EEEEEE"

    with PdfPages(filename) as pdf:
        # Create a figure for the report
        fig = plt.figure(figsize=(8.5, 11))
        
        # 1. Header Section
        plt.text(0.5, 0.96, "Disk Scheduling Algorithm Visualizer — Report", 
                 ha='center', va='top', fontsize=18, fontweight='bold', color=primary_color)
        plt.text(0.5, 0.93, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                 ha='center', va='top', fontsize=10, color="#777777")
        plt.axhline(0.91, color=primary_color, linewidth=2)

        # 2. Input Parameters Section
        plt.text(0.05, 0.88, "Input Parameters", fontsize=14, fontweight='bold', color=primary_color)
        
        param_y = 0.85
        params = [
            ("Request Queue", f"[{', '.join(map(str, inputs.get('requests', [])))}]"),
            ("Initial Head", f"{inputs.get('head_start', 'N/A')}"),
            ("Disk Size", f"{inputs.get('disk_size', 'N/A')} cylinders"),
            ("Direction", f"{inputs.get('direction', 'N/A').upper()}"),
            ("Total Requests", f"{len(inputs.get('requests', []))}")
        ]
        
        for label, val in params:
            plt.text(0.08, param_y, f"{label}:", fontsize=10, fontweight='bold', color=text_color)
            plt.text(0.3, param_y, val, fontsize=10, color=text_color)
            param_y -= 0.025

        # 3. Comparative Summary Table
        plt.text(0.05, 0.72, "Comparative Summary (Ranked by Efficiency)", fontsize=14, fontweight='bold', color=primary_color)
        
        sorted_results = sorted(results.items(), key=lambda x: x[1]['seek_count'])
        
        # Define table data
        col_labels = ['Rank', 'Algorithm', 'Total Seek Count', 'Avg Seek Time', 'Efficiency']
        table_data = []
        best_seek = sorted_results[0][1]['seek_count']
        
        for i, (name, res) in enumerate(sorted_results):
            efficiency = "Best" if i == 0 else f"-{((res['seek_count'] - best_seek) / best_seek * 100):.1f}%"
            table_data.append([
                i + 1,
                name,
                f"{res['seek_count']} cyl",
                f"{res['avg_seek_time']:.2f}",
                efficiency
            ])

        # Create table
        table = plt.table(cellText=table_data, colLabels=col_labels, 
                          loc='center', bbox=[0.05, 0.52, 0.9, 0.18])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        
        # Style table header
        for (row, col), cell in table.get_celld().items():
            if row == 0:
                cell.set_text_props(weight='bold', color='white')
                cell.set_facecolor(primary_color)
            elif row == 1:
                cell.set_facecolor("#EBF5FB") # Light blue for best
            else:
                cell.set_facecolor('white')

        # 4. Visualization/Chart Section
        plt.text(0.05, 0.48, "Seek Count Comparison Chart", fontsize=14, fontweight='bold', color=primary_color)
        
        # Create a subplot area for the bar chart
        ax = fig.add_axes([0.12, 0.28, 0.76, 0.18])
        names = [x[0] for x in sorted_results]
        counts = [x[1]['seek_count'] for x in sorted_results]
        
        # Consistent colors from the GUI
        algo_colors = {
            "FCFS": "#4F8EF7", "SSTF": "#F7C948", "SCAN": "#3DDC84",
            "C-SCAN": "#FF8C42", "C-LOOK": "#A78BFA", "LOOK": "#FF6B8A"
        }
        bar_colors = [algo_colors.get(n, primary_color) for n in names]
        
        bars = ax.bar(names, counts, color=bar_colors, alpha=0.8, edgecolor="#555555")
        ax.set_ylabel("Total Seek Count", fontsize=9)
        ax.set_title("Total Head Movement by Algorithm", fontsize=10)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add labels on top of bars
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 1, int(yval), ha='center', va='bottom', fontsize=8)

        # 5. Conclusion Note
        plt.text(0.05, 0.2, "Conclusion:", fontsize=12, fontweight='bold', color=primary_color)
        rec_text = (f"The analysis identifies {sorted_results[0][0]} as the most efficient algorithm for this specific request queue, "
                    f"achieving the minimum seek count of {best_seek} cylinders. Using {sorted_results[0][0]} provides better "
                    f"disk I/O performance and reduced mechanical wear compared to the other tested algorithms.")
        
        # Wrap text manually for simplicity
        plt.text(0.05, 0.14, rec_text, fontsize=10, color=text_color, wrap=True,
                 bbox=dict(boxstyle='round,pad=1', facecolor='#F9F9F9', edgecolor=accent_color))

        # 6. Footer
        plt.text(0.5, 0.04, "Educational Tool — Disk Scheduling Algorithms", ha='center', fontsize=8, color="#AAAAAA")
        
        # Hide the main figure axes
        plt.gca().axis('off')
        
        # Save the page
        pdf.savefig(fig)
        plt.close(fig)
