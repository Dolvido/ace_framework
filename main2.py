# Importing necessary libraries
import requests
import time
import textwrap
from gpt4all import GPT4All
import json

#gpt4_instance = GPT4All("D:/guanaco-7B.ggmlv3.q5_1.bin")
gpt4_instance = GPT4All("D:/nous-hermes-13b.ggmlv3.q5_1.bin")

# Function to get messages from the bus
def get_messages(layer_number, bus_url, bus_type):
    response = requests.get(f"{bus_url}/message", params={'bus': bus_type, 'layer': layer_number})
    if response.status_code == 200:
        
        print(f"Layer {layer_number}: Messages retrieved from {bus_type} bus: {response.json()['messages']}")
        return response.json()['messages']
    else:
        print(f"Layer {layer_number}: Failed to get messages")
        return []

# Function to send messages to the bus
def send_message(layer_number, bus_url, bus_type, message):
    url = f"{bus_url}/message"
    payload = {"layer": layer_number, "bus": bus_type, "message": message}
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

    # Enhanced error handling
    try:
        if response.status_code == 200 and response.text.strip():  # Check if response is not empty
            print(f"Layer {layer_number}: Messages retrieved from {bus_type} bus: {response.json()['messages']}")
        else:
            print(f"Layer {layer_number}: No messages retrieved from {bus_type} bus or non-200 status code received.")
    except json.JSONDecodeError:
        print(f"Layer {layer_number}: Failed to decode JSON. Response content: {response.text}")

    return response

# Function to process messages
def process_messages(layer_number, bus_url, messages, system_message):
    formatted_messages = [msg['message'] for msg in messages]
    conversation = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': '\n'.join(formatted_messages)}
    ]

    # Using the shared GPT-4 instance to generate a response
    prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation])
    response = gpt4_instance.generate(prompt, max_tokens=2000, temp=0)
    print(f"Layer {layer_number}: GPT-4 prompt: {prompt}")

    print(f"Layer {layer_number}: Response received: {response}")  # Print the received response

    try:
        # Since the response is a string, we can directly return it after stripping
        return response.strip()  
    except Exception as e:
        print(f"Layer {layer_number}: Error - {e}")
        return "Error processing the message."

# Main function to simulate the processing of messages sequentially
def main():
    bus_url = "http://127.0.0.1:900"  # Adjust the URL as per your setup
    layer_numbers = range(1, 7)
    system_message_files = [
        'layer1.txt',
        'layer2.txt',
        'layer3.txt',
        'layer4.txt',
        'layer5.txt',
        'layer6.txt'
    ]

    while True:
        for layer_number, system_message_file in zip(layer_numbers, system_message_files):
            with open(system_message_file, 'r') as file:
                system_message = file.read().strip()

            # Processing north bus messages
            north_bus_messages = get_messages(layer_number, bus_url, 'north')
            if north_bus_messages:
                print(f"Layer {layer_number}: Processing north bus messages")
                response = process_messages(layer_number, bus_url, north_bus_messages, system_message)
                send_message(layer_number, bus_url, 'south', response)

            # Processing south bus messages
            south_bus_messages = get_messages(layer_number, bus_url, 'south')
            if south_bus_messages:
                print(f"Layer {layer_number}: Processing south bus messages")
                response = process_messages(layer_number, bus_url, south_bus_messages, system_message)
                send_message(layer_number, bus_url, 'north', response)

        # Adding a sleep to prevent too frequent requests
        time.sleep(5)

# Running the main function to start the simulation
main()
