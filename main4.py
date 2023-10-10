import requests
import time
import json
from gpt4all import GPT4All

# Instantiating the GPT-4 model
gpt4_instance = GPT4All("D:/nous-hermes-13b.ggmlv3.q5_1.bin")

# Enhanced Layer class with specific message processing logic
class EnhancedLayer:
    def __init__(self, layer_number, mission_imperatives):
        self.layer_number = layer_number
        self.mission_imperatives = mission_imperatives

    def process_message(self, messages):
        # Incorporating mission imperatives into the processing logic
        formatted_messages = '\n'.join([msg['message'] for msg in messages])
        conversation = [
            {'role': 'system', 'content': self.mission_imperatives},
            {'role': 'user', 'content': formatted_messages}
        ]

        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation])
        response = gpt4_instance.generate(prompt, max_tokens=2000, temp=0)

        return response.strip()

# Function to get messages from the bus
def get_messages(layer_number, bus_url, bus_type):
    response = requests.get(f"{bus_url}/message", params={'bus': bus_type, 'layer': layer_number})
    return response.json()['messages'] if response.status_code == 200 else []

# Function to send messages to the bus
def send_message(layer_number, bus_url, bus_type, message):
    payload = {"layer": layer_number, "bus": bus_type, "message": message}
    headers = {'Content-Type': 'application/json'}
    requests.post(f"{bus_url}/message", headers=headers, data=json.dumps(payload))

# Main function to simulate the processing of messages sequentially
def main():
    bus_url = "http://127.0.0.1:900"  # Adjust the URL as per your setup
    layer_numbers = range(1, 7)
    system_message_files = [f'layer{i}.txt' for i in layer_numbers]

    while True:
        for layer_number, system_message_file in zip(layer_numbers, system_message_files):
            with open(system_message_file, 'r') as file:
                mission_imperatives = file.read().strip()

            layer = EnhancedLayer(layer_number, mission_imperatives)

            # Processing north bus messages
            north_bus_messages = get_messages(layer_number, bus_url, 'north')
            if north_bus_messages:
                print(f"Layer {layer_number}: Processing north bus messages")
                response = layer.process_message(north_bus_messages)
                send_message(layer_number, bus_url, 'south', response)

            # Processing south bus messages
            south_bus_messages = get_messages(layer_number, bus_url, 'south')
            if south_bus_messages:
                print(f"Layer {layer_number}: Processing south bus messages")
                response = layer.process_message(south_bus_messages)
                send_message(layer_number, bus_url, 'north', response)

        # Adding a sleep to prevent too frequent requests
        time.sleep(5)

# Running the main function to start the simulation
main()
