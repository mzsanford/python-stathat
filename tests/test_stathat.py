
import unittest

import mock
import requests
import requests_mock
import stathat


@requests_mock.Mocker()
class TestStatHatBase(unittest.TestCase):
    @unittest.skipIf(not stathat.HAS_GEVENT, "Must have gevent to test async")
    def test_send_async(self, rmock):
        path = '/ez'
        data = {'count': 1}
        instance = stathat._StatHatBase()

        mock_group = mock.Mock()
        stathat.async_group = mock_group

        rmock.post(stathat.STATHAT_ENDPOINT + path, text='{}')
        instance._send(path, data, True)
        mock_group.spawn.assert_called_with(instance._send_inner,
                                            stathat.STATHAT_ENDPOINT + path,
                                            data,
                                            silent=True)

    def test_send_sync(self, rmock):
        path = '/ez'
        data = {'count': 1}
        instance = stathat._StatHatBase()
        rmock.post(stathat.STATHAT_ENDPOINT + path, text='{}')
        instance._send(path, data, False)
        self.assertTrue(rmock.called, "Should have made an HTTP request")

    def test_send_sync_io_error(self, rmock):
        path = '/ez'
        data = {'count': 1}
        instance = stathat._StatHatBase()

        def cb(req, ctx):
            raise requests.ConnectionError("error connecting")

        rmock.post(stathat.STATHAT_ENDPOINT + path, text=cb)
        with self.assertRaises(stathat.StatHatError):
            instance._send(path, data, False)
        self.assertTrue(rmock.called, "Should have made an HTTP request")

    def test_send_sync_empty_reply(self, rmock):
        path = '/ez'
        data = {'count': 1}
        instance = stathat._StatHatBase()
        rmock.post(stathat.STATHAT_ENDPOINT + path, text='')
        with self.assertRaises(stathat.StatHatError):
            instance._send(path, data, False)
        self.assertTrue(rmock.called, "Should have made an HTTP request")

    def test_send_sync_error_reply(self, rmock):
        path = '/ez'
        data = {'count': 1}
        instance = stathat._StatHatBase()
        rmock.post(stathat.STATHAT_ENDPOINT + path, text='{"status":500,"msg":"example error"}')
        with self.assertRaises(stathat.StatHatError):
            instance._send(path, data, False)
        self.assertTrue(rmock.called, "Should have made an HTTP request")
