_gateway.py`
import unittest
from unittest.mock import patch, MagicMock
import json
from api_gateway import app

class TestAPIGateway(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('api_gateway.session_manager')
    @patch('api_gateway.airflow_client')
    def test_handle_simple_greeting_message(self, mock_airflow_client, mock_session_manager):
        mock_session_manager.get_session.return_value = {'state': 'idle', 'data': {}}
        response = self.app.post('/api/bot/message', 
                                 data=json.dumps({'user_id': 'test', 'message': 'hola'}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('¡Hola!', data['response'])
        mock_airflow_client.trigger_dag.assert_not_called()

    @patch('api_gateway.session_manager')
    @patch('api_gateway.airflow_client')
    def test_trigger_dag_for_complex_message(self, mock_airflow_client, mock_session_manager):
        mock_session_manager.get_session.return_value = {'state': 'idle', 'data': {}}
        response = self.app.post('/api/bot/message', 
                                 data=json.dumps({'user_id': 'test', 'message': 'reportar una falla'}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('Iniciando el proceso', data['response'])
        mock_airflow_client.trigger_dag.assert_called_once()

    def test_handle_webhook(self):
        response = self.app.post('/api/bot/webhook', 
                                 data=json.dumps({'user_id': 'test', 'message': 'Respuesta del DAG'}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'ok')

if __name__ == '__main__':
    unittest.main()

