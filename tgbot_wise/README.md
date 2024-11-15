# MediaWise telegram bot


Интеллектуальный помощник для поиска информации по агентской библиотеке материалов в виде бота для [Telegram](https://telegram.org/).

Бот разработан с целью упростить поиск.

## Основная функция бота WiseSearchMate:

Бот был создан чтобы пользователи могли быстро и удобно получать ссылки внтри материалов или продолжать взаимодействие прямо в Telegram. По сути, он является связующим звеном между пользователем и системой, предоставляя простой и интуитивно понятный интерфейс для поиска.

## Интеграция с системой агенства:

Бот полностью интегрирован с внутренней системой. Для этого мы использовали два ключевых подхода:

1. **REST API** — для передачи данных между ботом и сервером системы. Это позволяет боту отправлять запросы и получать структурированные ответы от системы.
2. **WebSocket** — для обеспечения квази-реалтайм работы. Это значит, что бот почти мгновенно получает и отправляет ответы и обновления с сервера, что делает взаимодействие с пользователем более быстрым и удобным.

### Основные возможности бота:
1. **Задать вопрос и получить ответ с ссылками в материалах**:
   - Пользователь может использовать бота, чтобы задать любой запрос по материалам. Запрос передаётся в систему, где автоматизированная система обработки запросов (в зависимости от режима работы) отвечает на него. Ответы возвращаются пользователю прямо в чат с ботом.

2. **Начало или продолжение обращения**:
   - Бот позволяет не только начать новый запрос, но и продолжить ранее начатый диалог. Мы реализовали поддержку [**deep linking**](https://core.telegram.org/bots/features#deep-linking), что даёт возможность пользователю вернуться к конкретному обращению через специальную ссылку — это облегчает процесс взаимодействия и сохраняет контекст общения.

3. **Оценка качества оказанной помощи**:
   - После получения ответа пользователь может оценить оказанную помощь с помощью **inline кнопок** прямо в сообщении с ответом. Эти оценки интегрируются с нашей системой, что помогает нам отслеживать качество работы автоматизированной системы.

## Установка:

### [uv](https://docs.astral.sh/uv/)

```sh
uv venv

source .venv\bin\activate # Linux
.venv\Scripts\activate # Windows

uv sync
```

### pip

```sh
python -m venv .venv

source .venv\bin\activate # Linux
.venv\Scripts\activate # Windows

pip install -r requirements.txt
```

## Файл `.env`

Для запуска требуется создать файл с основными параметрами конфигурации.

> Токен бота можно получить у [Bot Father](https://t.me/BotFather).

Пример:

```ini
BOT_TOKEN = "111111111:AAHFDHDau_jgzLnputjY" # Токен бота
LEVEL = "DEBUG" # Уровень логирования
WEB_URL = "https://rag.server.ru" # URL фронта системы
API_URL = "https://rag-api.server.ru" # URL API системы
WS_URL = "wss://rag-api.server.ru" # URL WebSocket системы
```


## Запуск:

### Локально

```sh
uv run main.py
```

> Можно запускать и без команду `uv run` при активированном окружении, либо установке через `pip`.

```sh
python main.py
```

### Docker

#### Запуск

1. Собрать Docker-образ:

```sh
docker build -t имя_образа .
```

2. Когда образ собран, запустить контейнер на основе образа:

```sh
docker run --name имя_контейнера имя_образа
```

#### Остановка и удаление

Если нужно остановить контейнер:

```sh
docker stop имя_контейнера
```

Если нужно удалить контейнер:

```sh
docker rm имя_контейнера
```

Если нужно удалить образ:

```sh
docker rmi имя_образа
```
