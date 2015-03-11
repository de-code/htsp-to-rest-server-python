from passlib.apache import HtpasswdFile

htpasswd_file=".htpasswd"

username = raw_input('username: ')
password = raw_input('password: ')

ht = HtpasswdFile(htpasswd_file, new=False)
if ht.check_password(username, password):
    print "valid"
else:
    print "invalid"
