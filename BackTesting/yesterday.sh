#!/usr/bin/env sh

python2.7 Open-Equal-Low.py --yesterday --varience Always-Buy --profit 1 --sl 0.5 --verbose > out.yesterday.Always-buy.$$
python2.7 Open-Equal-Low.py --yesterday --varience Both-Buy-And-Sell --profit 1 --sl 0.5 --verbose > out.yesterday.Both.$$
python2.7 Open-Equal-Low.py --yesterday --varience Go_with_Nifty --profit 1 --sl 0.5 --verbose > out.yesterday.Nifty.$$
