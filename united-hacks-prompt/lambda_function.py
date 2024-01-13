import json

import requests


def generate_general_schedule(prompt):
    headers = {'Content-Type': 'application/json',
               'Authorization': ''}

    base_url = 'https://api.openai.com/v1/chat/completions'

    preset_instruction = '''
    Given a user's New Year resolution or goal, generate a year-long schedule in the format of a json object.
    The schedule should outline a feasible plan, broken down into months, for achieving the stated resolution.
    If the user input is invalid or unclear, respond with "{"result": "Invalid input", "schedule": []}"
    The schedule in json object should be an array of objects, separated by commas, each object in the array represents a month.
    Every month object should contain the name of the month, the activity for the month and a target to be done by the end of the month.
    
    Example Month Object: {"month": "Jan", "activity": "Join a gym, set fitness goals", "target": "have a gym membership and a fitness goal"}
    
    Example Input:
    User: My New Year resolution is to improve my physical fitness.
    
    Example Output:
    {"result": "Generate complete", "schedule": [
    {"month": "Jan", "activity": "Join a gym, set fitness goals", "target": "Have a gym membership and a fitness goal"},
    {"month": "Feb", "activity": "Start regular workouts", "target": "Create a workout plan"},
    {"month": "Mar", "activity": "Incorporate healthy diet", "target": "Have a healthy meal plan"},
    ...,
    {"month": "Dec", "activity": "Evaluate progress, set new goal", "target": "Reflect your year and plan for the new year"}]}
    
    Note: This is a template, and GPT-4.0 should customize the schedule based on the user's specific resolution or goal.
    '''

    request_json = {
        'model': 'gpt-3.5-turbo',
        'messages': [{'role': 'system',
                      'content': preset_instruction},
                     {'role': 'user',
                      'content': prompt}],
        'temperature': 0.7
    }

    res = requests.post(url=base_url, headers=headers, json=request_json).json()
    return res


def generate_month_schedule(prompt):
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer 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'}

    base_url = 'https://api.openai.com/v1/chat/completions'

    preset_instruction = '''
        Given a user's monthly activity and goal, elaborate a detailed schedule in the format of a json object.
        The schedule should outline a feasible plan, broken down into weeks, for achieving the stated monthly goal.
        If the user input is invalid or unclear, respond with "{"result": "Invalid input", "schedule": []}"
        The schedule in json object should be an array of objects, separated by commas, each object in the array represents a week.
        Every weel object should contain the name of the week, several activities for each week and a targets to be done by the end of the week.

        Example Week Object: 
        {
        "week": "week1", 
        "activity": ["Brisk walking or jogging", "Strength training", "Yoga or stretching", "High-intensity interval training (HIIT) workout"], 
        "goal": ["Establishing a Routine", "Keeping a Routine", "Intensifying and Diversifying"]
        }

        Example Input:
        User: {"month": "Feb", "activity": "Start regular workouts", "target": "Create a workout plan"}

        Example Output:
        {"result": "Generate complete", "schedule": [
        {"week": "week1", "activity": ["Brisk walking or jogging", "Strength training", "Yoga or stretching", "High-intensity interval training (HIIT) workout"], "goal": ["Establishing a Routine", "Keeping a Routine", "Intensifying and Diversifying"]},
        {"week": "week2", "activity": ["Rest or light activity", "Full-body strength training", "Meditation or relaxation exercises", "Active recreation (hiking, biking, or sports)"], "goal": [...]},
        {"week": "week3", "activity": [...], "goal": [...]},
        {"week": "week4", "activity": [...], "goal": [...]},
        ]}

        Note: This is a template, and GPT should customize the schedule based on the user's specific resolution or goal.
        '''

    request_json = {
        'model': 'gpt-3.5-turbo',
        'messages': [{'role': 'system',
                      'content': preset_instruction},
                     {'role': 'user',
                      'content': prompt}],
        'temperature': 0.7
    }

    res = requests.post(url=base_url, headers=headers, json=request_json).json()
    return res


def response(success=False, message='', prompt='', prompt_type='', schedule=None):
    if schedule is None:
        schedule = {}
    response_json = {
        'success': success,
        'message': message,
        'prompt': prompt,
        'type': prompt_type,
        'schedule': schedule
    }
    response_object = {'statusCode': 200,
                       'headers': {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
                       'body': json.dumps(response_json)}

    return response_object


def lambda_handler(event, context):
    required_query = []
    generate_month = False
    month_prompt = {}
    generated_schedule = {}

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
        month_prompt = "{{\"month\": \"{}\", \"activity\": \"{}\", \"target\": \"{}\"}}".format(
            event['queryStringParameters']['month'],
            event[
                'queryStringParameters'][
                'activity'],
            event[
                'queryStringParameters'][
                'goal'])
        generated_data_raw = generate_month_schedule(month_prompt)
        print(generated_data_raw)
    else:
        generated_data_raw = generate_general_schedule(event['queryStringParameters']['goal'])
        print(generated_data_raw)

    if 'choices' in generated_data_raw.keys():
        if 'message' in generated_data_raw['choices'][0].keys():
            generated_schedule = json.loads(generated_data_raw['choices'][0]['message']['content'])

    if 'result' in generated_schedule.keys():
        if generated_schedule['result'] == 'Generate complete':
            return response(True, 'Generate Complete',
                            month_prompt if generate_month else event['queryStringParameters']['goal'],
                            'month' if generate_month else 'general', generated_schedule['schedule'])
        else:
            return response(False, 'Invalid Prompt',
                            month_prompt if generate_month else event['queryStringParameters']['goal'],
                            'month' if generate_month else 'general')
    else:
        return response(False, 'Generate Failed',
                        month_prompt if generate_month else event['queryStringParameters']['goal'],
                        'month' if generate_month else 'general')
