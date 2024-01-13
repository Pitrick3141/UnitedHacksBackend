import requests

prompt = input("What is your new year resolution?")

headers = {'Content-Type': 'application/json',
           'Authorization': 'Bearer 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'}

base_url = 'https://api.openai.com/v1/chat/completions'

preset_instruction = '''
Given a user's New Year resolution or goal, generate a year-long schedule in the format of a json object.
The schedule should outline a feasible plan, broken down into months, for achieving the stated resolution.
If the user input is invalid or unclear, respond with "{'result': 'Invalid input', 'schedule': []}"
The schedule in json object should be an array of objects, separated by commas, each object in the array represents a month.
Every month object should contain the name of the month, the activity for the month and a target to be done by the end of the month.

Example Month Object: {'month': 'Jan', 'activity': 'Join a gym, set fitness goals', 'target': 'have a gym membership and a fitness goal'}

Example Input:
User: My New Year resolution is to improve my physical fitness.

Example Output:
{'result': 'Generate complete', 'schedule': [
{'month': 'Jan', 'activity': 'Join a gym, set fitness goals', 'target': 'Have a gym membership and a fitness goal'},
{'month': 'Feb', 'activity': 'Start regular workouts', 'target': 'Create a workout plan'},
{'month': 'Mar', 'activity': 'Incorporate healthy diet', 'target': 'Have a healthy meal plan'},
...,
{'month': 'Dec', 'activity': 'Evaluate progress, set new goal', 'target': 'Reflect your year and plan for the new year'}]}

Note: This is a template, and GPT-4.0 should customize the schedule based on the user's specific resolution or goal.
Important: The result must be in proper JSON form and must contain the following keys: result, schedule.
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
print(res)
