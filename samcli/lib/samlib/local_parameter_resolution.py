"""
docstring
"""

import logging

from samtranslator.public.plugins import BasePlugin
from samtranslator.intrinsics.resolver import IntrinsicsResolver

LOG = logging.getLogger(__name__)


class LocalParameterResolution(BasePlugin):

    def __init__(self, parameter_overrides):
        """
        Initialize the plugin
        """
        overrides = [s.strip() for s in parameter_overrides.split(',')]
        self.parameter_overrides = dict(s.split('=') for s in overrides)
        super(LocalParameterResolution, self).__init__(LocalParameterResolution.__name__)

    def on_before_transform_template(self, template):
        """

        Parameters
        ----------
        template

        Returns
        -------

        """

        LOG.info(template)
        template_parameter_map = template.get("Parameters", {})
        parameter_to_value = {}

        for key, value in self.parameter_overrides.items():
            param_type = template_parameter_map.get(key).get('Type')
            if param_type == 'Number':
                self.parameter_overrides[key] = int(value)

        for key, value in template_parameter_map.items():
            if value.get("Default", None):
                parameter_to_value[key] = value.get("Default")

        LOG.info(parameter_to_value)
        # setting to mutate the template that was passed into the function
        # Note: {**blah, **blah2} is the Py3 way to merge dicts together. Need to support py2 as well here.
        some_template = \
            IntrinsicsResolver({**parameter_to_value, **self.parameter_overrides}).resolve_parameter_refs(template)

        LOG.info(some_template)
