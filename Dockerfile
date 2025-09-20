FROM python:3.11-slim
WORKDIR /app

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt


COPY App.py functions.py ./
COPY entrypoint.sh /entrypoint.sh


RUN chmod +x /entrypoint.sh



EXPOSE 80

RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
