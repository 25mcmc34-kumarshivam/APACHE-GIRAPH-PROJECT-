#!/usr/bin/env python3
"""Convert Giraph's internal numeric values to vertex<TAB>B/NB<TAB>round.

Positive integer value = first burn round. Zero or a negative value = the
vertex was never burned during the configured rounds, so output NB and -1.
This script reads raw Giraph output from stdin and writes human output to
stdout; the runner stores that stream in a new HDFS output file.
"""

from decimal import Decimal, InvalidOperation
import sys


def format_line(raw):
    """Format one Giraph IdWithValueTextOutputFormat record."""
    fields = raw.strip().split()
    if len(fields) != 2:
        raise ValueError("expected vertex ID and numeric value: {!r}".format(raw.strip()))
    vertex = int(fields[0])
    try:
        value = Decimal(fields[1])
    except InvalidOperation as error:
        raise ValueError("invalid burn value for vertex {}".format(vertex)) from error
    if not value.is_finite():
        raise ValueError("non-finite burn value for vertex {}".format(vertex))
    if value <= 0:
        return "{}\tNB\t-1".format(vertex)
    if value != value.to_integral_value():
        raise ValueError("non-integer burn round for vertex {}".format(vertex))
    return "{}\tB\t{}".format(vertex, int(value))


def main():
    for line_number, raw in enumerate(sys.stdin, 1):
        try:
            print(format_line(raw))
        except ValueError as error:
            sys.exit("ERROR on input line {}: {}".format(line_number, error))


if __name__ == "__main__":
    main()
