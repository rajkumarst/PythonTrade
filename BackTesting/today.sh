#!/usr/bin/env sh

python2.7 Open-Equal-Low.py --today --varience Always-Buy --profit 1 --sl 0.5 --verbose > out.today.always-buy.$$
python2.7 Open-Equal-Low.py --today --varience Both-Buy-And-Sell --profit 1 --sl 0.5 --verbose > out.today.Both.$$
python2.7 Open-Equal-Low.py --today --varience Go_with_Nifty --profit 1 --sl 0.5 --verbose > out.today.Nifty.$$
