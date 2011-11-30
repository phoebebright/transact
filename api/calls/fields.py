import datetime
from decimal import Decimal, InvalidOperation
from api.exceptions import ValidationDecimalException

class BaseField(object):
    """Base class for all field types.

    The ``source`` parameter sets the key that will be retrieved from the source
    data. If ``source`` is not specified, the field instance will use its own
    name as the key to retrieve the value from the source data.

    """
    def __init__(self, source=None):
        self.source = source

    def populate(self, data):
        """Set the value or values wrapped by this field"""

        self.data = data

    def to_python(self):
        '''After being populated, this method casts the source data into a
        Python object. The default behavior is to simply return the source
        value. Subclasses should override this method.

        '''
        return self.data

    def to_serial(self):
        '''Used to serialize forms back into JSON or other formats.

        This method is essentially the opposite of
        :meth:`~micromodels.fields.BaseField.to_python`. A string, boolean,
        number, dictionary, list, or tuple must be returned. Subclasses should
        override this method.

        '''
        return self.data


class CharField(BaseField):
    """Field to represent a simple Unicode string value."""

    def to_serial(self):
        return self.data.encode('utf8')

    def to_python(self):
        """Convert the data supplied using the :meth:`populate` method to a
        Unicode string.

        """
        if self.data is None:
            return ''
        return unicode(self.data, encoding='utf8')


class IntegerField(BaseField):
    """Field to represent an integer value"""

    def to_python(self):
        """Convert the data supplied to the :meth:`populate` method to an
        integer.

        """
        if self.data is None:
            return 0
        return int(self.data)


class FloatField(BaseField):
    """Field to represent a floating point value"""

    def to_python(self):
        """Convert the data supplied to the :meth:`populate` method to a
        float.

        """
        if self.data is None:
            return 0.0
        return float(self.data)


class BooleanField(BaseField):
    """Field to represent a boolean"""

    def to_python(self):
        """The string ``'True'`` (case insensitive) will be converted
        to ``True``, as will any positive integers.

        """
        if isinstance(self.data, basestring):
            return self.data.strip().lower() == 'true'
        if isinstance(self.data, int):
            return self.data > 0
        return bool(self.data)


class DateTimeField(BaseField):
    """Field to represent a datetime

    The ``format`` parameter dictates the format of the input strings, and is
    used in the construction of the :class:`datetime.datetime` object.

    The ``serial_format`` parameter is a strftime formatted string for
    serialization. If ``serial_format`` isn't specified, an ISO formatted string
    will be returned by :meth:`~micromodels.DateTimeField.to_serial`.

    """
    def __init__(self, format, serial_format=None, **kwargs):
        super(DateTimeField, self).__init__(**kwargs)
        self.format = format
        self.serial_format = serial_format

    def to_python(self):
        '''A :class:`datetime.datetime` object is returned.'''

        if self.data is None:
            return None
        return datetime.datetime.strptime(str(self.data), self.format)

    def to_serial(self):
        if not self.serial_format:
            return self.data.isoformat()
        return self.data.strftime(self.serial_format)


class DateField(DateTimeField):
    """Field to represent a :mod:`datetime.date`"""

    def to_python(self):
        datetime = super(DateField, self).to_python()
        return datetime.date()

class DecimalField(BaseField):
    """Field to represent a :mod:`decimal.Decimal`"""

    def populate(self, data):
        """Make sure we have proper Decimal field"""
        try:
            if isinstance(data, (int,  float)):
                data = str(data)
            self.data = Decimal(data)
        except InvalidOperation:
            raise ValidationDecimalException()

    def to_serial(self):
        return str(self.data)

class TimeField(DateTimeField):
    """Field to represent a :mod:`datetime.time`"""

    def to_python(self):
        datetime = super(TimeField, self).to_python()
        return datetime.time()
