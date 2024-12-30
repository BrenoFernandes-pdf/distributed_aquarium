from objects.temp import Temp

temp = Temp(False, 30)
addr = temp.get_addr_by_mult()

socket = temp.connect_tcp(addr)
msg = f'{temp.type}'

temp.write(socket, msg)
temp.receive(socket)