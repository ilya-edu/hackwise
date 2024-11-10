import ngrok, os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
from flask import Flask, request, jsonify, make_response

# Настройка ngrok для создания туннеля
os.environ["NGROK_AUTHTOKEN"] = ""
listener = ngrok.forward(5002, authtoken_from_env=True)

# Определение имени модели
MODEL_NAME = "microsoft/Phi-3-medium-128k-instruct"

# Инициализация Flask приложения
app = Flask(__name__)

# Загрузка модели с оптимизациями для эффективного использования памяти
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    load_in_4bit=True,
    torch_dtype=torch.bfloat16,
    device_map="auto"
)

# Перевод модели в режим оценки (отключение обучения)
model.eval()

# Загрузка токенизатора и конфигурации генерации
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
generation_config = GenerationConfig.from_pretrained(MODEL_NAME)

@app.route('/generate', methods=['POST'])
def generate_response():
    # Получение данных из POST запроса
    data = request.get_json()
    system_prompt = data.get('system_prompt', '')
    query = data.get('query', '')

    # Формирование промпта с использованием шаблона чата
    prompt = tokenizer.apply_chat_template([{
        "role": "assistant",
        "content": system_prompt
    }, {
        "role": "user",
        "content": query
    }], tokenize=False, add_generation_prompt=True)
    
    # Вывод промптов для отладки
    print(system_prompt)
    print(query)
    
    # Токенизация входных данных и перемещение на устройство модели
    data = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)
    data = {k: v.to(model.device) for k, v in data.items()}

    # Генерация ответа
    output_ids = model.generate(**data, generation_config=generation_config, max_new_tokens=2048)[0]
    output_ids = output_ids[len(data["input_ids"][0]):]
    output = tokenizer.decode(output_ids, skip_special_tokens=True).strip()
    
    # Вывод результата для отладки
    print(output)

    # Формирование и отправка ответа
    response = make_response(jsonify({'output': output}))
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return output

# Запуск Flask приложения
app.run(host='0.0.0.0', port=5002)