# BaraFansClub - Jaringan Komputer 2023

Repository template tugas besar 2 - IF3130 - Jaringan Komputer - 2023

# TCP Over UDP

This repository contains how to simulate TCP connection over UDP socket. It consist of simple server and client, server can send file to a or multiple client. There are no non builtin library are used for this implementation.

## Members - masuktipi

| Name                |   NIM    |
|---------------------|:--------:|
| Fatih N.R.I.        | 13521060 |
| Bintang Dwi Marthen | 13521144 |
| Nathan Tenka        | 13521172 |

## Usage

server.py

```
usage: server.py [-h] broadcast_port path_file [server_ip]
server.py: error: the following arguments are required: broadcast_port, path_file
```

client.py

```
usage: client.py [-h] client_port broadcast_port path_file [server_ip] [client_ip]
client.py: error: the following arguments are required: client_port, broadcast_port, path_file
```

serverGame.py
```
usage: serverGame.py [-h] broadcast_port
serverGame.py: error: the following arguments are required: broadcast_port
```

clientGame.py
```
usage: clientGame.py [-h] client_port broadcast_port
clientGame.py: error: the following arguments are required: client_port, broadcast_port
```

## Features implemented

1. Three-Way Handshake
2. ARQ Go-Back-N
3. File Transfer
4. Tic-Tac-Toe TCP Game
5. Remote PC Connection
