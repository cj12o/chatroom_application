from concurrent.futures import ThreadPoolExecutor
from .views.logger import logger
import atexit

class ThreadPoolManager:
    "class that manages global threadpool executor"
    executor = None

    @classmethod
    def get(cls):
        "return an instance of thread pool executor"

        if cls.executor is None:
            cls.executor = ThreadPoolExecutor(max_workers=4)
        logger.info("ThreadPoolManager called")
        return cls.executor
    
    @classmethod
    def shutdown(cls):
        "cleans up thread pool executor ,resource gets free"
        if cls.executor is None: return
        cls.executor.shutdown(wait=True)
        logger.info("ThreadPoolManager shutdown")

@atexit.register
def cleanPool():
    ThreadPoolManager.shutdown()