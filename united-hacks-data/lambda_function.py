import json
import boto3


def response(success=False, message='', response_uuid='', json_data=None):
    if json_data is None:
        json_data = {}
    response_json = {
        'success': success,
        'message': message,
        'uuid': response_uuid,
        'data': json_data
    }

    response_object = {'statusCode': 200,
                       'headers': {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
                       'body': json.dumps(response_json)}

    return response_object


def lambda_handler(event, context):
    required_query = ['uuid']
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('SmartSchedule')

    print('Provided Query Parameters: ', event['queryStringParameters'])

    if event['queryStringParameters'] is None:
        return response(False, 'Parameter Not Provided')

    for query in required_query:
        if query not in event['queryStringParameters'].keys():
            return response(False, 'Insufficient Parameters Provided')

    try:
        fetched_data = table.get_item(Key={'id': event['queryStringParameters']['uuid']})
        json_data = json.loads(fetched_data['Item']['JSONData'])
        return response(True, 'Fetch Complete', event['queryStringParameters']['uuid'], json_data)
    except Exception as e:
        print('[Error]', e)
        return response(False, 'Failed to Fetch Data from Database')
