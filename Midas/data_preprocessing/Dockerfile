FROM amancevice/pandas:latest

ADD requirements.txt ./requirements.txt

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r ./requirements.txt

COPY main.py ./main.py

ADD . .