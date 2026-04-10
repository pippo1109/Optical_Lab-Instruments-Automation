from comcasp_driver import CaspBoard

board = CaspBoard(r"C:\Users\Guaxyn\Documents\Testes Realizados no Labolatório de Engenharia Fotônica\Outros projetos\Lente_liquida\ComCasp64.dll")
ports = board.list_com_ports()

board = CaspBoard()
board.open()
board.print_info()

print(f"temp: {board.get_temperature()}")
print(f"tensão foco: {board.get_focus_voltage()}")

#############################################################
board.set_focus_voltage(49.0) #################################
#############################################################

print(f"temp: {board.get_temperature()}")
print(f"tensão foco: {board.get_focus_voltage()}")
board.close()