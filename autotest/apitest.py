# import requests
# import json

# from flask import jsonify

# session = requests.Session()
#
# def test():
#
#     url = "http://127.0.0.1/autotest/login/"
#     body = {
#         'userName': 'fin',
#         'password': 'test123456',
#     }
#     body_format=''
#     if (body_format == 'JSON'):
#         body = json.dumps(body)
#     else:
#         keys = body.keys()
#         for rec in keys:
#             if ('[{' in str(body[rec]) and '}]' in str(body[rec])):
#                 body = json.dumps(body)
#                 break
#     r = session.post(url, body)
#     print(r.status_code)
#
#     print("testcase1 start")
#     expect_code_result=200
#     if expect_code_result==r.status_code:
#         apitest_result='pass'
#     else:
#         apitest_result='fail'
#     print(apitest_result)
#     print("testcase1 end")
#
#     print("testcase2 start")
#     expect_code_err_result=404
#     if expect_code_err_result==r.status_code:
#         apitest_result='pass'
#     else:
#         apitest_result='fail'
#     print(apitest_result)
#     print("testcase2 end")
#
#     return apitest_result

# test()


# from deepseek import DeepSeekModel
# from deepseek import DeepSeekAPI
# import openai
# from openai import OpenAI
#
# client=OpenAI(api_key="sk-06a1758a18cc4695868aa5a87e896f3c",base_url="https://api.deepseek.com")
#
# response=client.chat.completions.create(
#     model="deepseek-chat",
#     message=[{
#         "role": "fin",
#         "content":"test",
#     }],
#     stream=False
#
# )
#
# print(response.choices[0].mesage.content)
#


from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai import RunContext
from pydantic import BaseModel, Field

class AssistantResponse(BaseModel):
    content: str = Field(description="助手的回复内容")


class UserInfo(BaseModel):
    username: str = Field(description="用户的名字")
    email: str = Field(description="用户的邮箱地址")
    age: int = Field(description="用户的年龄", ge=0, le=120)


# model = OpenAIModel(
#     'deepseek-chat',
#     # result_type=UserInfo,
#     base_url='https://api.deepseek.com',
#     api_key='sk-06a1758a18cc4695868aa5a87e896f3c',
# )
# agent = Agent(model)
# print(agent.model.)
# agent.run(result_type=UserInfo)


# agent = Agent("openai:gpt-4o", result_type=UserInfo, system_prompt="Extract user information")

# result = agent.run_sync("The user with ID 123 is called Samuel, born on Jan 28th 87")
# print(result.data)

import requests

API_KEY = "sk-06a1758a18cc4695868aa5a87e896f3c"  # 替换为你的 DeepSeek API 密钥
API_URL = "http://127.0.0.1:11434"  # DeepSeek API 地址


def query_deepseek(prompt: str) -> AssistantResponse:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": "deepseek-r1",  # 使用 DeepSeek-R1 模型
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "stream": False  # 设置为 False 以获取完整响应
    }
    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        data = response.json()
        assistant_message = data["choices"][0]["message"]["content"]
        return AssistantResponse(content=assistant_message)
    else:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")


prompt = "你好，请介绍一下你自己"
response = query_deepseek(prompt)
print(response.content)



# 加载一个预训练的模型，帮我们节省时间
# model = DeepSeekModel.load_pretrained("deepseek-base")
#
# # 这里是我们的训练数据，你可以根据自己的需求来填充数据
# train_data = [1,2,3] # 你的数据
#
#
# # 微调模型，让它学习如何回答问题
# model.fine_tune(train_data, epochs=3, batch_size=8)
#
# def chat():
#     user_input = requests.json.get("message")
#     response = model.generate(user_input) # 让模型生成回应
#     return jsonify({"response": response})

# chat()



#sk-06a1758a18cc4695868aa5a87e896f3c

