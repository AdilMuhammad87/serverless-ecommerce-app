import unittest
from unittest.mock import patch, MagicMock
import src.products.lambda_function as lambda_function

class TestLambdaFunction(unittest.TestCase):

    @patch('lambda_function.dynamodb')
    def test_get_item_success(self, mock_dynamodb):
        # Mock DynamoDB response
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.get_item.return_value = {
            'Item': {
                'productId': '123',
                'name': 'Test Product',
                'price': 10.99
            }
        }

        # Create a mock event
        event = {
            'pathParameters': {
                'productId': '123'
            }
        }

        # Call the handler
        response = lambda_function.lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 200)
        self.assertIn('body', response)
        self.assertIn('Test Product', response['body'])

    @patch('lambda_function.dynamodb')
    def test_get_item_not_found(self, mock_dynamodb):
        # Mock DynamoDB response for item not found
        mock_table = MagicMock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.get_item.return_value = {}

        # Create a mock event
        event = {
            'pathParameters': {
                'productId': '999'
            }
        }

        # Call the handler
        response = lambda_function.lambda_handler(event, None)

        # Assertions
        self.assertEqual(response['statusCode'], 404)
        self.assertIn('body', response)
        self.assertIn('Product not found', response['body'])

if __name__ == '__main__':
    unittest.main()
