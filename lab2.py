import decimal as dec


class Symbolfr:
    def __init__(self, symbol, frequency):
        self.symbol = symbol
        self.frequency = frequency


class Symbolbr:
    def __init__(self, symbol, low_board, high_board):
        self.symbol = symbol
        self.low_board = low_board
        self.high_board = high_board


def _get_frequency(element):
    return element.frequency


def get_symbols_boards(symbols_dict, symbol):
    for sym in symbols_dict:
        if sym.symbol == symbol:
            return sym.low_board, sym.high_board


def get_symbols_frequency(user_string, precision=250):
    if precision <= 0:
        raise ValueError("Precision of encoding can not be less than zero")
    if len(user_string) == 0:
        raise ValueError("Received empty string")

    symbols_array = []
    for ch in list(user_string):
        symbols_array.append(ch)

    symbols_array.sort()
    symbols_frequency = []
    count = dec.Decimal(0)

    for ch_i in list(symbols_array):
        for ch_g in list(symbols_array):
            if ch_i == ch_g:
                count += dec.Decimal(1)
        is_exist = False
        for sym in symbols_frequency:
            if sym.symbol == ch_i:
                is_exist = True
        if not is_exist:
            symbols_frequency.append(Symbolfr(ch_i, count))
        count = dec.Decimal(0)
    symbols_frequency.sort(key=_get_frequency, reverse=True)
    dec.getcontext().prec = precision
    return symbols_frequency


def get_symbols_intervals(user_string, precision=250):
    if precision <= 0:
        raise ValueError("Precision of encoding can not be less than zero")
    vector_length = dec.Decimal(0)
    symbols_frequency = get_symbols_frequency(user_string, precision)
    for sym in symbols_frequency:
        if sym.frequency <= 0:
            raise ValueError("Frequency of symbol less than zero")
        vector_length += sym.frequency
    symbols_intervals = []
    length = dec.Decimal(0)
    for element in symbols_frequency:
        low_board = length
        high_board = low_board + element.frequency / vector_length
        length += element.frequency / vector_length
        symbols_intervals.append(Symbolbr(element.symbol, low_board, high_board))
    return symbols_intervals


def encode(user_string, precision=250):
    if precision <= 0:
        raise ValueError("Precision of encoding can not be less than zero")
    if len(user_string) == 0:
        raise ValueError("Received empty string")
    dec.getcontext().rounding = dec.ROUND_UP
    vector_length = dec.Decimal(0)
    symbols_frequency = get_symbols_frequency(user_string, precision)
    for sym in symbols_frequency:
        vector_length += sym.frequency
    symbols_intervals = get_symbols_intervals(user_string, precision)
    low_old = dec.Decimal(0)
    low_board = dec.Decimal(0)
    high_old = dec.Decimal(1)
    high_board = dec.Decimal(1)
    for ch in list(user_string):
        low, high = get_symbols_boards(symbols_intervals, ch)
        high_board = low_old + (high_old - low_old) * high
        low_board = low_old + (high_old - low_old) * low
        high_old = high_board
        low_old = low_board
    dec.getcontext().prec = precision
    return low_board, high_board


def decode(symbols_frequency, code, precision_of_string=10):
    if precision_of_string <= 0:
        raise ValueError("Precision of string can not be less than zero")
    if code < 0 or code >= 1:
        raise ValueError("Incorrect code")
    vector_length = dec.Decimal(0)
    user_string = ""
    for sym in symbols_frequency:
        vector_length += sym.frequency
        count = int(sym.frequency)
        while count > 0:
            user_string += sym.symbol
            count -= 1
    dec.getcontext().rounding = dec.ROUND_UP
    symbols_intervals = get_symbols_intervals(user_string)
    first_char = ""
    for sym in symbols_frequency:
        low, high = get_symbols_boards(symbols_intervals, sym.symbol)
        if low <= code <= high:
            first_char = sym.symbol
    user_string = [first_char]
    for i in range(0, precision_of_string - 1):
        low, high = get_symbols_boards(symbols_intervals, user_string[i])
        code = (code - low) / (high - low)
        for sym in symbols_frequency:
            low, high = get_symbols_boards(symbols_intervals, sym.symbol)
            if low < code <= high:
                user_string.append(sym.symbol)
    result_string = ""
    for ch in user_string:
        result_string += ch
    return result_string
