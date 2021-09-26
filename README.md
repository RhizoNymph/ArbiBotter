# ArbiBotter

#############################################################################

REDIS IS ONLY REQUIRED IF YOU WANT TO USE THE PANIC MINTING FEATURE

THIS FEATURE CHECKS FOR MINTS IN NEW BLOCKS AND KEEPS A COUNT.

IF YOU PASS IN A PANIC POINT AND A MAX PRICE AS THE EXTRA LAST 2 PARAMETERS,

IT WILL TRIGGER A MINT AT YOUR QUANTITY WHEN IT DETECTS THAT MANY MINTS

SINCE START OF THE ARBIBOTS_MINTS.PY SCRIPT.

IF YOU DO NOT WANT TO USE THIS, SIMPLY DONT PASS THESE PARAMETERS AND SKIP

TO STEP 5.

#############################################################################



1) INSTALL ARBIBOTTER AND REDIS:

git clone https://github.com/QuantNymph/ArbiBotter

wget http://download.redis.io/redis-stable.tar.gz

tar xvzf redis-stable.tar.gz

cd redis-stable

sudo make

sudo make install

2) EDIT REDIS.CONF:

Still in the redis-stable directory, open redis.conf in a text editor add: requirepass

3) RUN REDIS

redis-server redis.conf

4) SETUP CONFIG.CFG

copy sample_config.cfg to a file name config.cfg in it, add your arbitrum websocket node URL after arbitrum_wss (you can get a free node at https://www.alchemy.com/ and skip the payment option) 

add your wallet address after personal_address 

add your private key after private_key (make sure you keep config.cfg in the .gitignore) 

add your redis password after redis

5) Navigate to ArbiBotter directory:

cd ../

cd ArbiBotter

6) RUN arbibotter.py:

still in the arbibotter directory, 

python arbibotter.py MINT_PRICE QUANTITY 

or if you want to use the panic minting feature: 

python arbibots_mints.py &

python arbibotter.py MINT_PRICE QUANTITY PANIC_POINT MAX_PRICE

(the & causes the first script to run in the background, use:

pkill -f arbibots_mints.py


to kill the process)
