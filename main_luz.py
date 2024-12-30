from objects.luz import Lamp

luz_aquario = Lamp(False)
addr = luz_aquario.get_addr_by_mult()
socket = luz_aquario.connect_tcp(addr)

msg = f'{luz_aquario.type}'
luz_aquario.write(socket, msg)
#msg = f'{luz_aquario.state}' Checar o estado (ligado/desligado) da Lâmpada
#luz_aquario.write(socket, msg)
luz_aquario.receive(socket)