FROM python

ADD . .

RUN pip install clang
RUN pip install libclang

CMD ["python", "./main.py"]