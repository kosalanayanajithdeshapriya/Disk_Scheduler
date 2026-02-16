🖴 Disk Scheduling Algorithm Visualizer
A comprehensive GUI application to compare and visualize 5 disk scheduling algorithms with interactive charts and detailed performance analysis.

Python
Tkinter
Matplotlib

📋 Table of Contents
Features

Algorithms

Installation

Usage

Project Structure

Screenshots

Examples

Contributing

✨ Features
🎯 Core Features
5 Disk Scheduling Algorithms: FCFS, SCAN, C-SCAN, LOOK, C-LOOK

Interactive GUI: User-friendly interface with Tkinter

Real-time Visualization: Matplotlib-powered head movement graphs

Comparative Analysis: Side-by-side algorithm comparison

Performance Metrics: Total seek time, average seek time, sequences

Best Algorithm Recommendation: Automatic optimal algorithm selection

Export Functionality: Save results to CSV file

🎨 GUI Components
Input parameter panel

Results display with scrolling

Interactive visualization panel

Comparison bar charts

Algorithm selection dropdown

Menu bar with export and help options

🔧 Algorithms
1. FCFS (First Come First Serve)
Strategy: Services requests in arrival order

Pros: Simple, fair, no starvation

Cons: High seek time

Use Case: Light loads, fairness critical

2. SCAN (Elevator Algorithm)
Strategy: Moves to disk end, then reverses

Pros: Better than FCFS for heavy loads

Cons: Unnecessary end travel

Use Case: Heavy loads, uniform distribution

3. C-SCAN (Circular SCAN)
Strategy: Moves to end, jumps to start

Pros: Uniform waiting time

Cons: Long return journey

Use Case: Consistent response time needed

4. LOOK
Strategy: Reverses at last request

Pros: More efficient than SCAN

Cons: Variable waiting times

Use Case: General purpose systems

5. C-LOOK
Strategy: Jumps from last to first request

Pros: Lowest seek time (usually best)

Cons: Slight complexity

Use Case: Most scenarios (optimal)

📦 Installation
Prerequisites
Python 3.7 or higher

pip package manager

Step 1: Clone or Download
bash
# Create project directory
mkdir Disk-Scheduling-Visualizer
cd Disk-Scheduling-Visualizer

# Copy all project files to this directory
Step 2: Install Dependencies
bash
# Install matplotlib
pip install matplotlib
Note: tkinter usually comes pre-installed with Python.

If tkinter is not installed:

Ubuntu/Debian: sudo apt-get install python3-tk

macOS: Included with Python

Windows: Included with Python

Step 3: Verify Installation
bash
python -c "import tkinter; import matplotlib; print('All dependencies installed!')"
🚀 Usage
Running the Application
bash
python disk_scheduler_gui.py
Or on Windows, double-click:

bash
run.bat
Step-by-Step Guide
Enter Request Queue

Input comma-separated cylinder numbers

Example: 82, 170, 43, 140, 24, 16, 190

Set Initial Head Position

Enter starting cylinder (e.g., 50)

Specify Disk Size

Enter total cylinders (e.g., 200)

Choose Direction

Select Right or Left for initial head movement

Calculate

Click "⚡ Calculate All Algorithms"

View results in the left panel

Visualize

Select algorithm from dropdown

Click "📊 Visualize Selected"

See head movement graph

Compare

Click "📈 Show Comparison"

View bar chart comparing all algorithms

Export (Optional)

File → Export Results (CSV)

Save analysis to CSV file

📁 Project Structure
text
Disk-Scheduling-Visualizer/
│
├── disk_scheduler_gui.py       # Main application (entry point)
├── algorithms.py               # All 5 scheduling algorithms
├── gui_components.py           # GUI component classes
├── utils.py                    # Utility & validation functions
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── .gitignore                  # Git ignore file
└── run.bat                     # Windows batch file to run app
File Descriptions
File	Purpose	Lines
disk_scheduler_gui.py	Main application & GUI	~350
algorithms.py	Algorithm implementations	~300
gui_components.py	GUI component classes	~350
utils.py	Helper functions	~150
📸 Screenshots
Main Application Window
text
┌─────────────────────────────────────────────────────────────┐
│     🖴 Disk Scheduling Algorithm Visualizer 🖴              │
├─────────────────────────────────────────────────────────────┤
│  Input Parameters                                           │
│  • Request Queue: [82, 170, 43, 140, 24, 16, 190]         │
│  • Initial Head:                                        │
│  • Disk Size:                                          │
│  • Direction: ⦿ Right  ○ Left                              │
├─────────────────────────────────────────────────────────────┤
│  [Calculate] [Visualize] [Compare] [Clear]                 │
├───────────────────────────┬─────────────────────────────────┤
│  Results Display          │  Visualization Panel            │
│  ─────────────           │  ──────────────────            │
│  FCFS: 631 cylinders     │  [Graph showing head movement]  │
│  SCAN: 236 cylinders     │                                 │
│  C-SCAN: 187 cylinders   │                                 │
│  LOOK: 208 cylinders     │                                 │
│  C-LOOK: 194 ★ BEST      │                                 │
└───────────────────────────┴─────────────────────────────────┘
📊 Examples
Example 1: Standard Test Case
Input:

Request Queue: 82, 170, 43, 140, 24, 16, 190

Initial Head: 50

Disk Size: 200

Direction: Right

Expected Results:

Algorithm	Total Seek	Avg Seek	Winner
FCFS	631	90.14	❌
SCAN	236	33.71	❌
C-SCAN	187	26.71	❌
LOOK	208	29.71	❌
C-LOOK	194	27.71	✅
Example 2: Sequential Requests
Input:

Request Queue: 10, 20, 30, 40, 50, 60

Initial Head: 0

Direction: Right

Expected: All algorithms perform similarly (sequential pattern)

Example 3: Random Distribution
Input:

Request Queue: 176, 79, 34, 60, 92, 11, 41, 114

Initial Head: 50

Direction: Right

Expected: C-LOOK and LOOK show significant performance advantage

🎓 Educational Value
This application is perfect for:

Operating Systems courses

Computer Science students

Understanding disk I/O optimization

Visual learning of scheduling algorithms

Performance analysis practice

📈 Performance Metrics
Metrics Calculated
Total Seek Count: Sum of all cylinder movements

Average Seek Time: Total / Number of requests

Seek Sequence: Complete order of visits

Movement Count: Number of direction changes

Formula
text
Seek Distance = |Current Position - Next Position|
Total Seek = Σ(Seek Distance)
Average Seek = Total Seek / Number of Requests
🔍 Algorithm Complexity
Algorithm	Time Complexity	Space Complexity
FCFS	O(n)	O(n)
SCAN	O(n log n)	O(n)
C-SCAN	O(n log n)	O(n)
LOOK	O(n log n)	O(n)
C-LOOK	O(n log n)	O(n)
n = number of requests

🛠️ Customization
Modifying Default Values
Edit gui_components.py:

python
self.request_entry.insert(0, "YOUR,CUSTOM,VALUES")
self.head_entry.insert(0, "YOUR_HEAD_POSITION")
self.disk_size_entry.insert(0, "YOUR_DISK_SIZE")
Adding New Algorithms
Add algorithm method to algorithms.py

Update get_all_results() method

Add to algorithm dropdown in GUI

Changing Colors
Edit visualization colors in gui_components.py:

python
colors = ['#YOUR_COLOR_1', '#YOUR_COLOR_2', ...]
🐛 Troubleshooting
Issue: ModuleNotFoundError: No module named 'matplotlib'
Solution: pip install matplotlib

Issue: ModuleNotFoundError: No module named 'tkinter'
Solution: Install python3-tk (Ubuntu: sudo apt-get install python3-tk)

Issue: Application doesn't start
Solution: Ensure all 4 Python files are in same directory

Issue: Invalid input error
Solution:

Use only integers for cylinder numbers

Ensure all requests are within disk range (0 to disk_size-1)

Check that head position is valid

📝 License
This project is created for educational purposes and is free to use and modify.

👥 Contributing
Contributions are welcome! To contribute:

Fork the repository

Create a feature branch

Make your changes

Submit a pull request

Ideas for Contributions
Add SSTF (Shortest Seek Time First) algorithm

Implement animation for head movement

Add real-time statistics dashboard

Create web version with Flask

Add unit tests

📚 References
Operating System Concepts by Silberschatz, Galvin, Gagne

Modern Operating Systems by Andrew S. Tanenbaum

GeeksforGeeks - Disk Scheduling

🙏 Acknowledgments
Python Tkinter community

Matplotlib developers

Operating Systems educators worldwide

📧 Contact
For questions or suggestions, please open an issue or reach out!