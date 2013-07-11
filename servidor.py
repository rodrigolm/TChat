#!/usr/bin/env python
# -*- coding: UTF-8 -*-
 
import socket
import thread
import time
import os
import sys
from termcolor import colored
 
HOST = "127.0.0.1"
PORT = 4004

# Função que retorna os usuários conectados.
def imprime_usuarios(dicionario):
	lista = "- "
	for chave in dicionario.keys():
		lista += chave
		lista += " - "
	return lista

def aceita(conn):
	"""
	Chama a função em uma thread para não bloquear. Espera que um
	nome seja digitado de uma conexão. Quando o nome for inserido,
	define a conexão e adiciona o usuário para o dicionário de
	usuários
	"""
	def inicia_thread():
		while True:
			conn.send(colored("Digite o seu nome: ", "yellow", attrs=["bold"]))
			try:
				nome = (conn.recv(1024).strip()).lower()
			except socket.error:
				continue
			if nome in usuarios:
				conn.send(colored("O nome escolhido já está em uso.\n", "red", attrs=["bold"]))
			elif nome:
				conn.setblocking(False)
				usuarios[nome] = conn
				conn.send(colored("\n================================================\n\nVocê se conectou... Bem-vindo!\n\n================================================\n\n", "green", attrs=["bold"]))
				conn.send(colored("Comandos:\nPara sair, digite: /sair\nPara mensagem privada, digite: /para usuario mensagem\nPara visualizar quais usuários estão conectados, digite: /online\n\n", "grey", attrs=["bold"]))
				conn.send(colored("...\n\n", "yellow", attrs=["bold"]))
				horario = colored(str(time.strftime('%X')), "grey", attrs=['bold'])
				print colored("-> O usuário <", attrs=["bold"]) + colored("%s" % nome, "cyan", attrs=["bold"]) + colored("> se conectou as", attrs=["bold"]), "[%s]" % horario, colored("<-", attrs=["bold"])
				broadcast(nome, "[%s] " % horario + colored("%s acaba de se conectar..." % nome, "yellow", attrs=["bold"]))
				break
	thread.start_new_thread(inicia_thread, ())
 
def broadcast(nome, mensagem):
	"""
	Verifica se no começo da mensagem contém o comando "/para"
	Caso seja verdadeiro, olha na mensagem para quem é o destinatário.
	Em seguida, envia a mensagem para um usuário específico.
	Caso a mensagem contenha o comando "/online", retorna para
	o usuário, a lista de usuários conectados no momento.
	"""

	tam_nome = len(nome)
	msg = mensagem.split(" ")
	comando = msg[2]
	verificador = 0

	if "/para" in comando:
		for destinatario, conn in usuarios.items():
			if destinatario == msg[3]:
				try:
					tam_destinatario = len(destinatario)
					remetente = msg[0] + " " + msg[1] + colored(" (privado) ", "magenta", attrs=["bold"])
					conn.send(remetente + mensagem[(47 + tam_nome + tam_destinatario):] + "\n")
					verificador = 1
				except socket.error:
					pass
		if verificador == 0:
			for destinatario, conn in usuarios.items():
				if destinatario == nome:
					try:
						conn.send(colored("Usuário não encontrado\n", "red", attrs=["bold"]))
					except socket.error:
						pass
	elif "/online" in comando:
		for destinatario, conn in usuarios.items():
			if destinatario == nome:
				try:
					conn.send(colored("Usuários conectados no momento:\n%s\n" % imprime_usuarios(usuarios), "yellow", attrs=["bold"]))
				except socket.error:
					pass
	else:
		"""
		Caso contrário, envia uma mensagem para todos os usuários,
		exceto quem enviou e o próprio servidor.
		"""
		for destinatario, conn in usuarios.items():
			if destinatario != nome and destinatario != servidor:
				try:
					conn.send(mensagem + "\n")
				except socket.error:
					pass

# Limpa a tela do console.
os.system('clear')

print colored("\nIniciando servidor em:", "yellow", attrs=['bold'])

# Configurando o socket do servidor.
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor.setblocking(False)
servidor.bind((HOST, PORT))
servidor.listen(1)

print colored("%s ...\n" % ("%s:%s" % servidor.getsockname()), "yellow", attrs=['bold'])
print colored("Servidor iniciado com sucesso. Esperando por conexões ...\n", "green", attrs=['bold'])

# Loop do programa.
usuarios = {}
while True:
	try:
		# Aceita novas conexões.
		while True:
			try:
				conn, addr = servidor.accept()
			except socket.error:
				break
			aceita(conn)
		# Leitura das conexões.
		for nome, conn in usuarios.items():
			try:
				mensagem = conn.recv(1024)
			except socket.error:
				continue
			if not mensagem:
				# Caso um usuário se desconecte.
				del usuarios[nome]
				horario = colored(str(time.strftime('%X')), "grey", attrs=['bold'])
				print colored("-> O usuário <", attrs=["bold"]) + colored("%s" % nome, "cyan", attrs=["bold"]) + colored("> se desconectou as", attrs=["bold"]), "[%s]" % horario, colored("<-", attrs=["bold"])
				broadcast(nome, "[%s] " % horario + colored("%s se desconectou." % nome, "yellow", attrs=["bold"]))
			else:
				# Envia mensagem.
				horario = colored(str(time.strftime('%X')), "grey", attrs=['bold'])
				broadcast(nome, "[%s]" % horario + " <" + colored("%s" % nome, "cyan", attrs=["bold"]) + "> %s" % mensagem.strip())
		time.sleep(.1)
	except (SystemExit, KeyboardInterrupt):
		break
