<h1 align="center" style="font-weight: bold !important">⚡️🎙 cln-podcast-payments</h1>

<p align="center">
  A <a href="https://blockstream.com/lightning">Core Lightning</a> plugin to work with <a href="https://github.com/lightning/blips/blob/master/blip-0010.md">streaming payments, boosts, and boostagrams</a> for <a href="https://value4value.info/">Podcasting 2.0</a>.
</p>

---

This is a simple plugin for Core Lightning that enables you to extract [podcast payment metadata](https://github.com/lightning/blips/blob/master/blip-0010.md") received from podcasting apps such as [Breez](https://breez.technology) or [Fountain](https://www.fountain.fm).

## 💡 Why

Core Lightning currently doesn't persist arbitrary TLVs such as [the ones](https://github.com/lightning/blips/blob/master/blip-0010.md) sent by Podcasting 2.0 apps.
This plugin is intended to provide a workaround until Core Lightning adds native support for this.
Keep an eye on https://github.com/ElementsProject/lightning/issues/4470 for more information

## 🏎 TL;DR

This plugin extends `lightning-cli` with a `podcastpayments` command that fetches past streams, boosts, and boostagrams received from Podcasting 2.0 apps.

``` shell
$ lightning-cli podcastpayments
{
   "count": 1,
   "payments": [
        {
            "label": "keysend-1664891872.800196000",
            "amount": "21000msat",
            "info": {
                "podcast": "Closing the Loop",
                "episode": "#01 - Gigi: Introduction to Closing the Loop",
                "action": "boost",
                "time": "00:00:31",
                "feedID": "4058673",
                "app_name": "Breez",
                "value_msat_total": "21000",
                "message": "yo!"
            }
        }
    ]
}
```

## 🔧 Installation

To run, the plugin needs Python 3 with [pyln-client](https://github.com/ElementsProject/lightning/tree/master/contrib/pyln-client) and [SQLAlchemy](https://www.sqlalchemy.org) installed.

``` shell
pip install pyln-client
pip install SQLAlchemy
```

Make sure those are installed in your Python environment.
Use a [virtual environment](https://docs.python.org/3/tutorial/venv.html) to not bloat your global Python installation.

Then, to activate the plugin:

1️⃣ _Clone this repo:_

``` shell
git clone https://github.com/cnixbtc/cln-podcast-payments.git
```


2️⃣ _Run `lightningd` with the `--plugin` option and specify the path to `podcast_payments.py`:_

``` shell
lightningd --plugin=/path/to/cln-podcast-payments/podcast_payments.py
```

More information on `lightningd` plugins can be found [in the docs](https://lightning.readthedocs.io/PLUGINS.html).

## 💻 Usage

Once installed, the plugin will run in the background and persist all podcast payment information to a local sqlite3 database.
More specifically, it will persist all TLV values with type `7629169` according to [bLIP 10](https://github.com/lightning/blips/blob/master/blip-0010.md).
The location of this database can be controlled using the optional `--podcastpayments-dir` option on `lightningd`:

``` shell
lightningd --plugin=/path/to/cln-podcast-payments/podcast_payments.py --podcastpayments-dir=/path/to/desired/db/location
```

By default, the database will be in: `$HOME/.lightning/bitcoin/podcast-payments`.

⚠️ Because TLVs are not persisted by Core Lightning, the plugin will only be able to persist payment information from payments that arrived after it was installed.
At the moment, there's no way to access payment information associated with historical payments.
This might change in the future, though. For more information see https://github.com/ElementsProject/lightning/issues/4470.

### Extract Payment Information: `podcastpayments`

This command fetches all podcast payment information that was persisted in the database since running the plugin.
The value of the `info` property may change depending on what the value of the corresponding TLV that was sent by the Podcasting 2.0 app.

``` shell
$ lightning-cli podcastpayments
{
   "count": 1,
   "payments": [
        {
            "label": "keysend-1664891872.800196000",
            "amount": "21000msat",
            "info": {
                "podcast": "Closing the Loop",
                "episode": "#01 - Gigi: Introduction to Closing the Loop",
                "action": "boost",
                "time": "00:00:31",
                "feedID": "4058673",
                "app_name": "Breez",
                "value_msat_total": "21000",
                "message": "yo!"
            }
        }
    ]
}
```
