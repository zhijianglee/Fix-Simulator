import unittest
from unittest.mock import patch

from apiservice import app


class TestApiService(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch('apiservice.databaseconnector.getResultFromDB')
    def test_retrieve_orders_by_client_comp_id(self, mock_get_result):
        # Mock the database result for the OMS_OCBC_01 client comp ID
        mock_get_result.return_value = (
            [
                {
                    'CLIENT_COMP_ID': 'OMS_OCBC_01',
                    'ORDER_ID': '12345',
                    'SENDER_COMP_ID': 'LZJSIM',
                    'ORDER_QTY': '1000'
                }
            ],
            200,
        )

        response = self.client.get('/retrieve_orders_by_client_comp_id/OMS_OCBC_01')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [
            {
                'CLIENT_COMP_ID': 'OMS_OCBC_01',
                'ORDER_ID': '12345',
                'SENDER_COMP_ID': 'LZJSIM',
                'ORDER_QTY': '1000'
            }
        ])
        mock_get_result.assert_called_once()
        expected_query = "SELECT * FROM SIMULATOR_RECORDS WHERE CLIENT_COMP_ID = 'OMS_OCBC_01'"
        mock_get_result.assert_called_with(expected_query)


if __name__ == '__main__':
    unittest.main()
