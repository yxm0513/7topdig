# -*- coding: utf-8 -*-
#!/usr/bin/python
from app import app

#host="10.32.100.116"
host='0.0.0.0'

if __name__ == '__main__':
	app.run(host, 5000)
	
