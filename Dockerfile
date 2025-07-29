FROM python
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

EXPOSE 5100
CMD ["python","App.py"]
