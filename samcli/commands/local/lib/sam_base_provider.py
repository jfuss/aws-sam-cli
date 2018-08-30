"""
Base class for SAM Template providers
"""

from samcli.lib.samlib.wrapper import SamTranslatorWrapper
from samtranslator.intrinsics.resolver import IntrinsicsResolver


class SamBaseProvider(object):
    """
    Base class for SAM Template providers
    """

    @staticmethod
    def get_template(template_dict, parameter_overrides):
        template_dict = template_dict or {}
        if template_dict:
            template_dict = SamTranslatorWrapper(template_dict, parameter_overrides).run_plugins()

        # This is copied from local_parameter_resolution so this happens after the template is passed through SAM
        # Translator
        # do this after so we can use floats instead of ints
        overrides = [s.strip() for s in parameter_overrides.split(',')]
        parameter_overrides = dict(s.split('=') for s in overrides)

        template_parameter_map = template_dict.get("Parameters", {})
        parameter_to_value = {}

        for key, value in parameter_overrides.items():
            param_type = template_parameter_map.get(key).get('Type')
            if param_type == 'Number':
                parameter_overrides[key] = float(value)

        for key, value in template_parameter_map.items():
            if value.get("Default", None):
                parameter_to_value[key] = value.get("Default")

        # setting to mutate the template that was passed into the function
        some_template = IntrinsicsResolver({**parameter_to_value, **parameter_overrides}).resolve_parameter_refs(
            template_dict)

        return template_dict
