FROM public.ecr.aws/docker/library/python:3.10

EXPOSE 8080
WORKDIR /workspace
COPY . /workspace

RUN pip install --no-cache-dir -r requirements.txt
RUN python --version

CMD ["python", "app/app.py"]