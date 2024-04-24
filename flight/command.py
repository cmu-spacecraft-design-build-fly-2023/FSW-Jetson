"""
Payload Command Queue

Description: Contains the CommandQueue class that manages the queue of tasks to be executed by the Payload. 

Author: Ibrahima S. Sow
Date: [Creation or Last Update Date]
"""

import queue
import threading
import time
from flight import Logger


# TODO use logger on DEBUG instead of print statements
class Task:
    def __init__(self, payload, task_id, function, data=None, priority=100):
        self.task_id = task_id
        self.function = function
        self.data = data
        self.priority = priority  # Lower numbers indicate higher priority
        self.created_at = time.time()
        self.attempts = 0
        self.payload = payload

    def execute(self):
        """Execute the task's function with the provided data, with retry logic."""
        self.attempts += 1
        try:
            result = self.function(self.payload) # for now ignore the data argument :: , self.data
            Logger.log("INFO", f"Task {self.task_id} completed successfully on attempt {self.attempts}.")
            return result
        except Exception as e:
            Logger.log("ERROR", f"Task {self.task_id} failed on attempt {self.attempts} with error: {e}")
            if self.attempts < 3:
                Logger.log("INFO", f"Retrying task {self.task_id}...")
                return self.execute()  # Simple retry logic
            else:
                Logger.log("INFO", f"Task {self.task_id} exceeded retry limit and will not be attempted again.")
                # TODO Error message must be logged here and sent to a monitoring system / Argus
                return None


class CommandQueue:
    def __init__(self):
        self._queue = queue.PriorityQueue()
        self.paused = False
        self.lock = threading.Lock()

    @property
    def queue(self):
        return self._queue

    def add_task(self, task):
        """Add a task to the queue with priority."""
        with self.lock:
            if not self.paused:
                self.queue.put((task.priority, time.time(), task))
            else:
                Logger.log("INFO", "Queue is paused. Task not added.")

    def get_next_task(self):
        """Remove and return a task from the queue based on priority."""
        with self.lock:
            if self.paused:
                # print("Queue is paused.")
                return None
            elif self.queue.empty():
                # print("Queue is empty.")
                return None
            else:
                _, _, task = self.queue.get()
                return task

    def pause(self):
        """Pause the queue operations."""
        self.paused = True

    def resume(self):
        """Resume the queue operations."""
        self.paused = False

    def is_empty(self):
        return self.queue.empty()

    def size(self):
        return self.queue.qsize()

    def clear(self):
        with self.lock:
            self.queue.queue.clear()

    def print_all_tasks(self):
        """Print all tasks in the queue in order."""
        with self.lock:
            tasks = list(self.queue.queue)
            tasks.sort()  # Sort primarily by priority, secondarily by timestamp
            for priority, timestamp, task in tasks:
                payload_present = "Yes" if task.payload else "No"
                Logger.log("INFO", f"Task ID: {task.task_id}, Priority: {priority},  Timestamp: {timestamp}, Payload Present: {payload_present}")


class TX_Queue:
    def __init__(self):
        self._queue = queue.Queue()
        self.lock = threading.Lock()

    @property
    def queue(self):
        return self._queue

    def add_msg(self, msg):
        with self.lock:
            self.queue.put(msg)

    def is_empty(self):
        return self.queue.empty()

    def size(self):
        return self.queue.qsize()

    def clear(self):
        with self.lock:
            self.queue.queue.clear()


