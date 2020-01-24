# Telegram Bot - EqualHash Pool

## Get Started

This Bot is mounted on Docker, so implementing it is very easy. You just need to have a database [MongoDB](https://hub.docker.com/_/mongo) and this container.

## Environment variables
Below you can see the Environment variables necessary for the operation of this container.

 - **$TELEGRAM_TOKEN** -> Token to access the HTTP API of your bot. 
 
 - **$URI_MONGODB**	-> Connection URI with your MongoDB database. 
 
> For example: mongodb://user:pass@192.168.1.2

 - **$URL_POOL** -> URL of your Pool and where the bot will be able to consult the statistics.

## Start the Container

To run this bot using Docker you can use the following command:

    docker run -d \
    -e "TELEGRAM_TOKEN=YOUR-TELEGRAM-TOKEN" \
    -e "URI_MONGODB=YOUR_URI_CONNECT_MONGODB" \
    -e "URL_POOL=URL_FOR_YOUR_POOL" \
    octaviojmaia/bot-equalhash
    
## Donations

**ETH/ETC**: 0x07EafA605A7253af37C5bd9F5d1e62F3a073424a


