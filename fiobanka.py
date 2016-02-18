# -*- coding: utf-8 -*-
#
# FioBankPy - Python library for accessing Fio bank's web API
# Copyright (C) 2016 Martin Doucha
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime, requests, decimal, re, time

__all__ = ['FioBanka']

BASEURL = 'https://www.fio.cz/ib_api/rest/'
def _parsedate(value):
	"""Regexp date parser. strptime() says that '%Y-%m-%d%z' is invalid"""
	match = re.search('(\d+)-(\d+)-(\d+)[+-]\d+', value)
	if not match:
		raise ValueError('Invalid date string')
	return datetime.date(*[int(x) for x in match.groups()])

class FioBanka(object):
	"""FioBanka(token)

	Connection object for accessing bank account associated with given
	token.
	"""

	def __init__(self, token):
		self._token = str(token)
		self._lastreq = None

	def _rate_limit(self):
		now = time.time()
		# Sleep extra 0.5s to avoid random HTTP 409 errors
		if self._lastreq != None and self._lastreq + 30.5 > now:
			time.sleep(self._lastreq + 30.5 - now)
		self._lastreq = time.time()

	def _get(self, cmd, *args):
		url = '/'.join([BASEURL, cmd, self._token] + list(args))
		r = requests.get(url)
		r.raise_for_status()
		return r

	def _parse_transactions(self, r):
		tmp = {}
		data = r.json(parse_float=decimal.Decimal)['accountStatement']
		translist = data['transactionList']['transaction']
		ret = [_FioTransaction(x) for x in translist]
		return (_FioTransactionsHeader(data['info']), ret)

	def set_last_id(self, transaction_id):
		"""set_last_id(self, transaction_id)
		
		Change starting point for get_transactions_last()."""
		self._get('set-last-id', str(transaction_id), '')

	def set_last_date(self, date):
		"""set_last_date(self, date)
		
		Change starting point for get_transactions_last()."""
		if isinstance(date, (datetime.date, datetime.datetime)):
			date = date.strftime('%Y-%m-%d') 
		self._get('set-last-date', date, '')

	def get_transactions_last(self):
		"""get_transactions_last(self)
		
		Download all new transactions."""
		self._rate_limit()
		r = self._get('last', 'transactions.json')
		return self._parse_transactions(r)

	def get_transactions_periods(self, start, end):
		"""get_transactions_periods(self, start, end)
		
		Download all transactions in the date range [start;end]"""
		if isinstance(start, (datetime.date, datetime.datetime)):
			start = start.strftime('%Y-%m-%d') 
		if isinstance(end, (datetime.date, datetime.datetime)):
			end = end.strftime('%Y-%m-%d') 
		self._rate_limit()
		r = self._get('periods', start, end, 'transactions.json')
		return self._parse_transactions(r)

	def get_report(self, year, report_id, format='pdf'):
		"""get_report(self, year, report_id, format='pdf')
		
		Download periodical account report for given year and ID."""
		filename = 'transactions.{0}'.format(format)
		self._rate_limit()
		r = self._get('by-id', str(year), str(report_id), filename)
		return r.content

class _FioTransactionsHeader(object):
	"""Transaction list header object."""

	def __init__(self, info):
		date = lambda x: _parsedate(x) if x != None else x
		self.accountID = info.get('accountID')
		self.bankId = info.get('bankId')
		self.bic = info.get('bic')
		self.closingBalance = info.get('closingBalance')
		self.currency = info.get('currency')
		self.dateEnd = date(info.get('dateEnd'))
		self.dateStart = date(info.get('dateStart'))
		self.iban = info.get('iban')
		self.idFrom = info.get('idFrom')
		self.idLastDownload = info.get('idLastDownload')
		self.idList = info.get('idList')
		self.idTo = info.get('idTo')
		self.openingBalance = info.get('openingBalance')
		self.yearList = info.get('yearList')

	def __repr__(self):
		return '<_FioTransactionsHeader ' + str(self.__dict__) + '>'

class _FioTransaction(object):
	"""Transaction details object."""

	def __init__(self, info):
		get = lambda x: info[x].get('value') if info.get(x) else None
		date = lambda x: _parsedate(x) if x != None else x
		self.date = date(get('column0'))
		self.amount = get('column1')
		self.remote_account = get('column2')
		self.bank_id = get('column3')
		self.constant_symbol = get('column4')
		self.variable_symbol = get('column5')
		self.specific_symbol = get('column6')
		self.user_identity = get('column7')
		self.type = get('column8')
		self.authorized_by = get('column9')
		self.remote_account_name = get('column10')
		self.bank_name = get('column12')
		self.currency = get('column14')
		self.message = get('column16')
		self.order_id = get('column17')
		self.id = get('column22')
		self.comment = get('column25')
		# One of these two fields is "Upřesnění", the othe is "BIC".
		# See http://www.fio.cz/docs/cz/API_Bankovnictvi.pdf
		# The docs don't say which is which and all my test data have
		# only NULL values there...
		self._column18 = get('column18')
		self._column26 = get('column26')

	def __repr__(self):
		return '<_FioTransaction ' + str(self.__dict__) + '>'
