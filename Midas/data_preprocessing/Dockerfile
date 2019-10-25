FROM daskdev/dask

ADD requirements.txt ./requirements.txt

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r ./requirements.txt

COPY main.py ./main.py
COPY train_transaction.csv ./train_transaction.csv
COPY train_identity.csv ./train_identity.csv

CMD ["python", "main.py"]
