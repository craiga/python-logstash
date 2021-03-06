from logstash.handlers import BaseLogstashHandler


class UDPLogstashHandler(BaseLogstashHandler):
    """Python logging handler for Logstash. Sends events over UDP.
    :param host: The host of the logstash server.
    :param port: The port of the logstash server (default 5959).
    :param message_type: The type of the message (default logstash).
    :param fqdn; Indicates whether to show fully qualified domain name or not (default False).
    :param version: version of logstash event schema (default is 0).
    :param tags: list of tags for a logger (default is None).
    """

    def makeChunkedPickle(self, record):
        return self.formatter.format(record)


# For backward compatibility
LogstashHandler = UDPLogstashHandler

