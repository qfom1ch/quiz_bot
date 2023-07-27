FROM python:3.10

RUN mkdir /quiz_bot

WORKDIR /quiz_bot

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD python bot.py
