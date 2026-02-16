# Disk Scheduling Algorithm Visualizer

A Python-based GUI application for comparing and visualizing disk scheduling algorithms with interactive charts and performance analysis.

## Overview

This application implements and compares five disk scheduling algorithms commonly used in operating systems:
- FCFS (First Come First Serve)
- SCAN (Elevator Algorithm)
- C-SCAN (Circular SCAN)
- LOOK
- C-LOOK

## Features

- Interactive GUI built with Tkinter
- Real-time visualization using Matplotlib
- Performance comparison charts
- Detailed metrics (seek time, average seek time, sequences)
- Best algorithm recommendation
- CSV export functionality
- Input validation and error handling

## Requirements

- Python 3.7 or higher
- matplotlib

sage
Enter comma-separated cylinder requests (e.g., 82, 170, 43, 140, 24, 16, 190)

Set initial head position (e.g., 50)

Specify disk size (e.g., 200)

Choose initial direction (Right or Left)

Click "Calculate All Algorithms" to see results

Use "Visualize Selected" to view head movement graphs

Click "Show Comparison" for performance bar chart

Example
Input:

Request Queue: 82, 170, 43, 140, 24, 16, 190

Initial Head: 50

Disk Size: 200

Direction: Right


Project Structure
text
Disk-Scheduling-Visualizer/
├── disk_scheduler_gui.py    # Main application
├── algorithms.py             # Algorithm implementations
├── gui_components.py         # GUI components
├── utils.py                  # Utility functions
├── requirements.txt          # Dependencies
└── README.md                 # Documentation
Algorithm Details
FCFS (First Come First Serve)
Services requests in arrival order

Simple but may result in high seek times

SCAN (Elevator Algorithm)
Moves head in one direction until the end, then reverses

Reduces seek time compared to FCFS

C-SCAN (Circular SCAN)
Moves to disk end, jumps to beginning, continues in same direction

Provides uniform wait time

LOOK
Similar to SCAN but reverses at the last request, not disk end

More efficient than SCAN

C-LOOK
Similar to C-SCAN but jumps from last to first request

Generally provides best performance

Technical Information
Time Complexity:

FCFS: O(n)

SCAN, C-SCAN, LOOK, C-LOOK: O(n log n)

Space Complexity: O(n) for all algorithms

Contributing
Contributions are welcome. Please follow these steps:

Fork the repository

Create a feature branch

Commit your changes

Push to the branch

Open a Pull Request

License
This project is created for educational purposes.

Contact
For questions or suggestions, please open an issue on GitHub.
# Clone the repository
git clone https://github.com/YOUR_USERNAME/Disk-Scheduling-Visualizer.git
cd Disk-Scheduling-Visualizer

# Install dependencies
pip install matplotlib

# Run the application
python disk_scheduler_gui.py
