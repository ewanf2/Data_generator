FROM python
WORKDIR /app
COPY App.py /app
COPY requirements.txt /app
COPY entrypoint.sh /entrypoint.sh
COPY functions.py /app
RUN pip install --no-cache-dir -r requirements.txt



EXPOSE 80

RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
