# COMP112-Assignment-5

# Filtering LRU-Cache HTTP Proxy

## Max Cohen and Jim Mao

## Brief Overview

All browsers, including Google Chrome and Mozilla Firefox, have the ability to incorporate a proxy into its Web browsing capabilities. A proxy is the server that sits in between the client and the server and attempts to fulfill the request for the client. If it can, the proxy sends the response to the client. If not, the proxy forwards the request to the server. The proxy is able to filter and content that the user requests, providing faster content delivery and security. 

LRU Cache stands for Least Recently Used Cache. This enables the cache to make a best-effort attempt to store only the most recent data when the cache has reached maximum capacity. The least recently used data is gradually replaced, increasing the effectiveness of the cache. The user can adjust the cache size to hold any number of items based on how much available space they are willing to use for the cache on their local machine.

The user can customize to block any site that he or she desires by providing the URL or server that the user does not wish to visit.

## Usage

python proxy.py [portnumber]

The default port number is 8080 if not port is supplied.

## Future Plans

Test, time, and revise LRU implementation based on measured times in retrieving from the cache.
