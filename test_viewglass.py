import unittest
import viewglass
import mock
import signal
import os
import logging
import pathlib
import requests

from io import StringIO
from freezegun import freeze_time
from time import sleep as ssleep

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class FakeResponse():
    def __init__(self, cloud, visibility):
        self.resp = {'sys': {'sunrise': 1526648177, 'sunset': 1526699523},
                     'visibility': 50, 'clouds': {'all': 50},
                     'main': {'temp': 64}}
        self.resp['clouds']['all'] = cloud
        self.resp['visibility'] = visibility


def kill_p(c):
    os.kill(os.getpid(), signal.SIGINT)
    return ssleep(1)


filename = "test_log.txt"


class test_intelligence(unittest.TestCase):
    """
    Test Class for Intelligence
    """

    def test_state_reset(self):
        """
        Test case to check ctrl+c signal. Asserts that SystemExit exception
        mock time.sleep by function that return signal.SIGIN
        """
        with mock.patch('time.sleep', side_effect=kill_p):
            obj = viewglass.Intelligence(filename, "95125", False)
            with self.assertRaises(SystemExit):
                obj.start()
                with self.assertRaises(ValueError):
                    obj.join()

    def test_bad_response(self):
        """
        TestCase to check bad response from the viewglass.getWeatherData
        Asserts KeyError exception
        """
        with mock.patch('sys.stdout', new=StringIO()) as fakeOutput:
            with mock.patch('viewglass.getWeatherData', return_value={'d': 1}):
                obj = viewglass.Intelligence(filename, "95125", False)
                obj.start()
                self.assertRaises(KeyError, obj.join())
                self.assertTrue('I got a KeyError - reason' in fakeOutput.getvalue().strip())

    def test_no_response(self):
        """
        TestCase to check empty response from the viewglass.getWeatherData
        Asserts KeyError exception
        """
        with mock.patch('sys.stdout', new=StringIO()) as fakeOutput:
            with mock.patch('viewglass.getWeatherData', return_value={}):
                obj = viewglass.Intelligence(filename, "95125", False)
                obj.start()
                self.assertRaises(KeyError, obj.join())
                self.assertTrue('I got a KeyError - reason' in fakeOutput.getvalue().strip())

    def test_file_assert(self):
        """
        TestCase to validate file , when 'quiet' option is False
        Asserts that file exists and have 5 lines with
        'Current time', 'Temp', 'Sunrise', 'Sunset', 'Selected Tint'
        """
        with mock.patch('time.sleep', side_effect=kill_p):
            obj = viewglass.Intelligence(filename, "95125", False)
            with self.assertRaises(SystemExit):
                obj.start()
                with self.assertRaises(ValueError):
                    obj.join()
        unit_file = pathlib.Path('.')
        self.assertTrue(unit_file.exists())
        try:
            fp = open(filename)
            expected_lines = ['Current time', 'Temp', 'Sunrise', 'Sunset', 'Selected Tint']
            for file_line, expected_line in zip(fp, expected_lines):
                self.assertTrue(expected_line in file_line)
        finally:
            fp.close()

    def test_invalid_zip_code(self):
        """
        TestCase to check invalid zipcode
        Asserts KeyError exception and stdout message
        """
        with mock.patch('sys.stdout', new=StringIO()) as fakeOutput:
            with mock.patch('viewglass.getWeatherData', return_value={}):
                obj = viewglass.Intelligence("unittest.txt", "aaa", False)
                obj.start()
                self.assertRaises(KeyError, obj.join())
                logger.debug('FAKE: ' + fakeOutput.getvalue().strip())
                self.assertTrue('I got a KeyError - reason' in fakeOutput.getvalue().strip())

    def test_quiet_true(self):
        """
        Test case to validate the file, when 'quiet' option is True
        Assert number of lines in the file after one iteretion cycle

        """
        with mock.patch('time.sleep', side_effect=kill_p):
            obj = viewglass.Intelligence(filename, "95125", True)
            with self.assertRaises(SystemExit):
                obj.start()
                with self.assertRaises(ValueError):
                    obj.join()
        unit_file = pathlib.Path('.')
        self.assertTrue(unit_file.exists())
        try:
            fp = open('unittest.txt')
            num_lines = 0
            for line in fp:
                num_lines += 1
                logger.debug("LN: %s" % line)
                self.assertTrue('Selected Tint' in line)
            self.assertNotEqual(num_lines, 0)
        finally:
            fp.close()

    @freeze_time("2012-01-01")
    def test_night_tint(self):
        """
        Test case to check that tint is always 1 in the night time
        """
        with mock.patch('time.sleep', side_effect=kill_p):
            obj = viewglass.Intelligence("unittest.txt", "10009", True)
            with self.assertRaises(SystemExit):
                obj.start()
                with self.assertRaises(ValueError):
                    obj.join()
        try:
            fp = open('unittest.txt')
            num_lines = 0
            for line in fp:
                num_lines += 1
                logger.debug("LINE: %s" % line)
                self.assertEquals('Selected Tint : 1\n', line)
            self.assertNotEqual(num_lines, 0)
        finally:
            fp.close()

    @freeze_time('2016-02-16 12:00:00')
    def test_day_tint(self):
        """
        Test case to check that tint is 2 in the day time with
        cloud > 40 or visibility < 3000
        """
        fake_response = FakeResponse(50, 2093)
        with mock.patch('viewglass.getWeatherData', return_value=fake_response.resp):
            with mock.patch('time.sleep', side_effect=kill_p):
                obj = viewglass.Intelligence(filename, "95125", True)
                with self.assertRaises(SystemExit):
                    obj.start()
                    with self.assertRaises(ValueError):
                        obj.join()
        try:
            fp = open(filename)
            num_lines = 0
            for line in fp:
                num_lines += 1
                logger.debug("LINE: %s" % line)
                self.assertEquals('Selected Tint : 2\n', line)
            self.assertNotEqual(num_lines, 0)
        finally:
            fp.close()

    def test_connection_failed(self):
        with mock.patch('viewglass.getWeatherData', side_effect=requests.exceptions.ConnectionError):
            """
            Test case to check connection issue event
            """
            with mock.patch('time.sleep', side_effect=kill_p):
                obj = viewglass.Intelligence(filename, "10009", True)
                with self.assertRaises(SystemExit):
                    obj.start()
                    with self.assertRaises(ValueError):
                        obj.join()
        try:
            fp = open(filename)
            num_lines = 0
            for line in fp:
                num_lines += 1
                logger.debug("LINE: %s" % line)
                self.assertTrue('Connection issue. Trying again ...', line)
            self.assertNotEqual(num_lines, 0)
        finally:
            fp.close()

if __name__ == "__main__":
    unittest.main()
