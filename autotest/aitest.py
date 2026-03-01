# from openai import OpenAI
#
# client = OpenAI(
#     base_url="http://localhost:11434",
#     api_key="ollama"  # 任意非空字符串
# )
#
# response = client.chat.completions.create(
#     model="deepseek-r1:1.5b",
#     messages=[{"role": "user", "content": "解释神经网络的工作原理"}],
#     temperature=0.5,
#     response_format={"type": "json_object"}
# )
#
# print(response)


from ollama import Client

client=Client(
    host='http://127.0.0.1:11434',
    headers={'x-some-header':'some-value'}
)

response = client.chat(model='deepseek-r1:1.5b',messages=[
{
    'role':'user',
    'content':'你是谁？',
},
])

print(response.message.content)