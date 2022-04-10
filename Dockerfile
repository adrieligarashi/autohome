FROM python:3.7

WORKDIR /autohome

COPY autohome/main_site.py autohome/main_site.py
COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

EXPOSE 8501 50057 53939 53940 53941

COPY . /autohome

ENTRYPOINT ["streamlit", "run", "autohome/main_site.py", "--server.port=8501", "--server.address=0.0.0.0"]

#ENTRYPOINT ["python", "-m"]

# CMD python -m http.server 8000
