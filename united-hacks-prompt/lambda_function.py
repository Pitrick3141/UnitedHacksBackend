import json
import datetime

import boto3
import requests
import uuid


def generate_general_schedule(prompt, **kwargs):
    headers = {'Content-Type': 'application/json',
               'Authorization': ''}

    base_url = 'https://api.openai.com/v1/chat/completions'

    model = 'gpt-3.5-turbo'

    temperature = 0.7

    if 'model' in kwargs.keys():
        model = kwargs['model']

    preset_instruction = '''
    Given a user's New Year resolution or goal, generate a year-long schedule in the format of a json object.
    The schedule should outline a feasible plan, broken down into months, for achieving the stated resolution.
    
    The schedule in json object should be an array of objects, separated by commas, each object in the array represents a month.
    Every month object should contain the name of the month, the activity for the month and a goal to be done by the end of the month.
    
    Example Month Object: {"month": "Jan", "activity": "Join a gym, set fitness goals", "goal": "have a gym membership and a fitness goal"}
    
    Example Input:
    User: My New Year resolution is to improve my physical fitness.
    
    Example Output:
    {"result": "Generate complete", "schedule": [
    {"month": "Jan", "activity": "Join a gym, set fitness goals", "goal": "Have a gym membership and a fitness goal"},
    {"month": "Feb", "activity": "Start regular workouts", "goal": "Create a workout plan"},
    {"month": "Mar", "activity": "Incorporate healthy diet", "goal": "Have a healthy meal plan"},
    ...,
    {"month": "Dec", "activity": "Evaluate progress, set new goal", "goal": "Reflect your year and plan for the new year"}]}
    
    Note: This is a template, and GPT should customize the schedule based on the user's specific resolution or goal, please assume that the user have solid foundations and preparation for their new year resolution.
    Note: There should be no repeated months and the number of months should not exceed 12.
    Important: The response must be in the format provided above, even though a schedule cannot be generated or there are other problems.
    '''

    request_json = {
        'model': model,
        'messages': [{'role': 'system',
                      'content': preset_instruction},
                     {'role': 'user',
                      'content': prompt}],
        'temperature': temperature
    }

    res = requests.post(url=base_url, headers=headers, json=request_json).json()
    return res


def generate_month_schedule(prompt, **kwargs):
    headers = {'Content-Type': 'application/json',
               'Authorization': ''}

    base_url = 'https://api.openai.com/v1/chat/completions'

    model = 'gpt-3.5-turbo'

    temperature = 0.7

    if 'model' in kwargs.keys():
        model = kwargs['model']

    preset_instruction = '''
        Given a user's monthly activity and goal, elaborate a detailed schedule in the format of a json object.
        The schedule should outline a feasible plan, broken down into 4 weeks, for achieving the stated monthly goal.
        
        The schedule in json object should be an array of 4 objects, separated by commas, each object in the array represents a week.
        Every week object should contain the name of the week, several activities for each week and a goal to be done by the end of the week.

        Example Week Object: 
        {
        "week": "week1", 
        "activity": ["Brisk walking or jogging", "Strength training", "Yoga or stretching", "High-intensity interval training (HIIT) workout"], 
        "goal": ["Establishing a Routine", "Keeping a Routine", "Intensifying and Diversifying"]
        }

        Example Input:
        User: {"month": "Feb", "activity": "Start regular workouts", "goal": "Create a workout plan"}

        Example Output:
        {"result": "Generate complete", "schedule": [
        {"week": "week1", "activity": ["Brisk walking or jogging", "Strength training", "Yoga or stretching", "High-intensity interval training (HIIT) workout"], "goal": ["Establishing a Routine", "Keeping a Routine", "Intensifying and Diversifying"]},
        {"week": "week2", "activity": ["Rest or light activity", "Full-body strength training", "Meditation or relaxation exercises", "Active recreation (hiking, biking, or sports)"], "goal": [...]},
        {"week": "week3", "activity": [...], "goal": [...]},
        {"week": "week4", "activity": [...], "goal": [...]},
        ]}

        Note: This is a template, and GPT should customize the schedule based on the user's specific resolution or goal, please assume that the user have solid foundations and preparation for their new year resolution.
        Note: There should be no repeated weeks and the number of weeks should not exceed 4.
        Important: The response must be in the format provided above, even though a schedule cannot be generated or there are other problems.
        '''

    request_json = {
        'model': model,
        'messages': [{'role': 'system',
                      'content': preset_instruction},
                     {'role': 'user',
                      'content': prompt}],
        'temperature': temperature
    }

    res = requests.post(url=base_url, headers=headers, json=request_json).json()
    return res


def response(success=False, message='', prompt_type='', schedule=None, **kwargs):
    if schedule is None:
        schedule = {}
    response_json = {
        'success': success,
        'message': message,
        'type': prompt_type,
        'schedule': schedule
    }
    for key in kwargs.keys():
        response_json[key] = kwargs[key]

    response_uuid = str(uuid.uuid1())
    response_json['uuid'] = response_uuid
    response_json = json.dumps(response_json)

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('SmartSchedule')

    est_time_delta = datetime.timedelta(hours=-5)
    est_object = datetime.timezone(est_time_delta, name='EST')

    table.put_item(Item={'id': response_uuid,
                         'CreatedAt': datetime.datetime.now(datetime.timezone.utc).astimezone(est_object).isoformat(timespec='milliseconds'),
                         'JSONData': response_json})
    response_object = {'statusCode': 200,
                       'headers': {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
                       'body': response_json}
    return response_object


def lambda_handler(event, context):
    required_query = []
    generate_month = False
    generated_schedule = {}

    print('Provided Query Parameters:', event['queryStringParameters'])

    if event['queryStringParameters'] is None:
        return response(False, 'Parameter Not Provided')

    if 'type' in event['queryStringParameters'].keys():
        if event['queryStringParameters']['type'] == 'month':
            required_query = ['month', 'activity', 'goal']
            generate_month = True
        else:
            required_query = ['goal']
            generate_month = False

    for query in required_query:
        if query not in event['queryStringParameters'].keys():
            return response(False, 'Insufficient Parameters Provided')

    if generate_month:
        month_prompt = "{{\"month\": \"{}\", \"activity\": \"{}\", \"goal\": \"{}\"}}".format(
            event['queryStringParameters']['month'],
            event[
                'queryStringParameters'][
                'activity'],
            event[
                'queryStringParameters'][
                'goal'])
        if 'model' in event['queryStringParameters'].keys():
            generated_data_raw = generate_month_schedule(month_prompt, model=event['queryStringParameters']['model'])
        else:
            generated_data_raw = generate_month_schedule(month_prompt)

    else:
        if 'model' in event['queryStringParameters'].keys():
            generated_data_raw = generate_general_schedule(event['queryStringParameters']['goal'],
                                                           model=event['queryStringParameters']['model'])
        else:
            generated_data_raw = generate_general_schedule(event['queryStringParameters']['goal'])

    if 'choices' in generated_data_raw.keys():
        if 'message' in generated_data_raw['choices'][0].keys():
            formatted_data = generated_data_raw['choices'][0]['message']['content'].replace("\n", "")
            print('Generated Data:', formatted_data)
            generated_schedule = json.loads(formatted_data)

    if 'result' in generated_schedule.keys():
        if generated_schedule['result'] == 'Generate complete':
            if generate_month:
                return response(True, 'Generate Complete', 'month', generated_schedule['schedule'],
                                month=event['queryStringParameters']['month'],
                                goal=event['queryStringParameters']['goal'],
                                activity=event['queryStringParameters']['activity'])
            else:
                return response(True, 'Generate Complete', 'general', generated_schedule['schedule'],
                                goal=event['queryStringParameters']['goal'])
        else:
            if generate_month:
                return response(False, generated_schedule['result'], 'month', None,
                                month=event['queryStringParameters']['month'],
                                goal=event['queryStringParameters']['goal'],
                                activity=event['queryStringParameters']['activity'])
            else:
                return response(False, generated_schedule['result'], 'general', None,
                                goal=event['queryStringParameters']['goal'])
    else:
        if generate_month:
            return response(False, 'Generation Failed', 'month', None,
                            month=event['queryStringParameters']['month'],
                            goal=event['queryStringParameters']['goal'],
                            activity=event['queryStringParameters']['activity'])
        else:
            return response(False, 'Generation Failed', 'general', None,
                            goal=event['queryStringParameters']['goal'])
