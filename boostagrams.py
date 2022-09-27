#!/usr/bin/env python3

import json
import sqlite3
import sqlalchemy as db
from pathlib import Path
from pyln.client import Plugin

plugin = Plugin()

@plugin.hook("invoice_payment")
def on_invoice_payment(payment, **kwargs):
    with open(plugin.boostagram_file, "a") as f:
        f.write("{},{},{}\n".format(payment["label"], payment["msat"], json.dumps(payment["extratlvs"])))

    return {"result": "continue"}


@plugin.init()
def init(options, configuration, plugin):
    boostagram_file = f'{options["boostagram-dir"]}/boostagrams.csv'

    path = Path(boostagram_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

    plugin.boostagram_file = boostagram_file 

plugin.add_option('boostagram-dir', '$HOME/.lightning/bitcoin/boostagrams', 'Directory where boostagrams will be stored.')

plugin.run()
