import platform
import pprint
import re
import sys
from hashlib import sha256
from typing import Optional

import requests
from flask import current_app
from flask import jsonify
from framework.auth.token import token_handler
from framework.commons.hex import *
from framework.commons.hex import h2h
from varname import nameof, argname, varname

import config
from framework.commons.logger import logger
from pygments import highlight, lexers, formatters


def nth_obj(rx: list[dict[str, object]] = [], obj: Optional[str] = '', n: Optional[int] = 0):
    return rx[n][obj] if (
            len(rx) > n
            and obj in rx[n]
            and rx[n][obj]
    ) else None


def first_obj(rx: list[dict[str, object]] = [], obj: Optional[str] = ''):
    return nth_obj(rx=rx, obj=obj)


def first_rx(rx, mx: Optional[str] = None, ax: Optional[str] = None):
    if rx and len(rx) > 0:
        # logger.debug(f'{mx} -> {ax}: {rx.json[0]}')
        if isinstance(rx, list):
            r = rx[0]
        else:
            # logger.debug(f'{mx} -> {ax}: {type(rx.json)}')
            r = rx
    else:
        # logger.debug(f'{mx} -> {ax}: null')
        r = None
    if mx and ax:
        # logger.info(f'{mx} -> {ax}: {rx}')
        logger.debug(f'{mx} -> {ax}: {r}')
    return r


def lower_rx(rx, mx: Optional[str] = None):
    if rx and isinstance(rx, list):
        rx = [lower_rx(rq) for rq in rx]
    elif rx and isinstance(rx, dict):
        rx = {**{k.lower(): lower_rx(v) for k, v in rx.items()}}
    else:
        pass
    if mx:
        logger.debug(f'{mx} -> rx: {rx}')
    return rx


def lower_req(request, mx: Optional[str] = None):
    req = request.json if (request and request.json) else {}
    rx = lower_rx(req)
    if mx:
        logger.debug(f'{mx} -> rx: {rx}')
    return rx


def lower_res(request, mx: Optional[str] = None):
    req = request.json() if (request and request.json()) else {}
    rx = lower_rx(req)
    if mx:
        logger.debug(f'{mx} -> rx: {rx}')
    return rx


def get_one_safe(mx=None, ax=None, a=None, s=None, d=None, e=False):
    r = a.get(s, d)
    if e:
        try:
            r = eval(r)
        except Exception as e:
            r = d
            logger.warn(f'{mx} -> {ax}[{s}]: {r}')
    return r


def get_safe(a=None, *s, d: Optional = None, e: Optional[bool] = False, mx: Optional[str] = None,
             ax: Optional[str] = None):
    if isinstance(a, dict):
        r = get_one_safe(mx=mx, ax=ax, a=a, s=s[:1][0], d=d, e=e)
        if len(s) > 1 and isinstance(r, dict):
            if r != {}:
                r = get_safe(r, s[1:][0], d=d, e=e, mx=mx, ax=ax)
            else:
                r = d
    else:
        r = None
    if mx and ax:
        logger.debug(f'{mx} -> {ax}{"".join([f"[{q}]" for q in s])}: {r}')
        # logger.debug(highlight(f'{mx} -> {ax}[{s}]: {r}', lexers.JsonLexer(), formatters.TerminalFormatter()))
        # pprint.plogger.debug(f'{mx} -> {ax}[{s}]: {r}', indent=4, width=1024)
        pass
    return r


def rfile(f: Optional[str] = None, n: Optional[int] = 256):
    with open(f, mode="rb") as frb:
        rb = frb.read()
    rs = [b2h(rb[i:(i + n)]) for i in range(0, len(rb), n)]
    ks = sha256(rb).hexdigest()
    hs = []
    ds = []
    x = 0
    for rx in rs:
        hs.append('00 d6 %04x' % (n * x))
        ds.append(rx)
        # logger.debug(tlv(hs[x], ds[x]))
        x += 1
    return hs, ds, ks


def reb(v):
    match v:
        case bytes(_):
            v = b2h(v)
        case int(_):
            v = i2h(v)
        case _:
            v = v
    return v


def walk(node):
    if type(node) is dict:
        return {k: walk(v) for k, v in node.items()}
    elif type(node) is list:
        return [walk(x) for x in node]
    else:
        return reb(node)


def replace_var(match):
    return f'{match.group(0)}'


def tlv(t: Optional[str] = None, s: Optional[str] = None, ber=None, ):
    if not s or s == 'None' or s is None:
        return None
    t = h2h(t or '')
    bx = ber if ber is not None else ber or len(t) > 2
    if ber is not None:
        bx = ber
    return ' '.join([t, lhh(hex=s, ber=bx), h2h(s)]).strip()


def btlv(t: Optional[str] = None, s: Optional[str] = None):
    return tlv(t, s, ber=True)


def apdu_header_expand(header='00 00 00 00'):
    bcmd = h2b(header)[:4]
    if len(bcmd) > 3:
        try:
            cla = b2h(bcmd[0:1])
            ins = b2h(bcmd[1:2])
            p1p2 = b2h(bcmd[2:4])
            return cla, ins, p1p2
        except:
            return None, None, None
    else:
        return None, None, None


def apdu_header_compact(cla, ins, p1p2):
    return '%s %s %s' % (cla, ins, p1p2)


def apdu_expand(apdu='00 00 00 00'):
    bcmd = h2b(apdu)
    lx = len(bcmd)
    if lx < 4:
        return None, None, None
    cla, ins, p1p2 = apdu_header_expand(header=apdu)
    if cla is None:
        return None, None, None
    data = b''
    le = b''
    match lx:
        case 4:
            data = b''
            le = b''
        case 5:
            le = bcmd[4:5]
            data = b''
        case 6:
            le = b''
            data = bcmd[5:6]
        case _:
            match (lx > 7):
                case True:
                    i = h2i(m0h(apdu, 4, 7)) + 7
                    match (lx - i):
                        case 0:
                            data = bcmd[7:i]
                        case 1:
                            data = bcmd[7:i]
                            le = bcmd[:1]
                        case _:
                            j = h2i(m0h(apdu, 4, 5)) + 5
                            match (lx - j):
                                case 0:
                                    data = bcmd[5:j]
                                case 1:
                                    data = bcmd[5:j]
                                    le = bcmd[:1]
                                case _:
                                    return None, None, None

                case False:
                    j = h2i(m0h(apdu, 4, 5)) + 5
                    match (lx - j):
                        case 0:
                            data = bcmd[5:j]
                        case 1:
                            data = bcmd[5:j]
                            le = bcmd[:1]
                        case _:
                            return None, None, None
    return '%s %s %s' % (cla, ins, p1p2), b2h(data), b2h(le)


def apdu_compact(header='00 00 00 00', data='', le=''):
    # cla, ins, p1p2 = apdu_header_expand(header=header)
    lc = lhh(data)
    lc = lc if lc != '00' else ''
    return h2h(f'{header} {lc} {data} {le}')


def split_apdu(apdu, mx: Optional[str] = None, ax: Optional[str] = None):
    header, data, le = (None, None, None)
    if isinstance(apdu, dict) and all(key in apdu for key in ['header', 'data', 'le']):
        header = get_safe(apdu, 'header')
        data = get_safe(apdu, 'data')
        le = get_safe(apdu, 'le')
    else:
        if isinstance(apdu, str):
            header, data, le = apdu_expand(apdu)
    logger.debug(f'{mx} -> header: {header}, data: {data}, le: {le}')
    return header, data, le


def payload_colapse(apdu_commands: Optional[list[dict[str, object]]] = []):
    apdus = []
    if apdu_commands and len(apdu_commands) > 0:
        apdus = []
        for apdu in apdu_commands:
            if all(key in apdu for key in ['data', 'bypass']):
                apdus.append(apdu)
            if all(key in apdu for key in ['apdu', 'bypass']):
                load = get_safe(apdu, 'apdu', d={})
                if all(key in load for key in ['header', 'data', 'le']):
                    apdus.append({
                        'data': apdu_compact(
                            header=load['header'],
                            data=load['data'],
                            le=load['le']
                        ),
                        'bypass': apdu['bypass']
                    })
    return apdus


def payload_expand(apdu_commands: Optional[list[dict[str, object]]] = []):
    apdus = []
    if apdu_commands and len(apdu_commands) > 0:
        apdus = []
        for apdu in apdu_commands:
            if all(key in apdu for key in ['data', 'bypass']):
                header, data, le = apdu_expand(get_safe(apdu, 'data', d=''))
                apdus.append({
                    'apdu': {'header': header, 'data': data, 'le': le},
                    'bypass': apdu['bypass']
                })
            if all(key in apdu for key in ['apdu', 'bypass']):
                load = get_safe(apdu, 'apdu', d={})
                if all(key in load for key in ['header', 'data', 'le']):
                    apdus.append({
                        'apdu': load,
                        'bypass': apdu['bypass']
                    })
    return apdus


def compose_apdu(rx, session, control_cmds, apdu_commands, encrypt=None, colapse: Optional[bool] = False):
    session['transaction-no'] = rx['transaction-no']
    if encrypt:
        session = session | {'encrypt': encrypt}
        if colapse:
            apdu_commands = payload_colapse(apdu_commands)
    else:
        session.pop('encrypt', None)
        session.pop('logged-in', None)
        apdu_commands = payload_colapse(apdu_commands)
    return (
            {k: v for k, v in rx.items() if k not in ['control-responses', 'apdu-responses']} |
            {
                'transaction-no': session['transaction-no'],
                'card-no': get_safe(rx, 'card-no', d=''),
                'control-commands': control_cmds,
                'apdu-commands': apdu_commands,
                'session': str(session),
                'continue': len(control_cmds) > 0 or len(apdu_commands) > 0
            }
    )
