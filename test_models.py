from google import genai

client = genai.Client(api_key="GEMINIAI_API_KEY")

print("Here are the models you can use:")
for model in client.models.list():
    print(model.name)
