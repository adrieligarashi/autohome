FROM tiangolo/uvicorn-gunicorn:python3.7

# WORKDIR /webflask

COPY . ./app

RUN apt-get update && apt-get upgrade -y
RUN apt-get install ffmpeg libsm6 libxext6 vim -y
RUN pip install -r ./app/requirements.txt

EXPOSE 8000
EXPOSE 80
EXPOSE 1883
EXPOSE 3002
EXPOSE 8080
#ENTRYPOINT ["streamlit", "run", "autohome/main_site.py", "--server.port=8501", "--server.address=0.0.0.0"]

#ENTRYPOINT ["python", "-m"]

# CMD gunicorn -k eventlet -b 0.0.0.0:5005 -w 1 app:app

WORKDIR /app/app

CMD gunicorn -k eventlet -w 1 -b 0.0.0.0:8000 autohome.app:app --log-file=- --timeout 600
