# Mastodon
Scripts for making Mastodon more manageable.
First up, Defed.py is from user @clarjon1@wireless.cat6.network and I took his example from here https://clarjon1.com/blog/mastodon-defederation-tool and tweaked it to work with a CSV that you give it. Or if you run NewDefed you can download a specific blocklist from Codeberg and update your site using that.

python Defed.py csvfilename.csv
python NewDefed.py unified_tier0_blocklist

Added a .json file that can store your key and instance domain. I made it so it can load up lists from Oliphant, available here. https://codeberg.org/oliphant/blocklists/

Enjoy
