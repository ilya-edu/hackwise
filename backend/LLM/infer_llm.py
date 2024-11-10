import ngrok, os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig, BitsAndBytesConfig
from flask import Flask, request, jsonify, make_response
import json

# Настройка ngrok для создания туннеля
os.environ["NGROK_AUTHTOKEN"] = ""
listener = ngrok.forward(5002, authtoken_from_env=True)


MODEL_NAME = "Vikhrmodels/Vikhr-Nemo-12B-Instruct-R-21-09-24"

# Инициализация Flask приложения
app = Flask(__name__)

bnb_config = BitsAndBytesConfig(
   load_in_8bit=True,
)

# Загрузка модели с оптимизациями для эффективного использования памяти
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    torch_dtype=torch.bfloat16,
    device_map="cuda:0"
)

# Перевод модели в режим оценки (отключение обучения)
model.eval()

# Загрузка токенизатора и конфигурации генерации
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
generation_config = GenerationConfig.from_pretrained(MODEL_NAME)

GROUNDED_SYSTEM_PROMPT = "Your task is to answer the user's questions using only the information from the provided documents. Give two answers to each question: one with a list of relevant document identifiers and the second with the answer to the question itself, using documents with these identifiers."

@app.route('/generate', methods=['POST'])
def generate_response():
    try:
        data = request.get_json()
        system_prompt = data.get('system_prompt', '')
        query = data.get('query', '')
        documents = data.get('documents', [])

        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        if not documents:
            return jsonify({'error': 'Documents are required'}), 400

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "documents", "content": json.dumps(documents, ensure_ascii=False)},
            {"role": "user", "content": query}
        ]
        sample_messages = [
    {'role': 'system', 'content': GROUNDED_SYSTEM_PROMPT}, 
    {'role': 'documents', 'content': json.dumps(documents, ensure_ascii=False)},
    {'role': 'user', 'content': query}
        ]
        sample_prompt = tokenizer.apply_chat_template(
            sample_messages,
            tokenize=False,
            add_generation_prompt=True
        )
        sample_inputs = tokenizer(
            sample_prompt,
            return_tensors="pt",
            add_special_tokens=False,
            padding=True,
            truncation=True
        )
        sample_inputs = {k: v.to(model.device) for k, v in sample_inputs.items()}

        with torch.no_grad():
            sample_output_ids = model.generate(
                **sample_inputs,
                generation_config=generation_config,
                temperature=0.3,
                max_new_tokens=2048,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id
            )[0]
            
        sample_output_ids = sample_output_ids[len(sample_inputs["input_ids"][0]):]
        sample_output = tokenizer.decode(sample_output_ids, skip_special_tokens=True).strip()
        sample_output_json = json.loads(sample_output)
        relevant_doc_ids = sample_output_json.get('relevant_doc_ids', [])
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        
        print(f"System prompt: {system_prompt}")
        print(f"docs: {documents}")
        print(f"Query: {query}")
        
        inputs = tokenizer(
            prompt,
            return_tensors="pt",
            add_special_tokens=False,
            padding=True,
            truncation=True
        )
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        # Генерация ответа
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                generation_config=generation_config,
                temperature=0.3,
                max_new_tokens=2048,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id
            )[0]
            
        output_ids = output_ids[len(inputs["input_ids"][0]):]
        output = tokenizer.decode(output_ids, skip_special_tokens=True).strip()

        print(f"Generated output: {output}")

        response = make_response(jsonify({
            'output': output,
            'relevant': relevant_doc_ids
        }))
        response.headers["Content-Type"] = "application/json; charset=utf-8"
        return response

    except Exception as e:
        print(f"Error during generation: {str(e)}")
        return jsonify({'error': str(e)}), 500

app.run(host='0.0.0.0', port=5002)