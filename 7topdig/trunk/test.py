from tests import suite
import unittest

ts = suite()
unittest.TextTestRunner(verbosity=2).run(ts)