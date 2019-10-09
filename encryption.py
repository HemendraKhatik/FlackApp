"""
Author:		kaloneh <kaloneh@gmail.com>
Comment:	for the future sake of security it's necessary to encrypt all messages and passwords.
			When the database user_table is diclosured or revealed not only there is no chance to
			protect the current user, but also other users' plain data can be manipulated, however,
			encrypting passwords buy some times to be decrypted so that broadcasting an anouncement
			can aware users to make changes and then migrating to proper pool to avoid the disclosure!
"""

# import sys
import hashlib
# from functools import wraps

class HashTable(object):
	"""The HashTable is responsible for hashifying critical data
		such as password and some messages in which helps to guarantee
		once the session is hijacked or any irresponsible action is
		occurred data still remains safe and cant't be decoded easily"""
	
	def __init__(self, method='md5'):
		self._method = method

	def hexdigest(self, plain, encoding='utf-8'):
		hasher = getattr(hashlib,self._method)()
		getattr(hasher,'update')(plain.encode(encoding))
		return getattr(hasher,'hexdigest')()

