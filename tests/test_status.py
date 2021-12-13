import asyncio
import pytest
from zeroscale.status import Status

def test_status_printing():
    assert Status.running.__repr__() == "<Status.running>"
