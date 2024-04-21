import queue
import threading
import time

class Task:
    def __init__(self, task_id, function, payload=None, priority=100):
        self.task_id = task_id
        self.function = function
        self.payload = payload
        self.priority = priority  # Lower numbers indicate higher priority
        # self.timestamp = time.time()

    def execute(self):
        """Execute the task's function with the provided payload."""
        try:
            result = self.function(self.payload)
            print(f"Task {self.task_id} completed successfully.")
            return result
        except Exception as e:
            print(f"Task {self.task_id} failed with error: {e}")
            # Optionally, re-enqueue or log the task error for further action

class PriorityCommandQueue:
    def __init__(self):
        self.queue = queue.PriorityQueue()

    def enqueue(self, task):
        """Add a task to the queue with priority."""
        self.queue.put((task.priority, task))

    def dequeue(self):
        """Remove and return a task from the queue based on priority."""
        _, task = self.queue.get()
        return task

    def is_empty(self):
        return self.queue.empty()
    
    def size(self):
        return self.queue.qsize()
    
    def clear(self):
        self.queue.queue.clear()

    def print_all_tasks(self):
        """Print all tasks in the queue in order."""
        tasks = list(self.queue.queue)
        tasks.sort(key=lambda x: x[0])  # Sort tasks based on priority
        for _, task in tasks:
            payload = True if task.payload else False
            print(f"Task ID: {task.task_id}, Priority: {task.priority}, Payload: {payload}")


if __name__ == "__main__":
    def print_message(payload):
        print(payload)
        return "Message printed successfully."

    command_queue = PriorityCommandQueue()

    task1 = Task(1, print_message, "Hello, World!", 50)
    task2 = Task(2, print_message, "Goodbye, World!", 10)

    command_queue.enqueue(task1)
    command_queue.enqueue(task2)

    command_queue.print_all_tasks()

    while not command_queue.queue.empty():
        task = command_queue.dequeue()
        task.execute()
        time.sleep(1)