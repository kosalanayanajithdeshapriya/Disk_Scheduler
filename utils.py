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