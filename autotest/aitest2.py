import time
from ollama import Client

client=Client(
    host='http://127.0.0.1:11434',
    headers={'x-some-header':'some-value'}
)

now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

response = client.chat(model='deepseek-r1:1.5b',
                       messages=[
                           {
                               "role": "system",
                                "content": "用户将提供给你一段功能需求内容，请你分析需求，并以等价类、边界值，错误猜测法设计生成2到6个功能测试用例，注意一定要大于等于2个小于6个，"
                                              "每个功能测试用例都以 JSON 的形式输出，输出的 JSON 需遵守以下的格式：\n\n"
                                              "{"
                                              "\n  \"用例标题\": <用例标题，格式为中文>,"
                                              "\n  \"创建时间\": <" + now + ">,"
                                                                            "\n  \"创建人\": \"fin\","
                                                                            "\n  \"步聚1\": <操作步聚>,"
                                                                            "\n  \"预期结果1\": <预期结果1>,"
                                                                            "\n  \"步聚2\": <操作步聚>,"
                                                                            "\n  \"预期结果2\": <预期结果2>,"
                                                                            "\n  \"步聚3\": <操作步聚>,"
                                                                            "\n  \"预期结果3\": <预期结果3>,"
                                              "},"
                                              "\n{"
                                              "\n  \"用例标题\": <用例标题，格式为中文>,"
                                              "\n  \"创建时间\": <" + now + ">,"
                                                                            "\n  \"创建人\": \"fin\","
                                                                            "\n  \"步聚1\": <操作步聚>,"
                                                                            "\n  \"预期结果1\": <预期结果1>,"
                                                                            "\n  \"步聚2\": <操作步聚>,"
                                                                            "\n  \"预期结果2\": <预期结果2>,"
                                                                            "\n  \"步聚3\": <操作步聚>,"
                                                                            "\n  \"预期结果3\": <预期结果3>,"
                                                                            "}"
                           },
                           {
                               "role": "user",
                               "content": "系统登录功能"
                           }
                       ]
                       )

print(response.message.content)