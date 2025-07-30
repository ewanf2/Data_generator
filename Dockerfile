FROM python
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
#VOLUME  ["/app/data"]
EXPOSE 80

CMD ["waitress-serve", "--listen=0.0.0.0:80", "App:App"]
