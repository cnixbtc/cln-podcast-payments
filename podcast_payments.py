#!/usr/bin/env python3

import json
from pathlib import Path

from pyln.client import Plugin, LightningRpc
from sqlalchemy import Column, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

plugin = Plugin()
Base = declarative_base()

class PodcastPayment(Base):
    __tablename__ = "podcast_payments"

    label = Column(String, primary_key=True)
    amount = Column(String)
    info = Column(String)

    def to_json(self):
        return {
            'label': self.label,
            'amount': self.amount,
            'info': json.loads(self.info)
        }

@plugin.init()
def init(options, configuration, plugin):
    db_dir = options["podcastpayments-dir"]

    Path(db_dir).mkdir(parents=True, exist_ok=True)

    engine = create_engine("sqlite:///{}/podcast-payments.db".format(db_dir))
    Base.metadata.create_all(engine)

    plugin.engine = engine

@plugin.hook("invoice_payment")
def on_invoice_payment(payment, plugin, **kwargs):
    defer_processing = {"result": "continue"}

    if not "extratlvs" in payment or len(payment["extratlvs"]) < 1:
        return defer_processing

    # see https://github.com/lightning/blips/blob/master/blip-0010.md
    podcast_payment_infos = [
        tlv["value"] for tlv in payment["extratlvs"] if tlv["type"] == 7629169
    ]

    if len(podcast_payment_infos) != 1:
        return defer_processing

    podcast_payment_info_bytes = bytes.fromhex(podcast_payment_infos[0])
    podcast_payment_info_string = podcast_payment_info_bytes.decode().strip()

    podcast_payment = PodcastPayment(
        label=payment["label"],
        amount=payment["msat"],
        info=podcast_payment_info_string,
    )

    with Session(plugin.engine) as session:
        with session.begin():
            session.add(podcast_payment)

    return defer_processing

@plugin.method("podcastpayments")
def podcast_payments(plugin, **kwargs):
    """Lists all podcast payments received since running this plugin.

    A podcast payment is a payment that includes a TLV of type 7629169.
    See https://github.com/lightning/blips/blob/master/blip-0010.md for details.
    """
    with Session(plugin.engine) as session:
        return {
            'count': session.query(PodcastPayment).count(),
            'payments': session.query(PodcastPayment).all()
        }

@plugin.method("podcastboost")
def podcastboost(
    plugin,
    destination,
    amount_msat,
    payment_info,
    rpcfile="$HOME/.lightning/bitcoin/lightning-rpc",
):
    """Send a podcast payment.
    """
    l = LightningRpc(rpcfile)

    l.keysend(destination,
              amount_msat=amount_msat,
              extratlvs={7629169: json.dumps(payment_info).encode().hex()})

    return {
        'destination': destination,
        'amount_msat': amount_msat,
        'payment_info': payment_info
    }

plugin.add_option(
    "podcastpayments-dir",
    "$HOME/.lightning/bitcoin/podcast-payments",
    "Directory where boostagrams will be stored.",
)

plugin.run()
