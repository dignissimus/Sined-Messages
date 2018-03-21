from enum import Enum, auto

TONES = [440, 880, 1320, 1760, 2200, 2640, 3080, 3520, 4000, 4440] # The tones to use to communicate

# [1320, 3038, 3798] # (Binary)
# [880, 1320, 1760, 2200, 2640, 3080, 3520, 3960, 4400, 4840, 5280, 5720, 6160, 6600, 7040, 7480, 7920, 8360] (Base 16)
# [1320, 2200, 3080, 3960, 4840, 5720, 6600, 7480, 8360]
# [880, 1760, 2640, 3520, 4400, 5280, 6160, 7040, 7920]
# [440, 880, 1320, 1760, 2200, 2640, 3080, 2520, 3960]
# [1360, 2240, 3120] # [1360, 1800, 2240, 2680, 3120]
# [440, 880, 1320, 1760, 2200, 2640, 3080, 3520, 4000, 4440]
# [1360, 1800, 2240, 2680, 3120]
# [440, 880, 1320, 1760]
BOUND = 210  # 110  # reasonable space for errors, 220 could work too
LENGTH = .1 # Sets the time to play the tone
CHUNK_SIZE = 4096 # The chunk size
BOX_LENGTH = 3 # THe length of a block

MIN_VALUE = 0 # Smallest value to be sent
MAX_VALUE = 7 # The largest to be sent
SEPARATOR = 8 # The separator char
BASE = 8 # The base to be working in

USE_SEPARATOR = True # Whether or not separating


class ReturnCode(Enum):
    EXIT = auto()
