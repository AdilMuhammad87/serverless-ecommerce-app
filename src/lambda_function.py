import json
import boto3
import logging

# Initialize DynamoDB and Logging
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Products')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    try:
        logger.info(f"Received event: {json.dumps(event)}")

        if event['httpMethod'] == 'GET' and 'queryStringParameters' in event:
            return read_product(event)
        elif event['httpMethod'] == 'POST' and 'body' in event:
            return update_product(event)
        elif event['httpMethod'] == 'DELETE' and 'queryStringParameters' in event:
            return delete_product(event)
        else:
            raise ValueError("Unsupported HTTP method or missing parameters")
    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def read_product(event):
    product_id = event['queryStringParameters'].get('productId')
    if not product_id:
        raise ValueError("Missing required field: productId")

    response = table.get_item(Key={'productId': product_id})
    if 'Item' in response:
        return {'statusCode': 200, 'body': json.dumps(response['Item'])}
    else:
        return {'statusCode': 404, 'body': json.dumps({'message': 'Product not found'})}

def update_product(event):
    body = json.loads(event['body'])
    product_id = body.get('productId')
    update_key = body.get('updateKey')
    update_value = body.get('updateValue')

    if not product_id or not update_key or not update_value:
        raise ValueError("Missing required fields in payload")

    response = table.update_item(
        Key={'productId': product_id},
        UpdateExpression="set #attrName = :val",
        ExpressionAttributeNames={'#attrName': update_key},
        ExpressionAttributeValues={':val': update_value},
        ReturnValues="UPDATED_NEW"
    )
    return {'statusCode': 200, 'body': json.dumps({
        'message': 'Product updated successfully',
        'updatedAttributes': response['Attributes']
    })}

def delete_product(event):
    product_id = event['queryStringParameters'].get('productId')
    if not product_id:
        raise ValueError("Missing required field: productId")

    table.delete_item(Key={'productId': product_id})
    return {'statusCode': 200, 'body': json.dumps({'message': 'Product deleted successfully'})}
