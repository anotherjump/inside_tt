import pytest


def pytest_addoption(parser):
    parser.addoption('-U', action='store', default=1, help='number of fake users to add')
    parser.addoption('-M', action='store', default=1, help='number of messages per user to post')
    parser.addoption('-C', action='store_true',  help='clean users and messages after test')
