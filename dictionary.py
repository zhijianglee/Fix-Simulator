from enum import Enum


# Taken from https://www.onixs.biz/fix-dictionary/4.2/tagNum_29.html
class LastCapacity(Enum):
    Agent = 1
    Cross_As_Agent = 2
    Cross_As_Principal = 3
    Principal = 4


# Taken form https://www.onixs.biz/fix-dictionary/4.2/tagNum_40.html
class OrderType(Enum):
    Market = 1
    Limit = 2
    Stop = 3
    StopLimit = 4


# Taken from https://www.onixs.biz/fix-dictionary/4.2/tagNum_22.html
class IDSource(Enum):
    ISIN = 4
    RIC = 5
    EXCHANGE_SYMBOL = 8


# Taken from https://www.onixs.biz/fix-dictionary/4.2/tagNum_20.html
class ExecTransType(Enum):
    New = 0
    Cancel = 1
    Correct = 2
    Status = 3


# Taken from https://www.onixs.biz/fix-dictionary/4.2/tagNum_150.html
class ExecType(Enum):
    New = 0
    Partially_Filled = 1
    Filled = 2
    Done_For_Day = 3
    Canceled = 4
    Replaced = 5
    Pending_Cancel = 6
    Stopped = 7
    Rejected = 8
    Suspended = 9
    Pending_New = 'A'
    Calculated = 'B'
    Expired = 'C'
    Restated = 'D'
    Pending_Replace = 'E'


# Taken from https://www.onixs.biz/fix-dictionary/4.2/tagNum_39.html
class OrdStatus(Enum):
    New = 0
    Partially_Filled = 1
    Filled = 2
    Done_For_Day = 3
    Canceled = 4
    Replaced = 5
    Pending_Cancel = 6
    Stopped = 7
    Rejected = 8
    Suspended = 9
    Pending_New = 'A'
    Calculated = 'B'
    Expired = 'C'
    Accepted_For_Bidding = 'D'
    Pending_Replace = 'E'


# Taken from https://www.onixs.biz/fix-dictionary/4.2/tagNum_35.html
class MsgType(Enum):
    Heartbeat = 0
    Resend_Request = 2
    Test_Request = 1
    Reject = 3
    Sequence_Reset = 4
    Logout = 5
    Indication_of_Interest = 6
    Execution_Report = 8
    Order_Cancel_Reject = 9
    Logon = 'A'
    Single_Order = 'D'
    Order_Cancel_Request = 'F'
    Order_Cancel_or_Replace_Request = 'G'
