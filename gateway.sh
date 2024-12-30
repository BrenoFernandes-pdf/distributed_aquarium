#!/bin/bash
# Lembra de usar chmod +x gateway.sh antes de ./gateway.sh

# Configurações do Netcat
PORTA_NETCAT=37020
IP_GATEWAY=$(hostname -I | awk '{print $1}')

# Inicia o Netcat em modo escuta
echo "Iniciando o Netcat no IP: $IP_GATEWAY e porta: $PORTA_NETCAT"
nc -l $PORTA_NETCAT &
NC_PID=$!  # Captura o PID do Netcat para finalizar depois, se necessário

# Espera 2 segundos para garantir que o Netcat esteja em execução
sleep 2

# Envia a mensagem multicast com as informações do gateway
echo "$IP_GATEWAY $PORTA_NETCAT" | nc -u 224.3.29.71 10000
echo "Mensagem multicast enviada: $IP_GATEWAY $PORTA_NETCAT"

# Aguarda a execução do Netcat
wait $NC_PID
