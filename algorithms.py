"""
Disk Scheduling Algorithms Implementation
Contains: FCFS, SCAN, C-SCAN, LOOK, C-LOOK
"""

class DiskScheduler:
    """Core implementation of disk scheduling algorithms"""

    def __init__(self, requests, head_start, disk_size, direction='right'):
        """
        Initialize the disk scheduler

        Args:
            requests (list): List of cylinder requests
            head_start (int): Initial head position
            disk_size (int): Total number of cylinders
            direction (str): Initial direction ('right' or 'left')
        """
        self.requests = requests.copy()
        self.head_start = head_start
        self.disk_size = disk_size
        self.direction = direction.lower()

    def fcfs(self):
        """
        First Come First Serve (FCFS) Algorithm
        Services requests in the order they arrive

        Returns:
            dict: Contains sequence, seek_count, and avg_seek_time
        """
        sequence = [self.head_start] + self.requests
        seek_count = 0

        # Calculate total seek time
        for i in range(len(sequence) - 1):
            distance = abs(sequence[i+1] - sequence[i])
            seek_count += distance

        return {
            'sequence': sequence,
            'seek_count': seek_count,
            'avg_seek_time': seek_count / len(self.requests) if self.requests else 0
        }

    def scan(self):
        """
        SCAN (Elevator) Algorithm
        Moves in one direction to disk end, then reverses

        Returns:
            dict: Contains sequence, seek_count, and avg_seek_time
        """
        # Separate requests based on head position
        left = sorted([r for r in self.requests if r < self.head_start], reverse=True)
        right = sorted([r for r in self.requests if r >= self.head_start])

        sequence = [self.head_start]
        seek_count = 0

        if self.direction == 'right':
            # Move right to end
            if right:
                sequence.extend(right)
                seek_count += right[-1] - self.head_start

                # Go to disk end
                sequence.append(self.disk_size - 1)
                seek_count += (self.disk_size - 1) - right[-1]

                # Move left
                if left:
                    sequence.extend(left)
                    seek_count += (self.disk_size - 1) - left[-1]
            else:
                # No right requests, go to end then left
                sequence.append(self.disk_size - 1)
                seek_count += (self.disk_size - 1) - self.head_start

                if left:
                    sequence.extend(left)
                    seek_count += (self.disk_size - 1) - left[-1]
        else:
            # Move left to start
            if left:
                sequence.extend(left)
                seek_count += self.head_start - left[-1]

                # Go to disk start
                sequence.append(0)
                seek_count += left[-1]

                # Move right
                if right:
                    sequence.extend(right)
                    seek_count += right[-1]
            else:
                # No left requests, go to start then right
                sequence.append(0)
                seek_count += self.head_start

                if right:
                    sequence.extend(right)
                    seek_count += right[-1]

        return {
            'sequence': sequence,
            'seek_count': seek_count,
            'avg_seek_time': seek_count / len(self.requests) if self.requests else 0
        }

    def cscan(self):
        """
        C-SCAN (Circular SCAN) Algorithm
        Moves in one direction to end, jumps to start, continues

        Returns:
            dict: Contains sequence, seek_count, and avg_seek_time
        """
        # Separate and sort requests
        left = sorted([r for r in self.requests if r < self.head_start])
        right = sorted([r for r in self.requests if r >= self.head_start])

        sequence = [self.head_start]
        seek_count = 0

        if self.direction == 'right':
            # Service right requests
            if right:
                sequence.extend(right)
                seek_count += right[-1] - self.head_start

                # Go to disk end
                sequence.append(self.disk_size - 1)
                seek_count += (self.disk_size - 1) - right[-1]
            else:
                sequence.append(self.disk_size - 1)
                seek_count += (self.disk_size - 1) - self.head_start

            # Jump to start
            sequence.append(0)
            seek_count += self.disk_size - 1

            # Service left requests
            if left:
                sequence.extend(left)
                seek_count += left[-1]
        else:
            # Service left requests
            if left:
                sequence.extend(left)
                seek_count += self.head_start - left[0]

                # Go to disk start
                sequence.append(0)
                seek_count += left[0]
            else:
                sequence.append(0)
                seek_count += self.head_start

            # Jump to end
            sequence.append(self.disk_size - 1)
            seek_count += self.disk_size - 1

            # Service right requests
            if right:
                sequence.extend(right)
                seek_count += (self.disk_size - 1) - right[0]

        return {
            'sequence': sequence,
            'seek_count': seek_count,
            'avg_seek_time': seek_count / len(self.requests) if self.requests else 0
        }

    def look(self):
        """
        LOOK Algorithm
        Like SCAN but reverses at last request (not disk end)

        Returns:
            dict: Contains sequence, seek_count, and avg_seek_time
        """
        # Separate and sort requests
        left = sorted([r for r in self.requests if r < self.head_start], reverse=True)
        right = sorted([r for r in self.requests if r >= self.head_start])

        sequence = [self.head_start]
        seek_count = 0

        if self.direction == 'right':
            if right:
                # Move right to last request
                sequence.extend(right)
                seek_count += right[-1] - self.head_start

                # Move left
                if left:
                    sequence.extend(left)
                    seek_count += right[-1] - left[-1]
            else:
                # No right requests, just go left
                if left:
                    sequence.extend(left)
                    seek_count += self.head_start - left[-1]
        else:
            if left:
                # Move left to last request
                sequence.extend(left)
                seek_count += self.head_start - left[-1]

                # Move right
                if right:
                    sequence.extend(right)
                    seek_count += right[-1] - left[-1]
            else:
                # No left requests, just go right
                if right:
                    sequence.extend(right)
                    seek_count += right[-1] - self.head_start

        return {
            'sequence': sequence,
            'seek_count': seek_count,
            'avg_seek_time': seek_count / len(self.requests) if self.requests else 0
        }

    def clook(self):
        """
        C-LOOK Algorithm
        Like C-SCAN but jumps from last request to first (not disk ends)

        Returns:
            dict: Contains sequence, seek_count, and avg_seek_time
        """
        # Separate and sort requests
        left = sorted([r for r in self.requests if r < self.head_start])
        right = sorted([r for r in self.requests if r >= self.head_start])

        sequence = [self.head_start]
        seek_count = 0

        if self.direction == 'right':
            if right:
                # Service right requests
                sequence.extend(right)
                seek_count += right[-1] - self.head_start

                # Jump to leftmost and continue
                if left:
                    seek_count += right[-1] - left[0]
                    sequence.extend(left)
                    if len(left) > 1:
                        seek_count += left[-1] - left[0]
            else:
                # No right requests, service left
                if left:
                    sequence.extend(left)
                    if len(left) > 1:
                        seek_count += left[-1] - left[0]
        else:
            if left:
                # Service left requests
                sequence.extend(left)
                if len(left) > 1:
                    seek_count += self.head_start - left[0]
                    seek_count += left[0] - left[-1]
                else:
                    seek_count += self.head_start - left[0]

                # Jump to rightmost and continue
                if right:
                    seek_count += right[-1] - left[-1] if left else 0
                    sequence.extend(right)
                    if len(right) > 1:
                        seek_count += right[-1] - right[0]
            else:
                # No left requests, service right
                if right:
                    sequence.extend(right)
                    if len(right) > 1:
                        seek_count += right[-1] - right[0]

        return {
            'sequence': sequence,
            'seek_count': seek_count,
            'avg_seek_time': seek_count / len(self.requests) if self.requests else 0
        }

    def get_all_results(self):
        """
        Calculate results for all algorithms

        Returns:
            dict: Results for all 5 algorithms
        """
        return {
            'FCFS': self.fcfs(),
            'SCAN': self.scan(),
            'C-SCAN': self.cscan(),
            'LOOK': self.look(),
            'C-LOOK': self.clook()
        }

    def get_best_algorithm(self):
        """
        Determine the best algorithm based on seek count

        Returns:
            tuple: (algorithm_name, result_dict)
        """
        results = self.get_all_results()
        best = min(results.items(), key=lambda x: x[1]['seek_count'])
        return best