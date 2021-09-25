# ArbiBotter
ArbiBotter

1) INSTALL REDIS:

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

5) RUN arbibots_mints.py:

cd ArbiBotter

python arbibots_mints.py

6) RUN arbibotter.py:

still in the arbibotter directory, python arbibotter.py

###################################################################### 

PLEASE NOTE THAT IT CURRENTLY CHECKS MINT PRICE EVERY 10 SECONDS I DONT KNOW HOW THIS STACKS AGAINST ALCHEMY'S FREE COMPUTE LIMIT IM WORKING ON SETTING UP A PROPER WAITING MECHANISM THAT ONLY MAKES NECESSARY NODE CALLS. IM ALSO ADDING IN A NUMBER OF MINTS SEEN IN THE MEMPOOL WHERE IT PANICS AND MINTS AT THAT PRICE IF THE OPTION IS SET. 

######################################################################
