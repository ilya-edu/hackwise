import transformers
import pandas as pd

# Читаем CSV файл
df = pd.read_csv('article_2024-07-06_16h13m47.csv')

# Функция для разбиения текста на куски
def split_text(text, chunk_size=2000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# Применяем функцию к колонке 'Content' и создаем новый DataFrame
result = df['Content'].apply(split_text).explode().reset_index()

# Переименовываем колонки
result.columns = ['Original_Index', 'Content_Chunk']

# Добавляем номер чанка
result['Chunk_Number'] = result.groupby('Original_Index').cumcount() + 1

result = result.merge(df.drop('Content', axis=1), left_on='Original_Index', right_index=True)

# Сохраняем результат в новый CSV файл
result.to_csv('output_file.csv', index=False)



