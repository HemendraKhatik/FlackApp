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

