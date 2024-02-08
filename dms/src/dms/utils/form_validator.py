import base64
from jsonschema.validators import Draft4Validator


class FormValidateError(Exception):
	def __init__(self, message, schema, relative_path):
		super(FormValidateError, self).__init__(message)
		self.schema = schema
		self.relative_path = relative_path


def _create_normalizer(schema):
	normalizer = {"schema": schema}
	for key, value in schema.items():
		if key == 'type':
			normalizer['t'] = value
			if value == 'array':
				normalizer['c'] = lambda v: v.split(schema.get('delimiter'))
			elif value == 'integer':
				normalizer['c'] = int
			elif value == 'number':
				normalizer['c'] = float
			elif value == 'bytes':
				encoding = schema.get('encoding')
				if encoding == 'hex':
					normalizer['c'] = lambda v: v.decode('hex')
				elif encoding == 'base64':
					normalizer['c'] = base64.standard_b64decode
				elif encoding == 'urlbase64':
					normalizer['c'] = base64.urlsafe_b64decode
				else:
					normalizer['c'] = lambda v: v.encode('utf-8')
		elif key == 'properties':
			normalizer['f'] = {}
			for pname, pvalue in value.items():
				normalizer['f'][pname] = _create_normalizer(pvalue)
		elif key == 'items':
			normalizer['i'] = _create_normalizer(value)

	return normalizer


def _normalize_data_field(normalizer, data, path):
	if 'c' in normalizer:
		try:
			ndata = normalizer['c'](data)
		except Exception as ex:
			raise FormValidateError(
				'%s cannot convert as %s(%s)' % (data, normalizer['t'], ex),
				normalizer["schema"], path)
	else:
		ndata = data
	if 'i' in normalizer:
		inormalizer = normalizer['i']
		for i in range(len(ndata)):
			tmp_path = path + [i]
			ndata[i] = _normalize_data_field(inormalizer, ndata[i], tmp_path)
	return ndata


def _normalize_data(normalizer, data):
	if not isinstance(data, dict):
		raise FormValidateError("root type should be object", data, [])
	field_normalizer = normalizer.get('f', {})
	ndata = {}
	for fname, val in data.items():
		if fname in field_normalizer:
			ndata[fname] = _normalize_data_field(field_normalizer[fname], val, [fname])
		else:
			ndata[fname] = val
	return ndata


class FormValidator(object):
	"""
	refer to json schema. the root should be a object
	supported schema
	common: type
	object: properties, required
	array: items, maxItems, minItems, delimiter
	integer: minimum, maximum
	number: minimum, maximum
	string: length, minLength, maxLength, pattern
	bytes: length, minLength, maxLength, encoding
	bytes encoding support raw / hex / base64 / urlbase64
	"""

	def __init__(self, schema):
		self._normalizer = None
		self._validator = None
		self._schema = None

		self.schema = schema

	@property
	def schema(self):
		return self._schema

	@schema.setter
	def schema(self, schema):
		if schema.get("type", "object") != "object":
			raise FormValidateError("root type should be object", schema, [])
		self._schema = schema
		self._normalizer = _create_normalizer(self._schema)
		self._validator = Draft4Validator(self._schema).validate

	def normalize(self, data):
		ret = _normalize_data(self._normalizer, data)
		self._validator(ret)
		return ret

