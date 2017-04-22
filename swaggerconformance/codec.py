"""
Provides a codec for converting between JSON representations of objects and
the objects themselves.
"""
import logging

from pyswagger.primitives import SwaggerPrimitive
from pyswagger.primitives._int import validate_int, create_int
from pyswagger.primitives._float import validate_float, create_float
# pyswagger and requests make INFO level logs regularly by default, so lower
# their logging levels to prevent the spam.
logging.getLogger("pyswagger").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

__all__ = ["SwaggerCodec"]


log = logging.getLogger(__name__)


class _SwaggerPrimitiveDefaults(SwaggerPrimitive):
    """An enhanced primitive factory which can handle default types."""

    def get(self, _type, _format=None):
        """If we don't understand the format, fallback to the most
        basic version for the type, and if we don't know the type, then
        that is an error as the allowed types are strictly specified,
        so just let that be handled as normal.
        """
        result = super().get(_type, _format)
        if result == (None, None):
            result = super().get(_type, None)

        return result


class SwaggerCodec:
    """Encodes objects as JSON and decodes JSON back into objects."""

    def __init__(self):
        self._factory = _SwaggerPrimitiveDefaults()

        # Pyswagger doesn't support integers or floats without a 'format', even
        # though it does seem valid for a spec to not have one.
        # We work around this by adding support for these types without format.
        # See here: https://github.com/mission-liao/pyswagger/issues/65
        self._factory.register('integer', None, create_int, validate_int)
        self._factory.register('number', None, create_float, validate_float)

    @property
    def swagger_factory(self):
        """The underlying pyswagger primitive factory.

        :rtype: pyswagger.primitives.SwaggerPrimitive
        """
        return self._factory

    def register(self, type_str, format_str, creator):
        """Register a new creator for objects of the given type and format.

        :param type_str: The Swagger schema type to register for.
        :type type_str: str
        :param format_str: The Swagger schema format to register for.
        :type format_str: str
        :param creator: The callable to create an object of the desired type.
        :type creator: callable
        """
        self._factory.register(type_str, format_str, creator)
