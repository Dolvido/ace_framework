import requests
import time
import discord
from discord.ext import tasks
from gpt4all import GPT4All


# Mocking the GPT-4 instance for testing purposes
class MockGPT4Instance:
    def generate(self, prompt, max_tokens, temp):
        # Simulating a response from the GPT-4 model
        return {"choices": [{"message": {"content": f"Response to: {prompt}"}}]}

# Shared GPT-4 instance - Replace this with actual GPT-4 instance or API
gpt4_instance = MockGPT4Instance()
gpt4_instance = GPT4All("D:/guanaco-7B.ggmlv3.q5_1.bin")

# Function to get messages from the bus
def get_messages(layer_number, bus_url, bus_type):
    response = requests.get(f"{bus_url}/message", params={'bus': bus_type, 'layer': layer_number})
    if response.status_code == 200:
        messages = response.json()['messages']
        print(f"Retrieved {len(messages)} {bus_type} bus messages for layer {layer_number}: {messages}")  # Debug print
        return messages
    else:
        print(f"Layer {layer_number}: Failed to get messages")
        return []

# Function to send messages to the bus
def send_message(layer_number, bus_url, bus_type, message):
    data = {'bus': bus_type, 'layer': layer_number, 'message': message}
    response = requests.post(f"{bus_url}/message", json=data)
    if response.status_code == 200:
        print(f"Layer {layer_number}: Message sent successfully")
    else:
        print(f"Layer {layer_number}: Failed to send message")

# Function to process messages
def process_messages(layer_number, bus_url, messages, system_message):
    formatted_messages = [msg['message'] for msg in messages]
    conversation = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': '\\n'.join(formatted_messages)}
    ]

    # Using the shared GPT-4 instance to generate a response
    prompt = "\\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation])
    response = gpt4_instance.generate(prompt, max_tokens=2000, temp=0)

    print(f"Layer {layer_number}: Response received: {response}")  # Print the received response

    try:
        # Since the response is a string, we can directly return it after stripping
        return response.strip()  
    except Exception as e:
        print(f"Layer {layer_number}: Error - {e}")
        return "Error processing the message."

import discord
from discord.ext import tasks

intents = discord.Intents.default()  # Use default intents
intents.messages = True


class MyBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, intents=intents)

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        self.process_messages_bg_task.start()

    @tasks.loop(seconds=5)
    async def process_messages_bg_task(self):
        send_message("Task is running")  # Debug print
        channel = self.get_channel('1160768315535405156')  # Set your Discord channel ID here

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

        for layer_number, system_message_file in zip(layer_numbers, system_message_files):
            print(f"Processing layer {layer_number}")
            with open(system_message_file, 'r') as file:
                system_message = file.read().strip()

            # Processing north bus messages
            north_bus_messages = get_messages(layer_number, bus_url, 'north')
            if north_bus_messages:
                print(f"North bus messages found for layer {layer_number}")  # Debug print

                print(f"Layer {layer_number}: Processing north bus messages")
                response = process_messages(layer_number, bus_url, north_bus_messages, system_message)
                send_message(layer_number, bus_url, 'south', response)
                await channel.send(f"Layer {layer_number}: {response}")

            # Processing south bus messages
            south_bus_messages = get_messages(layer_number, bus_url, 'south')
            if south_bus_messages:
                print(f"Layer {layer_number}: Processing south bus messages")
                response = process_messages(layer_number, bus_url, south_bus_messages, system_message)
                send_message(layer_number, bus_url, 'north', response)
                await channel.send(f"Layer {layer_number}: {response}")

bot = MyBot()
bot.run('MTE1NzAxODM0OTU3OTAxNDE1Ng.GM4NS6.Bw_q0GdV7CO7IliGo70v5dgiWTj0WLA3g5-7rk')  # Replace with your actual Discord bot token
