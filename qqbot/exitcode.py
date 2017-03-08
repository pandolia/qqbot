# -*- coding: utf-8 -*-

QSESSION_ERROR = 201
RESTART = 202
POLL_ERROR = 203
FETCH_ERROR = 204

def ErrorInfo(code):
    return {
        0:   'NO ERROR',
        201: 'QSESSION ERROR',
        202: 'RESTART',
        203: 'POLL ERROR',
        204: 'FETCH ERROR'
    }.get(code, 'UNKNOWN ERROR') + ('(code=%d)' % code)
