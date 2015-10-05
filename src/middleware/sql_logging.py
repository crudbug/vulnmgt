from django.db import connection
from sys import stdout


class SQLLogging:
    def process_response(self, request, response):
        if stdout.isatty():
            for query in connection.queries:
                print "\033[1;31m[%s]\033[0m \033[1m%s\033[0m" % (query['time'], " ".join(query['sql'].split()))
        return response
