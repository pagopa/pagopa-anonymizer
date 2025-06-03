FROM python:3.11@sha256:68a8863d0625f42d47e0684f33ca02f19d6094ef859a8af237aaf645195ed477

WORKDIR /app
COPY . /app
RUN pip install --upgrade pip && pip install -r requirements.txt
CMD ["python", "-u", "src/app.py"]


