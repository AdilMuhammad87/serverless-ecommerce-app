import json
import boto3
import os
import logging
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
cart_table = dynamodb.Table('ShoppingCart')  # Or read from env: os.environ.get('CART_TABLE')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Received event: %s", event)
    
    http_method = event.get('httpMethod')
    query_params = event.get('queryStringParameters') or {}
    body = event.get('body')
    
    if http_method == 'GET' and 'userId' in query_params:
        return get_cart(query_params['userId'])
    elif http_method == 'POST' and body:
        return add_to_cart(body)
    elif http_method == 'DELETE' and query_params.get('userId') and query_params.get('itemId'):
        return remove_from_cart(query_params['userId'], query_params['itemId'])
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({"message": "Invalid request"})
        }

def decimal_default(o):
    if isinstance(o, Decimal):
        return float(o)
    raise TypeError

def get_cart(user_id):
    try:
        # Query all items for a user
        response = cart_table.query(
            KeyConditionExpression="userId = :uid",
            ExpressionAttributeValues={":uid": user_id}
        )
        items = response.get('Items', [])
        return {
            'statusCode': 200,
            'body': json.dumps(items, default=decimal_default)
        }
    except Exception as e:
        logger.error("Error getting cart: %s", e)
        return {'statusCode': 500, 'body': json.dumps({"error": str(e)})}

def add_to_cart(body):
    try:
        data = json.loads(body, parse_float=Decimal)
        user_id = data['userId']
        item_id = data['itemId']
        quantity = data.get('quantity', 1)
        
        cart_table.put_item(
            Item={
                'userId': user_id,
                'itemId': item_id,
                'quantity': quantity
            }
        )
        return {
            'statusCode': 200,
            'body': json.dumps({"message": "Item added to cart"})
        }
    except Exception as e:
        logger.error("Error adding to cart: %s", e)
        return {'statusCode': 500, 'body': json.dumps({"error": str(e)})}

def remove_from_cart(user_id, item_id):
    try:
        response = cart_table.delete_item(
            Key={'userId': user_id, 'itemId': item_id},
            ReturnValues='ALL_OLD'
        )
        if 'Attributes' in response:
            return {
                'statusCode': 200,
                'body': json.dumps({"message": "Item removed"})
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({"message": "Item not found"})
            }
    except Exception as e:
        logger.error("Error removing item: %s", e)
        return {'statusCode': 500, 'body': json.dumps({"error": str(e)})}
