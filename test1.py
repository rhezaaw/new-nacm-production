import paramiko
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname='10.10.10.40', port='22', username='admin', password='1234')

returned_array = []

for command in commands:
	log.debug('command to launch in ssh in {}: {}'.format(hostname, command))
	stdin, stdout, stderr = client.exec_command('ip route add dst-address=123.123.123.0/24 gateway=10.10.10.1')
	out = stdout.read().decode('utf-8')
	err = stderr.read().decode('utf-8')
	returned_array.append({'out': out, 'err': err})
	log.debug('commnad launched / out: {} / error: {}'.format(out, err))

	client.close()

#return returned_array 
