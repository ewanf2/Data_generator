FROM python
WORKDIR /app
COPY App.py  /app
COPY requirements.txt /app
RUN pip install -r requirements.txt


#VOLUME  ["/app/schemas"]
EXPOSE 80
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
