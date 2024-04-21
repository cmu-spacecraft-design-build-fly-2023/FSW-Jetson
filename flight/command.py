import queue
import threading
import time


# TODO use logger on DEBUG instead of print statements
class Task:
    def __init__(self, task_id, function, payload=None, priority=100):
        self.task_id = task_id
        self.function = function
        self.payload = payload
        self.priority = priority  # Lower numbers indicate higher priority
        self.created_at = time.time()
        self.attempts = 0

    def execute(self):
        """Execute the task's function with the provided payload, with retry logic."""
        self.attempts += 1
        try:
            result = self.function(self.payload)
            print(f"Task {self.task_id} completed successfully on attempt {self.attempts}.")
            return result
        except Exception as e:
            print(f"Task {self.task_id} failed on attempt {self.attempts} with error: {e}")
            if self.attempts < 3:
                print(f"Retrying task {self.task_id}...")
                return self.execute()  # Simple retry logic
            else:
                print(f"Task {self.task_id} exceeded retry limit and will not be attempted again.")
                # TODO Error message must be logged here and sent to a monitoring system / Argus
                return None
            
        

class PriorityCommandQueue:
    def __init__(self):
        self.queue = queue.PriorityQueue()
        self.paused = False
        self.lock = threading.Lock()

    def enqueue(self, task):
        """Add a task to the queue with priority."""
        with self.lock:
            if not self.paused:
                self.queue.put((task.priority, time.time(), task))
            else:
                print("Queue is paused. Task not added.")

    def dequeue(self):
        """Remove and return a task from the queue based on priority."""
        with self.lock:
            if not self.queue.empty() and not self.paused:
                _, _, task = self.queue.get()
                return task
            else:
                print("Queue is paused or empty.")
                return None

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
                print(f"Task ID: {task.task_id}, Priority: {priority}, Payload Present: {payload_present}, Timestamp: {timestamp}, ")




if __name__ == "__main__":

    import random
    def print_message(payload):
        print(payload)

        return "Message printed successfully."

    def throw_random_error(payload):
        if random.random() < 0.7:
            raise Exception("Random error occurred!")
        else:
            print("No error occurred.")

    command_queue = PriorityCommandQueue()

    task1 = Task(1, print_message, "Hello, World!", 50)
    task2 = Task(2, print_message, "Goodbye, World!", 10)
    task3 = Task(3, throw_random_error, "Testing random error", 75)

    command_queue.enqueue(task1)
    command_queue.enqueue(task2)
    command_queue.enqueue(task3)

    command_queue.print_all_tasks()

    while not command_queue.is_empty():
        task = command_queue.dequeue()
        task.execute()
        time.sleep(1)