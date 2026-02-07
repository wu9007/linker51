import os, json, requests
from openai import OpenAI
from dotenv import load_dotenv

class DeepSeekCommander:
    def __init__(self):
        load_dotenv()
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        )
        self.gateway_url = "http://127.0.0.1:5001/v1"

    def dispatch(self, query: str):
        # 1. 定义工具能力 (符合向后扩展的宏观设计)
        tools = [{
            "type": "function",
            "function": {
                "name": "switch_color",
                "description": "变更视觉追踪的目标颜色",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "color": {"type": "string", "enum": ["yellow", "green", "blue", "red"]}
                    },
                    "required": ["color"]
                }
            }
        }]

        # 2. 获取决策
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个精准的机械臂指挥官。"},
                {"role": "user", "content": query}
            ],
            tools=tools
        )

        message = response.choices[0].message

        # 3. 执行工具序列
        if message.tool_calls:
            execution_results = []
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                if func_name == "switch_color":
                    color = args.get('color')
                    try:
                        # 宏观设计：通过 API 实现进程间解耦
                        res = requests.post(f"{self.gateway_url}/vision/color", json={"color": color}, timeout=3)
                        execution_results.append(f"硬件响应: {res.json().get('message', 'OK')}")
                    except Exception as e:
                        execution_results.append(f"链路错误: {e}")

            # 如果有工具执行，返回执行结果总结
            return "\n".join(execution_results)

        # 如果没有工具调用（普通对话），返回 AI 的文字回复
        return message.content

if __name__ == "__main__":
    # 初始化大脑
    try:
        brain = DeepSeekCommander()
    except Exception as e:
        print(f"初始化失败: {e}")
        exit(1)

    while True:
        try:
            # 获取用户输入
            user_input = input("\n指令 >> ").strip()
            # 退出判定
            if not user_input:
                continue
            if user_input.lower() in ['exit', 'quit', 'q']:
                print("正在关闭...")
                break
            # 调度执行
            print("思考中...")
            result = brain.dispatch(user_input)
            # 反馈结果
            print(f"响应: {result}")
        except KeyboardInterrupt:
            print("\n\n强制退出...")
            break
        except Exception as e:
            print(f"发生未知错误: {e}")