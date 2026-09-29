import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
import function_call_schedule , function_call_email

load_dotenv()
user_prompt = "檢查我的email，教授有傳給我甚麼信件？"
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

#告訴gemini 使用get today schedule function 
schedule_function = types.FunctionDeclaration(
    name = "get_today_schedule",
    description="取得使用者今天的行程。當使用者詢問今天的行程、安排或今天要做什麼時使用。",
     parameters_json_schema={
        "type": "object",
        "properties": {
            "day": {
                "type": "string" , 
                "description": "填入今天或明天"
            }
        },
        "required": [
            "day"
        ]
    }
)

emails_function = types.FunctionDeclaration(
    name = "get_email" ,
    description = "查看信件內容",
    parameters_json_schema= {
        "type" : "object",
        "properties" : {
            "keyword" : {
                "type" : "string" ,
                "description": "只有當使用者明確詢問 Email、信件、郵件、寄件人或收件匣內容時才使用此工具。一般知識問題或與 Email 無關的問題不要使用。 "
            }
        },
        "required" : [
            "keyword"
        ]
    }
)

tool = types.Tool(
    function_declarations = [
        schedule_function,
        emails_function
    ]
)

#問 gemini 
response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents=user_prompt ,
    config = types.GenerateContentConfig(
        tools=[tool]
    )
)
print("Gemini 回傳的 function calls：")
print(response.function_calls)

if response.function_calls:
    function_call = response.function_calls[0]

    print("Gemini想呼叫 :", function_call.name)
    print("Gemini 給的參數：", function_call.args)

    if function_call.name == "get_today_schedule":
        day = function_call.args["day"]
        result = function_call_schedule.get_today_schedule(day)

    elif function_call.name == "get_email":
        keyword = function_call.args["keyword"]
        result = function_call_email.get_email(keyword)
    else:
        raise ValueError(
            f"未知的 Tool：{function_call.name}"
        )
    print("Tool 執行結果：")
    print(result)
    #包裝執行的結果
    function_response = types.Part.from_function_response(
        name=function_call.name,
        response=result
    )
    #對話歷史
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=user_prompt
                )
            ]
        ),

        response.candidates[0].content,

        types.Content(
            parts=[
                function_response
            ]
        )
    ]
    #把Tools的答案送回給Gemini   這段才是真正發API Request
    final_response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=contents,
        config=types.GenerateContentConfig(
            tools=[tool],
            system_instruction="""
            只有当使用者的问题明确需要某个工具时才调用工具。
            如果是一般知识、闲聊或与现有工具无关的问题，
            请直接回答，不要为了使用工具而勉强选择工具。
            """
        )
    )
else :
    print("Gemini 不需要使用到Tools ", response.text)


