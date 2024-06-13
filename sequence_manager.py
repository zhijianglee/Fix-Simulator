class SequenceManager:
    _instance = None
    _sequence_number = 1

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SequenceManager, cls).__new__(cls)
        return cls._instance

    def reset_sequence_number(self):
        self._sequence_number = 1

    def set_sequence_number(self, num):
        self._sequence_number = num

    def get_sequence_number(self):
        return self._sequence_number

    def increment_sequence_number(self):
        self._sequence_number += 1
