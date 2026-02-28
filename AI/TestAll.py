# _*_ coding: utf-8 _*_
# @Time : 2026/2/25 星期三 10:32
# @Author : 韦丽
# @Version: V 1.0
# @File : TestAll.py
# @desc :
from AI.LLMService import LLMService
from AI.RAGService import RAGService
import os
from openai import OpenAI

# 初始化服务
rag_service = RAGService()
llm_service = LLMService("sk-6396cd26c2204d5b8854c4b2e5ac0eec")

# 模拟加载文档
sample_docs = [
    "博物三个常设展厅：古代文明展、近代历史展和民俗文化展。",
    "特展'丝绸之馆开放时间为每周二至周日9:00-17:00，周一闭馆。",
    "本馆共有路'将于下月开幕，展出珍贵文物120件。",
    "博物馆提供免费讲解服务，每日上午10点和下午2点各一场。",
    "馆内设有咖啡厅和纪念品商店，位于一楼大厅西侧。"
]
rag_service.add_documents(sample_docs)

if __name__ == '__main__':
    # 生成回答
    # answer = llm_service.generate_answer("访问成功没有？", "")
    from openai import OpenAI
    import os

    # 初始化OpenAI客户端
    client = OpenAI(
        # 如果没有配置环境变量，请用阿里云百炼API Key替换：api_key="sk-xxx"
        # api_key=os.getenv("DASHSCOPE_API_KEY"),
        api_key= "sk-6396cd26c2204d5b8854c4b2e5ac0eec",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    messages = [{"role": "user", "content": "你是谁， 能做什么？我现在是一个没有工作的软件工程师，如何在2026年找到工作？"}]
    completion = client.chat.completions.create(
        model="deepseek-v3.2",
        messages=messages,
        # 通过 extra_body 设置 enable_thinking 开启思考模式
        extra_body={"enable_thinking": True},
        stream=True,
        stream_options={
            "include_usage": True
        },
    )

    reasoning_content = ""  # 完整思考过程
    answer_content = ""  # 完整回复
    is_answering = False  # 是否进入回复阶段
    print("\n" + "=" * 20 + "思考过程" + "=" * 20 + "\n")

    for chunk in completion:
        if not chunk.choices:
            print("\n" + "=" * 20 + "Token 消耗" + "=" * 20 + "\n")
            print(chunk.usage)
            continue

        delta = chunk.choices[0].delta

        # 只收集思考内容
        if hasattr(delta, "reasoning_content") and delta.reasoning_content is not None:
            if not is_answering:
                print(delta.reasoning_content, end="", flush=True)
            reasoning_content += delta.reasoning_content

        # 收到content，开始进行回复
        if hasattr(delta, "content") and delta.content:
            if not is_answering:
                print("\n" + "=" * 20 + "完整回复" + "=" * 20 + "\n")
                is_answering = True
            print(delta.content, end="", flush=True)
            answer_content += delta.content


