from threading import Thread
import traceback
import requests
import json
from time import sleep
from datetime import datetime
import textwrap
from gpt4all import GPT4All

# Mocking the GPT-4 instance for the purpose of this example, as we can't run actual GPT-4 model due to limitations.
# In a real-world scenario, this should be replaced with actual implementation to interact with GPT-4 model.
class MockGPT4Instance:
    def generate(self, prompt, max_tokens, temp):
        # Mock response, returns the received prompt with additional text
        return {"choices": [{"message": {"content": f"Response to: {prompt}"}}]}


# Shared GPT-4 instance
gpt4_instance = GPT4All("D:/guanaco-7B.ggmlv3.q5_1.bin")



class ACELayer(Thread):
    def __init__(self, layer_number, bus_url, system_message_file):
        super().__init__()
        self.layer_number = layer_number
        self.bus_url = bus_url
        self.system_message_file = system_message_file
        self.running = True

    def send_message(self, bus, message):
        data = {'bus': bus, 'layer': self.layer_number, 'message': message}
        response = requests.post(f"{self.bus_url}/message", json=data)
        if response.status_code == 200:
            print(f"Layer {self.layer_number}: Message sent successfully")
        else:
            print(f"Layer {self.layer_number}: Failed to send message")

    def get_messages(self, bus):
        response = requests.get(f"{self.bus_url}/message", params={'bus': bus, 'layer': self.layer_number})
        if response.status_code == 200:
            return response.json()['messages']
        else:
            print(f"Layer {self.layer_number}: Failed to get messages")
            return []

    def process_messages(self, messages):
        formatted_messages = [msg['message'] for msg in messages]
        with open(self.system_message_file, 'r') as file:
            system_message = file.read().strip()
        
        conversation = [
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': '\n'.join(formatted_messages)}
        ]

        # Here we use the shared GPT-4 instance to generate response
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation])
        response = gpt4_instance.generate(prompt, max_tokens=200, temp=0)
        return response['choices'][0]['message']['content'].strip()

    def run(self):
        print(f"Layer {self.layer_number} started")
        while self.running:
            try:
                # Handling north bus messages
                try:
                    north_bus_messages = self.get_messages('north')
                    if north_bus_messages:
                        print(f"Layer {self.layer_number}: Processing north bus messages")
                        response = self.process_messages(north_bus_messages)
                        self.send_message('south', response)
                    else:
                        print(f"Layer {self.layer_number}: No messages on north bus")
                except Exception as e:
                    print(f"Layer {self.layer_number}: Error processing north bus messages - {e}")
                    print(traceback.format_exc())

                # Handling south bus messages
                try:
                    south_bus_messages = self.get_messages('south')
                    if south_bus_messages:
                        print(f"Layer {self.layer_number}: Processing south bus messages")
                        response = self.process_messages(south_bus_messages)
                        self.send_message('north', response)
                    else:
                        print(f"Layer {self.layer_number}: No messages on south bus")
                except Exception as e:
                    print(f"Layer {self.layer_number}: Error processing south bus messages - {e}")
                    print(traceback.format_exc())

                sleep(5)  # Prevent too frequent requests
            except Exception as e:
                print(f"Layer {self.layer_number}: Unexpected error - {e}")
                print(traceback.format_exc())
                sleep(5)  # Prevent rapid error printing

    def stop(self):
        self.running = False


# Paths to the system message files for each layer
system_message_files = [
    'layer1.txt',
    'layer2.txt',
    'layer3.txt',
    'layer4.txt',
    'layer5.txt',
    'layer6.txt'
]

# Creating layer instances and starting them
layers = [ACELayer(i+1, "http://127.0.0.1:900", system_message_files[i]) for i in range(6)]

# Print the system messages to debug if they are being read correctly
for layer, system_message_file in zip(layers, system_message_files):
    with open(system_message_file, 'r') as file:
        print(f"System message for Layer {layer.layer_number}:")
        print(textwrap.indent(file.read().strip(), '    '))
        print()

# Starting all layers
for layer in layers:
    layer.start()

# For demonstration purposes, we will let the layers run for a while and then stop them.
# In a real application, you would likely have a more graceful shutdown process.
sleep(60)  # Let the layers run for 60 seconds

# Stopping all layers
for layer in layers:
    layer.stop()

# Waiting for all threads to complete
for layer in layers:
    layer.join()

print("All layers have been stopped.")