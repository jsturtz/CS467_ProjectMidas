FROM python
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install numpy
RUN pip install cython
RUN pip install -r requirements.txt
COPY . /code/
