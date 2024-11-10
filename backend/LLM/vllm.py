import ngrok, os
from flask import Flask, request, jsonify, make_response
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

# Настройка ngrok для создания туннеля
os.environ["NGROK_AUTHTOKEN"] = ""
listener = ngrok.forward(5002, authtoken_from_env=True)

# Определение имени модели
MODEL_NAME = "microsoft/Phi-3-medium-128k-instruct"

# Инициализация Flask приложения
app = Flask(__name__)

# Настройка параметров сэмплирования для генерации текста
sampling_params = SamplingParams(temperature=0.0001, max_tokens=2048)

# Инициализация модели LLM
llm = LLM(model=MODEL_NAME, tensor_parallel_size=2)

# Загрузка токенизатора
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

@app.route('/generate', methods=['POST'])
def generate_response():
    # Получение данных из POST запроса
    data = request.get_json()
    system_prompt = data.get('system_prompt', '')
    query = data.get('query', '')

    # Формирование промпта с использованием шаблона чата
    prompt = tokenizer.apply_chat_template([{
        "role": "system",
        "content": system_prompt
    }, {
        "role": "user",
        "content": query
    }], tokenize=False, add_generation_prompt=True)
    
    # Генерация ответа с использованием модели
    output = llm.generate(prompt, sampling_params)
    output = output[0].outputs[0].text

    # Формирование и отправка ответа
    response = make_response(jsonify({'output': output}))
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return output

# Запуск Flask приложения
app.run(host='0.0.0.0', port=5002)