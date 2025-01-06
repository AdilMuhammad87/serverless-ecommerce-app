import json
import boto3
import logging
from decimal import Decimal

# Initialize DynamoDB and Logging
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Products')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def decimal_default(obj):
    """Helper function to convert Decimal types to float for JSON serialization."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        http_method = event.get('httpMethod')
        query_params = event.get('queryStringParameters')
        body = event.get('body')

        if http_method == 'GET' and query_params and 'productId' in query_params:
            return read_product(query_params['productId'])
        elif http_method == 'POST' and body:
            return update_product(body)
        elif http_method == 'DELETE' and query_params and 'productId' in query_params:
            return delete_product(query_params['productId'])
        else:
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Unsupported HTTP method or missing parameters'}, default=decimal_default)
            }
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return {
            'statusCode': 200,
            'body': json.dumps({'error': str(e)}, default=decimal_default)
        }

def read_product(product_id):
    try:
        response = table.get_item(Key={'productId': product_id})
        if 'Item' in response:
            return {
                'statusCode': 200,
                'body': json.dumps(response['Item'], default=decimal_default)
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Product not found'}, default=decimal_default)
            }
    except Exception as e:
        logger.error(f"Error reading product: {str(e)}")
        return {
            'statusCode': 200,
            'body': json.dumps({'error': f"Error reading product: {str(e)}"}, default=decimal_default)
        }

def update_product(body):
    try:
        data = json.loads(body, parse_float=Decimal)
        product_id = data.get('productId')
        update_key = data.get('updateKey')
        update_value = data.get('updateValue')

        if not product_id or not update_key or update_value is None:
            return {
                'statusCode': 200,
                'body': json.dumps({'error': 'Missing required fields in payload'}, default=decimal_default)
            }

        response = table.update_item(
            Key={'productId': product_id},
            UpdateExpression=f"SET #attrName = :val",
            ExpressionAttributeNames={'#attrName': update_key},
            ExpressionAttributeValues={':val': update_value},
            ReturnValues="UPDATED_NEW"
        )

        updated_attributes = {k: float(v) if isinstance(v, Decimal) else v for k, v in response.get('Attributes', {}).items()}

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Product updated successfully',
                'updatedAttributes': updated_attributes
            }, default=decimal_default)
        }
    except json.JSONDecodeError:
        return {
            'statusCode': 200,
            'body': json.dumps({'error': 'Invalid JSON in request body'}, default=decimal_default)
        }
    except Exception as e:
        logger.error(f"Error updating product: {str(e)}")
        return {
            'statusCode': 200,
            'body': json.dumps({'error': f"Error updating product: {str(e)}"}, default=decimal_default)
        }

def delete_product(product_id):
    try:
        response = table.delete_item(
            Key={'productId': product_id},
            ReturnValues='ALL_OLD'  # To check if the item existed before deletion
        )
        if 'Attributes' in response:
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Product deleted successfully'}, default=decimal_default)
            }
        else:
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'Product not found'}, default=decimal_default)
            }
    except Exception as e:
        logger.error(f"Error deleting product: {str(e)}")
        return {
            'statusCode': 200,
            'body': json.dumps({'error': f"Error deleting product: {str(e)}"}, default=decimal_default)
        }
