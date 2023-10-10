
# Importing necessary libraries
from queue import Queue
from gpt4all import GPT4All

# Actual GPT4All language model for processing messages
class GPT4AllLanguageModel:
    def __init__(self, model_path):
        from gpt4all import GPT4All  # Importing GPT4All when the class is instantiated
        self.model = GPT4All(model_path)

    def process(self, layer_number, message):
        # Generating a response using the provided GPT4All model
        response = self.model.generate(message, max_tokens=2000, temp=0)
        return f"Processed by Layer{layer_number}: {response}"

# Creating a shared instance of the GPT4All language model
language_model = GPT4AllLanguageModel("D:/nous-hermes-13b.ggmlv3.q5_1.bin")


# Layer class to represent each layer in the ACE framework
class Layer:
    def __init__(self, layer_number, mission_file_path):
        self.layer_number = layer_number
        self.mission_imperatives = self.load_mission_imperatives(mission_file_path)

    def load_mission_imperatives(self, file_path):
        try:
            with open(file_path, 'r') as file:
                return file.read().strip()
        except Exception as e:
            print(f"Error loading mission imperatives from {file_path}: {e}")
            return ""

    def process_message(self, message):
        response = language_model.process(self.layer_number, message)
        return response

# Enhanced Layer class with optimized message processing logic
class EnhancedLayer(Layer):
    def process_message(self, message):
        keywords = self.mission_imperatives.lower().split()
        response = "General message processed."
        for keyword in keywords:
            if keyword in message.lower():
                response = f"{keyword.capitalize()} message processed."
                break
        response = language_model.process(self.layer_number, f"Layer{self.layer_number}: {response}")
        return response

# Communication bus class representing the northbound and southbound buses
class EnhancedBus(Queue):
    def __init__(self):
        super().__init__()
        self.log = []
    
    def send_message(self, message, layer_number):
        structured_message = {"content": message, "layer_number": layer_number}
        self.put(structured_message)
        self.log.append(structured_message)
    
    def fetch_message(self, layer_number):
        for message in list(self.queue):
            if message["layer_number"] == layer_number:
                self.queue.remove(message)
                return message["content"]
        return None

# Instantiating the layers and communication buses
layers = {
    1: Layer(1, "layer1.txt"),
    2: Layer(2, "layer2.txt"),
    3: Layer(3, "layer3.txt"),
    4: Layer(4, "layer4.txt"),
    6: Layer(6, "layer6.txt")
}
northbound_bus = EnhancedBus()
southbound_bus = EnhancedBus()

# Main processing loop function with optimized logic
def optimized_main_loop():
    iteration = 0
    max_iterations = 5
    test_messages = [
        "Priority task for optimization", 
        "New strategy for enhancement",
        "Update model for refinement"
    ]
    for i, msg in enumerate(test_messages):
        northbound_bus.send_message(msg, i+1)

    while iteration < max_iterations:
        print(f"Iteration {iteration + 1}:")
        
        for layer_number, layer in layers.items():
            message = northbound_bus.fetch_message(layer_number)
            if message:
                response = layer.process_message(message)
                southbound_bus.send_message(response, layer_number)
                print(f"  Layer {layer_number} Response to Northbound Message: {response}")
        
        print("  Southbound Messages:")
        for layer_number in layers.keys():
            message = southbound_bus.fetch_message(layer_number)
            if message:
                print(f"    Layer {layer_number}: {message}")
        
        print("-" * 50)
        iteration += 1

# Running the optimized main processing loop
optimized_main_loop()
