FROM python:3.11-bookworm

COPY requirements.txt /requirements.txt
COPY post_dr_comment.py /post_dr_comment.py

RUN pip install -r /requirements.txt

ENTRYPOINT [ "/post_dr_comment.py" ]
