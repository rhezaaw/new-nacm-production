import paramiko
import sys
ssh = paramiko.SSHClient()  # ??ssh??
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='10.10.10.40', port='22', username='admin', password='1234', look_for_keys=False )
rcon = ssh.invoke_shell()
outpt = rcon.recv(65535)
#stdin, stdout, stderr = ssh.exec_command('int bridge add name=basdwde')
#stdin, stdout, stderr = ssh.exec_command('int bridge add name=kavsdd')
#result = stdout.read().decode('utf-8')
rcon.send('int bridge add name=laal')
#print(str(result))
#print(sys.stdin.read())
#result1 = result.decode()
#print(result1)
#error = stderr.read().decode('utf-8')
#print(error)
