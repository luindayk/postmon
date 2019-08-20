#!/usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import timedelta
from celery import Celery
from celery.utils.log import get_task_logger
from IbgeTracker import IbgeTracker
import PackTracker
from database import MongoDb as Database
import os

USERNAME = os.environ.get('POSTMON_DB_USER')
PASSWORD = os.environ.get('POSTMON_DB_PASSWORD')
HOST = os.environ.get('POSTMON_DB_HOST', 'localhost')
PORT = os.environ.get('POSTMON_DB_PORT', '27017')

if all((USERNAME, PASSWORD)):
    broker_conn_string = 'mongodb://%s:%s@%s:%s' \
        % (USERNAME, PASSWORD, HOST, PORT)
else:
    broker_conn_string = 'mongodb://%s:%s' % (HOST, PORT)

print(broker_conn_string)

app = Celery('postmon', broker=broker_conn_string)

app.conf.update(
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_TIMEZONE='America/Sao_Paulo',
    CELERY_ENABLE_UTC=True,
    CELERYBEAT_SCHEDULE={
        'track_ibge_daily': {
            'task': 'PostmonTaskScheduler.track_ibge',
            'schedule': 900, #timedelta(days=1)  # útil para
                                           # testes: timedelta(minutes=1)
        },
        'track_packs': {
            'task': 'PostmonTaskScheduler.track_packs',
            'schedule': 60, #timedelta(hours=1),
        }

    }
)

logger = get_task_logger(__name__)


@app.task
def track_ibge():
    logger.info('Iniciando tracking do IBGE...')
    db = Database()
    ibge = IbgeTracker()
    ibge.track(db)
    logger.info('Finalizou o tracking do IBGE')


@app.task
def track_packs():
    logger.info('Iniciando tracking de pacotes...')
    db = Database()
    runTask = PackTracker.correios_check()
    print('runTask: ' + str(runTask))
    if runTask:
        for obj in db.packtrack.get_all():
            provider = obj['servico']
            track = obj['codigo']
            changed = PackTracker.run(provider, track)
            if changed:
                PackTracker.report(provider, track)

    logger.info('Finalizou o tracking de pacotes')
