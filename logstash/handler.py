import math
from logging.handlers import SocketHandler
from logstash import formatter

def split_string(s, chunk_size, encoding='utf-8'):
    """Split long strings into chunks."""
    s_bytes = s.encode(encoding)

    strings = []
    if len(s_bytes) <= chunk_size:
        strings.append(s)

    else:
        # Since strings will have extra characters added at the start and end
        # ('middle of string' becomes '…middle of string… (2/3)'), the real
        # chunk size is a little less than chunk_size.
        approx_num_strings = math.ceil(len(s_bytes) / (chunk_size - 20))
        dummy_extra_data = '…… ({n}/{n})'.format(n=approx_num_strings)
        dummy_extra_data_bytes = dummy_extra_data.encode(encoding)
        chunk_size = chunk_size - len(dummy_extra_data_bytes)

        # Build a list of strings.
        remaining_string = s
        while remaining_string:
            # Get a string of chunk_size characters.
            characters_trimmed = 0
            string = remaining_string[:chunk_size]
            string_bytes = string.encode(encoding)

            # If this string is too large, remove characters until it's not.
            while len(string_bytes) > chunk_size:
                characters_trimmed = characters_trimmed + 1
                string_size = chunk_size - characters_trimmed
                string = remaining_string[:string_size]
                string_bytes = string.encode(encoding)

            # Add this string to the list, and remove it from the remaining
            # string.
            strings.append(string)
            remaining_string = remaining_string[len(string):]

        # Decorate the strings.
        for i, string in enumerate(strings):
            # If not the first string, prefix with an ellipsis.
            if i != 0:
                string = '…' + string

            # If not the last string, suffix with an ellipsis.
            if i != len(strings) - 1:
                string = string + '…'

            # Suffix with an indication of which chunk this is (e.g. '(7/14)').
            strings[i] = string + ' ({}/{})'.format(i + 1, len(strings))

    return strings



# Derive from object to force a new-style class and thus allow super() to work
# on Python 2.6
class BaseLogstashHandler(SocketHandler, object):
    """Python logging handler for Logstash."""

    def __init__(self, host, port, max_message_size=math.inf):
        self.max_message_size = max_message_size
        super(BaseLogstashHandler, self).__init__(host, port)

    def makePickle(self, record):
        """Pickle the record in chunks."""
        for msg in split_string(record.msg, chunk_size=self.max_message_size):
            record.msg = msg
            yield self.makeChunkedPickle(record)

    def makeChunkedPickle(self, record):
        return super(BaseLogstashHandler, self).makePickle(record)

    def send(self, strings):
        """Send pickled chunks."""
        for s in strings:
            super().send(s)
