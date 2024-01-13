import json


def lambda_handler(event, context):
    # Handle Headers
    origin = ''
    if 'origin' in event['headers'].keys():
        origin = event['headers']['origin']

    # Generate Response Json
    response_json = {'message': 'test complete!', 'request_event': json.dumps(event)}

    # Generate Response Object
    response_object = {'statusCode': 200,
                       'headers': {'Access-Control-Allow-Origin': origin, 'Content-Type': 'application/json'},
                       'body': json.dumps(response_json)}

    return response_object
