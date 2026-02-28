# _*_ coding: utf-8 _*_
# @Time : 2026/2/25 星期三 10:17
# @Author : 韦丽
# @Version: V 1.0
# @File : App.py
# @desc :

from flask import Flask, request, jsonify, Response

import threading
import queue
import json

from AI.ASRService import ASRService
from AI.LLMService import LLMService
from AI.RAGService import RAGService
from AI.TTSService import TTSService

app = Flask(__name__)

# 初始化服务
rag_service = RAGService()
llm_service = LLMService("sk-6396cd26c2204d5b8854c4b2e5ac0eec")
asr_service = ASRService("your-access-key-id", "your-access-key-secret", "your-app-key")
tts_service = TTSService("your-access-key-id", "your-access-key-secret", "your-app-key")

# 模拟加载文档
sample_docs = [
    "博物三个常设展厅：古代文明展、近代历史展和民俗文化展。",
    "特展'丝绸之馆开放时间为每周二至周日9:00-17:00，周一闭馆。",
    "本馆共有路'将于下月开幕，展出珍贵文物120件。",
    "博物馆提供免费讲解服务，每日上午10点和下午2点各一场。",
    "馆内设有咖啡厅和纪念品商店，位于一楼大厅西侧。"
]
rag_service.add_documents(sample_docs)


class StreamGenerator:
    def __init__(self, generator):
        self.generator = generator

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return next(self.generator)
        except StopIteration:
            raise StopIteration


@app.route('/api/query', methods=['POST'])
def query():
    data = request.json
    question = data.get('question', '')

    # 检索相关文档
    search_results = rag_service.search(question)
    context = '\n'.join([r['content'] for r in search_results])

    # 生成回答
    answer = llm_service.generate_answer(question, context)

    return jsonify({
        'answer': answer,
        'references': search_results
    })


@app.route('/api/query_stream', methods=['POST'])
def query_stream():
    data = request.json
    question = data.get('question', '')

    # 检索相关文档
    search_results = rag_service.search(question)
    context = '\n'.join([r['content'] for r in search_results])

    def generate():
        # 模拟流式输出
        answer = llm_service.generate_answer(question, context)
        words = answer.split(' ')
        for i, word in enumerate(words):
            yield f"data: {json.dumps({'token': word + (' ' if i < len(words) - 1 else ''), 'references': search_results if i == 0 else []})}\n\n"

    return Response(generate(), mimetype='text/plain')


@app.route('/api/speech_to_text', methods=['POST'])
def speech_to_text():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    audio_path = f"/tmp/{audio_file.filename}"
    audio_file.save(audio_path)

    try:
        text = asr_service.recognize_audio(audio_path)
        return jsonify({'text': text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/text_to_speech', methods=['POST'])
def text_to_speech():
    data = request.json
    text = data.get('text', '')
    output_file = f"/tmp/tts_output_{hash(text)}.wav"

    try:
        success = tts_service.synthesize_speech(text, output_file)
        if success:
            return jsonify({'audio_url': f'/audio/{output_file.split("/")[-1]}'})
        else:
            return jsonify({'error': 'Speech synthesis failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
