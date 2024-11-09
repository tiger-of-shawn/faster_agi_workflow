
import inspect
import threading
import time


class BaseGraphNode:
    def __init__(self, name : str = '', **kwargs):
        self.name = name
        self.kwargs = kwargs
        self.output_callbacks = []
        self.input_data = []
        self.input_keys = []
        self.output_keys = []
        self.data_lock = threading.Lock()
        self.data_semaphore = threading.Semaphore(0)  # Initial value of 0
        self.thread = threading.Thread(target=self.process_data)
        self.running = False

    def process_data(self):
        while self.running:
            self.data_semaphore.acquire()  # Decrement the semaphore, wait for new data
            with self.data_lock:
                if self.input_data:
                    data = self.input_data.pop(0)
                    print(f"Processing: {data}")
                    for callback in self.output_callbacks:
                        callback(key = 'output', value = data)
                else:
                    # This should not happen because we only acquire when there's data
                    print("Unexpected state: semaphore acquired but no data")

    @staticmethod
    def callback_prototype(key: str, value: any) -> None:
        pass
    def get_input_keys(self) -> list:
        return self.input_keys

    def get_output_keys(self) -> list:
        return self.output_keys
    
    def set_input(self, **kwargs) -> bool:
        with self.data_lock:
            data_to_add = {}
            for key, value in kwargs.items():
                if key in self.input_keys:
                    data_to_add[key] = value
            if set(data_to_add.keys()) == set(self.input_keys):
                self.input_data.append(data_to_add)
                self.data_semaphore.release()  # Increment the semaphore, signaling new data
                return True
            else:
                print(f'got: {set(data_to_add.keys())}')
                print(f'expected: {set(self.input_keys)}')
                print(f"Missing inputs: {self.input_keys - data_to_add.keys()}")
                return False 

    def register_output_callback(self, callback) -> bool:
        if callable(callback) and callback not in self.output_callbacks:
            callback_signature = inspect.signature(callback)
            prototype_signature = inspect.signature(self.callback_prototype)

            if callback_signature == prototype_signature:
                self.output_callbacks.append(callback)
                print(f"Callback {callback.__name__} registered.")
            else:
                print(f"Callback {callback.__name__} does not match the prototype: {self.callback_prototype.__name__}")
        else:
            print("Invalid or duplicate callback.")
    def run(self) -> bool:
        if not self.running:
            self.running = True
            self.thread.start()
            print("Thread started.")
            return True
        return False
    def stop(self) -> bool:
        if self.running:
            self.running = False
            # Ensure the thread exits by releasing the semaphore enough times
            self.data_semaphore.release()
            self.thread.join()
            print("Thread stopped.")
            return True
        return True
