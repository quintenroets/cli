class ErrorHandler():
    error = False

    def __init__(self, obj=None, exit=True):
        self.obj = obj
        self.exit = exit
    
    def __enter__(self):
        pass

    def __exit__(self, type, value, tb):
        if tb:
            if type != KeyboardInterrupt and not ErrorHandler.error:
                error = self.show_error(exit=self.exit)
            if self.obj is not None:
                self.obj.crashed = error
        
        return True

    @staticmethod
    def show_error(message=None, exit=True):
        # most of the time no error => save time by only importing on error
        
        import cli
        import os
        import traceback
        from plib import Path
        
        ErrorHandler.error = True
        path = Path.assets / '.error.txt'
        path.text = message or traceback.format_exc()
        
        notify_process = cli.start(f'cat {path}; read', console=True)

        if exit:
            # make sure notify process has started before terminating original process
            notify_process.communicate()
            os._exit(0)

        return path.text
