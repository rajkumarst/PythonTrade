#!/usr/bin/env sh

python2.7 Open-Equal-Low.today.py --varience Always-Buy --profit 1 --sl 0.5 --verbose > out.Always-buy.$$
python2.7 Open-Equal-Low.today.py --varience Both-Buy-And-Sell --profit 1 --sl 0.5 --verbose > out.Both.$$
python2.7 Open-Equal-Low.today.py --varience Go_with_Nifty --profit 1 --sl 0.5 --verbose > out.Nifty.$$
