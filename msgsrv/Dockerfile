FROM python:3.9 as fat
COPY requirements.txt .
RUN pip install --user -r requirements.txt
FROM python:3.9-slim
EXPOSE 5000
WORKDIR /msgsrv
COPY main.py /msgsrv
COPY requirements.txt /msgsrv
COPY --from=fat /root/.local /root/.local
RUN apt-get update && apt-get install -y libmariadb-dev

CMD python main.py
