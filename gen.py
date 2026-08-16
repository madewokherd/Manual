import json

with open('src/data/options.json') as f:
    options = json.load(f)

max_tasks = options['user']['num_tasks']['range_end']

items = []
for i in range(1, max_tasks+1):
    item = {
        'name': f'Task {i:03}',
        'filler': False,
        'trap': False,
        'useful': True,
        'progression': True,
        'category': ['Task'],
        }
    items.append(item)

with open('src/data/items.json','w') as f:
    json.dump(items, f)

locations = [
    {
        'name': "Victory",
        'victory': True,
        'requires': '{OptionCountPercent(@Task, completion_percentage)}'
    }
]
for i in range(1, max_tasks+1):
    location = {
        'name': f'Task {i:03} Reward',
        'requires': f'|Task {i:03}|',
        }
    locations.append(location)

with open('src/data/locations.json','w') as f:
    json.dump(locations, f)

