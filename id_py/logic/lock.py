import os
from io import TextIOWrapper
from .commissionnumber import CommissionNumber

class LockDetector:

    def __init__(self):
        self.lock_file_path = os.getenv('LOCK_CONFIG')

    def detect_lock(self, commission_number: CommissionNumber):
        if self.lock_file_path == None:
            return None
        with open(str(self.lock_file_path)) as file:
            entries = file.readlines()
            for entry in entries:
                split = entry.split(';')
                commission_number_locked = split[0]
                message = split[1]
                if commission_number.number.lower() == commission_number_locked.lower():
                    return Lock(commission_number, message)
        return None


class Lock:
    def __init__(self, commission_number: str, message: str):
        self.commission_number = commission_number
        self.message = message
