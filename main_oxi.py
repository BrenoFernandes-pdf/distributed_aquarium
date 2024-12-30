from objects.oxi import Ox

oxigen = Ox(False, 9)
addr = oxigen.get_addr_by_mult()

socket = oxigen.connect_tcp(addr)
msg = f'{oxigen.type}'

oxigen.write(socket, msg)
oxigen.receive(socket)