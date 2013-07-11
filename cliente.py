#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Usuario do Chat

import socket
import select
import string
import os
import time
import sys
from termcolor import colored

def prompt():
	sys.stdout.flush()

if __name__ == "__main__":
		# Limpa a tela do console
		os.system('clear')

		if(len(sys.argv) < 3):
			print colored("\nForma de usar: python cliente.py host porta\n", "red", attrs=["bold"])
			sys.exit()

		servidor = sys.argv[1]
		porta = int(sys.argv[2])

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.settimeout(2)

		# Conecta ao servidor
		try:
			print colored("\nConectando-se ao servidor...\n", "yellow", attrs=["bold"])
			s.connect((servidor, porta))
		except:
			print colored("\nNão foi possível se conectar!\n", "red", attrs=["bold"])
			sys.exit()

		while 1:
			lista_socket = [sys.stdin, s]

			leitura_sockets, escrita_sockets, erro_sockets = select.select(lista_socket, [], [])

			for sock in leitura_sockets:
				# Mensagens vindas do servidor
				if sock == s:
					dado = sock.recv(4096)
					if not dado:
						print colored("\nDesconectou do servidor.\n", "red", attrs=["bold"])
						s.close()
						sys.exit()
					else:
						# Imprime dados
						sys.stdout.write(dado)
						prompt()
				# Usuario digitou uma mensagem
				else:
					msg = sys.stdin.readline()
					if "/sair" in msg:
						print colored("\nDesconectou do servidor.\n", "red", attrs=["bold"])
						s.close()
						sys.exit()
					s.send(msg)
					prompt()
