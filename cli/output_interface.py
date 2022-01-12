import itertools
import os
import threading
import time

UP = "\x1B[1A"
CLR = "\x1B[0K"
NEWLINE = "\n"
CLR_N = f"{CLR}{NEWLINE}"


class Message:
    def __init__(self, message=None):
        self._message = message
    
    def show(self, message):
        message = message.strip()
        l = self.message_length
        print(f"{UP * l}{CLR_N * l}{UP * l}{message.replace(NEWLINE, CLR_N)}{CLR_N}", end="")
        self._message = message
        
    @property
    def message_length(self):
        width = os.get_terminal_size().columns
        length = sum([
            ((len(line) - 1) // width) + 1 for line in self._message.split("\n")
            ]) if self._message else 0
        return length
        
    @property
    def message(self):
        return self._message
    
    @message.setter
    def message(self, message):
        self.show(message)

    def __enter__(self):
        message = self._message
        self._message = None
        self.message = message
        return self
    
    def __exit__(self, *_):
        l = self.message_length
        print(UP * l + CLR_N * l + UP * l, end="")


class Spinner(Message):
    def __init__(self, message):
        super().__init__(message)
        self.quit = False
        self.tail = None
        
    def __enter__(self):
        threading.Thread(target=self.update).start()
        return super().__enter__()
        
    def show(self, message):
        super().show(message)
        self.tail = self.message.split("\n")[-1]
        
    def update(self):
        signs = itertools.cycle('/-\|')
        for sign in signs:
            if self.quit:
                break
            
            if self.tail:
                print(f'{UP}{self.tail}.. {sign}{CLR_N}', end="")
            time.sleep(0.08)
            
    def __exit__(self, *_):
        self.quit = True
        super().__exit__(*_)
        
