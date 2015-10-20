#! /usr/bin/python3

from psycopg2 import connect as pgconnect
import psycopg2.extras


def connect(connection_string):
    """Returns a psycopg2 connection"""
    connection = pgconnect(connection_string)
    return connection


def getDictCursor(connection):
    """Returns a psycopg2 DictCursor"""
    cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return cursor
