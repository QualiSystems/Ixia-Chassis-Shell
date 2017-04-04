
import paramiko


def exec_command(command):
    cmd_to_write = 'puts [{}]\n\r'.format(command)
    print cmd_to_write
    stdin.write(cmd_to_write)
    stdin.flush()
    l = len(stdout.channel.in_buffer)
    while not l:
        l = len(stdout.channel.in_buffer)
    output = stdout.read(l)
    print output
    return output.strip()

key = paramiko.RSAKey.from_private_key_file("C:/Program Files (x86)/Ixia/IxOS/8.20-EA/TclScripts/lib/ixTcl1.0/id_rsa")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname='192.168.42.174', port=8022, username='ixtcl', pkey=key)
stdin, stdout, _ = ssh.exec_command('')

exec_command('source /opt/ixia/ixos/current/IxiaWish.tcl')
exec_command('package req IxTclHal')
