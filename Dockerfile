FROM python
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt


#VOLUME  ["/app/schemas"]
EXPOSE 80
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
#CMD ["waitress-serve", "--listen=0.0.0.0:80", "App:App"]