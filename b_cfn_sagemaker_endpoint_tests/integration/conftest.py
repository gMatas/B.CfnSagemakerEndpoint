from .infra_create import inf_create
from .infra_destroy import inf_destroy


def pytest_sessionstart(session):
    inf_create()


def pytest_sessionfinish(session, exitstatus):
    inf_destroy()
