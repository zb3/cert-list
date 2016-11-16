# cert-list
is an **experimental** set of small tools to fetch domain names from Certificate Transparency logs.

It uses parts of code from [catlfish](https://git.nordu.net/catlfish.git), see `LICENSE_CATLFISH`.

You probably want to use [ct-tools](https://github.com/tomrittervg/ct-tools) instead, because cert-list downloads only domain names, not whole certificates.

Once again, this is experimental, it doesn't handle failures, so don't rely on it.

## Let's go

To run this, you'll need:
* Python2 (b'coz'...)
* PyOpenSSL
* Bash or something else

FOA, you'll need to make `python2` execute python 2 (archlinux rocks), or change this to `python` in `updlog.py`.

## Get a particular range

```
python2 get.py [start] [howmany <= 1000] [ct_log_url]
```

As you can see, there's a header row that contains ID of that certificate in a given CT log URL, validity period and organization name if this is an Extended Validity certificate.
Then there are domains/emails (alternate names included, but www is skipped), and finally a blank line after each certificate.

## Get all new domain names 

`updlog.py` reads the `last-id` folder to check where to start for a given CT log URL (or more precisely, only the `[a-z0-9]` part of that URL). After everything downloaded, it writes the tree size into that folder, so that when you run it next time, it will only fetch new domains.

```
python2 updlog.py [ct_log_url] [num_threads=1] [optional_force_start_from]
```

* Things will get saved in the `curr` folder.
* Each thread writes (appends) to it's own file.
* This will not check for duplicate entries.
* If something goes wrong in one thread, it doesn't affect others.

## Filter saved files

`filter.py` supports `--valid` option that will discard all expired certificates, and `--ev` option to discard all certificates that aren't EV (EV OID's list taken from Chromium source code).

```
python2 filter.py --ev
```
```
python2 filter.py --valid
```

By default, that tool will filter logs in the `curr` folder and save filtered logs into the `filtered` folder but that can be changed:
```
python2 filter.py --valid --dirname='current' --destdirname='f11t3r3d'
```