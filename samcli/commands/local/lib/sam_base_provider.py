"""
Base class for SAM Template providers
"""

import logging
import re

from samtranslator.intrinsics.resolver import IntrinsicsResolver
from samtranslator.intrinsics.actions import RefAction, Action
from six import string_types

from samcli.lib.samlib.wrapper import SamTranslatorWrapper
from samcli.lib.samlib.resource_metadata_normalizer import ResourceMetadataNormalizer


LOG = logging.getLogger(__name__)


class SubAction(Action):
    intrinsic_name = "Fn::Sub"

    def resolve_parameter_refs(self, input_dict, parameters):
        """
        Substitute references found within the string of `Fn::Sub` intrinsic function
        :param input_dict: Dictionary representing the Fn::Sub function. Must contain only one key and it should be
            `Fn::Sub`. Ex: {"Fn::Sub": ...}
        :param parameters: Dictionary of parameter values for substitution
        :return: Resolved
        """

        def do_replacement(full_ref, prop_name):
            """
            Replace parameter references with actual value. Return value of this method is directly replaces the
            reference structure
            :param full_ref: => ${logicalId.property}
            :param prop_name: => logicalId.property
            :return: Either the value it resolves to. If not the original reference
            """
            return parameters.get(prop_name, full_ref)

        return self._handle_sub_action(input_dict, do_replacement)

    def resolve_resource_refs(self, input_dict, supported_resource_refs):
        """
        Resolves reference to some property of a resource. Inside string to be substituted, there could be either a
        "Ref" or a "GetAtt" usage of this property. They have to be handled differently.
        Ref usages are directly converted to a Ref on the resolved value. GetAtt usages are split under the assumption
        that there can be only one property of resource referenced here. Everything else is an attribute reference.
        Example:
            Let's say `LogicalId.Property` will be resolved to `ResolvedValue`
            Ref usage:
                ${LogicalId.Property}  => ${ResolvedValue}
            GetAtt usage:
                ${LogicalId.Property.Arn} => ${ResolvedValue.Arn}
                ${LogicalId.Property.Attr1.Attr2} => {ResolvedValue.Attr1.Attr2}
        :param input_dict: Dictionary to be resolved
        :param samtranslator.intrinsics.resource_refs.SupportedResourceReferences supported_resource_refs: Instance of
            an `SupportedResourceReferences` object that contain value of the property.
        :return: Resolved dictionary
        """

        def do_replacement(full_ref, ref_value):
            """
            Perform the appropriate replacement to handle ${LogicalId.Property} type references inside a Sub.
            This method is called to get the replacement string for each reference within Sub's value
            :param full_ref: Entire reference string such as "${LogicalId.Property}"
            :param ref_value: Just the value of the reference such as "LogicalId.Property"
            :return: Resolved reference of the structure "${SomeOtherLogicalId}". Result should always include the
                ${} structure since we are not resolving to final value, but just converting one reference to another
            """

            # Split the value by separator, expecting to separate out LogicalId.Property
            splits = ref_value.split(self._resource_ref_separator)

            # If we don't find at least two parts, there is nothing to resolve
            if len(splits) < 2:
                return full_ref

            logical_id = splits[0]
            property = splits[1]
            resolved_value = supported_resource_refs.get(logical_id, property)
            if not resolved_value:
                # This ID/property combination is not in the supported references
                return full_ref

            # We found a LogicalId.Property combination that can be resolved. Construct the output by replacing
            # the part of the reference string and not constructing a new ref. This allows us to support GetAtt-like
            # syntax and retain other attributes. Ex: ${LogicalId.Property.Arn} => ${SomeOtherLogicalId.Arn}
            replacement = self._resource_ref_separator.join([logical_id, property])
            return full_ref.replace(replacement, resolved_value)

        return self._handle_sub_action(input_dict, do_replacement)

    def resolve_resource_id_refs(self, input_dict, supported_resource_id_refs):
        """
        Resolves reference to some property of a resource. Inside string to be substituted, there could be either a
        "Ref" or a "GetAtt" usage of this property. They have to be handled differently.
        Ref usages are directly converted to a Ref on the resolved value. GetAtt usages are split under the assumption
        that there can be only one property of resource referenced here. Everything else is an attribute reference.
        Example:
            Let's say `LogicalId` will be resolved to `NewLogicalId`
            Ref usage:
                ${LogicalId}  => ${NewLogicalId}
            GetAtt usage:
                ${LogicalId.Arn} => ${NewLogicalId.Arn}
                ${LogicalId.Attr1.Attr2} => {NewLogicalId.Attr1.Attr2}
        :param input_dict: Dictionary to be resolved
        :param dict supported_resource_id_refs: Dictionary that maps old logical ids to new ones.
        :return: Resolved dictionary
        """

        def do_replacement(full_ref, ref_value):
            """
            Perform the appropriate replacement to handle ${LogicalId} type references inside a Sub.
            This method is called to get the replacement string for each reference within Sub's value
            :param full_ref: Entire reference string such as "${LogicalId.Property}"
            :param ref_value: Just the value of the reference such as "LogicalId.Property"
            :return: Resolved reference of the structure "${SomeOtherLogicalId}". Result should always include the
                ${} structure since we are not resolving to final value, but just converting one reference to another
            """

            # Split the value by separator, expecting to separate out LogicalId
            splits = ref_value.split(self._resource_ref_separator)

            # If we don't find at least one part, there is nothing to resolve
            if len(splits) < 1:
                return full_ref

            logical_id = splits[0]
            resolved_value = supported_resource_id_refs.get(logical_id)
            if not resolved_value:
                # This ID/property combination is not in the supported references
                return full_ref

            # We found a LogicalId.Property combination that can be resolved. Construct the output by replacing
            # the part of the reference string and not constructing a new ref. This allows us to support GetAtt-like
            # syntax and retain other attributes. Ex: ${LogicalId.Property.Arn} => ${SomeOtherLogicalId.Arn}
            return full_ref.replace(logical_id, resolved_value)

        return self._handle_sub_action(input_dict, do_replacement)

    def _handle_sub_action(self, input_dict, handler):
        """
        Handles resolving replacements in the Sub action based on the handler that is passed as an input.
        :param input_dict: Dictionary to be resolved
        :param supported_values: One of several different objects that contain the supported values that need to be changed.
            See each method above for specifics on these objects.
        :param handler: handler that is specific to each implementation.
        :return: Resolved value of the Sub dictionary
        """
        if not self.can_handle(input_dict):
            return input_dict

        key = self.intrinsic_name
        sub_value = input_dict[key]

        resolved_sub_value = self._handle_sub_value(sub_value, handler)

        # TODO: Can this be constrained further?
        logical_id_regex = '.*'
        ref_pattern = re.compile(r'\$\{(' + logical_id_regex + ')\}')

        if not re.findall(ref_pattern, str(resolved_sub_value)):
            return resolved_sub_value
        else:
            input_dict[key] = resolved_sub_value
            return input_dict

    def _handle_sub_value(self, sub_value, handler_method):
        """
        Generic method to handle value to Fn::Sub key. We are interested in parsing the ${} syntax's inside
        the string portion of the value.
        :param sub_value: Value of the Sub function
        :param handler_method: Method to be called on every occurrence of `${LogicalId}` structure within the string.
            Implementation could resolve and replace this structure with whatever they seem fit
        :return: Resolved value of the Sub dictionary
        """

        # Just handle known references within the string to be substituted and return the whole dictionary
        # because that's the best we can do here.
        if isinstance(sub_value, string_types):
            # Ex: {Fn::Sub: "some string"}
            sub_value = self._sub_all_refs(sub_value, handler_method)

        elif isinstance(sub_value, list) and len(sub_value) > 0 and isinstance(sub_value[0], string_types):
            # Ex: {Fn::Sub: ["some string", {a:b}] }
            sub_value[0] = self._sub_all_refs(sub_value[0], handler_method)

        return sub_value

    def _sub_all_refs(self, text, handler_method):
        """
        Substitute references within a string that is using ${key} syntax by calling the `handler_method` on every
        occurrence of this structure. The value returned by this method directly replaces the reference structure.
        Ex:
            text = "${key1}-hello-${key2}
            def handler_method(full_ref, ref_value):
                return "foo"
            _sub_all_refs(text, handler_method) will output "foo-hello-foo"
        :param string text: Input text
        :param handler_method: Method to be called to handle each occurrence of ${blah} reference structure.
            First parameter to this method is the full reference structure Ex: ${LogicalId.Property}. Second parameter is just the
            value of the reference such as "LogicalId.Property"
        :return string: Text with all reference structures replaced as necessary
        """

        # RegExp to find pattern "${logicalId.property}" and return the word inside bracket
        logical_id_regex = '.*'
        ref_pattern = re.compile(r'\$\{('+logical_id_regex+')\}')

        return re.sub(ref_pattern,
                      # Pass the handler entire string ${logicalId.property} as first parameter and "logicalId.property"
                      # as second parameter. Return value will be substituted
                      lambda match: handler_method(match.group(0), match.group(1)),
                      text)


class SamBaseProvider(object):
    """
    Base class for SAM Template providers
    """

    # There is not much benefit in infering real values for these parameters in local development context. These values
    # are usually representative of an AWS environment and stack, but in local development scenario they don't make
    # sense. If customers choose to, they can always override this value through the CLI interface.
    _DEFAULT_PSEUDO_PARAM_VALUES = {
        "AWS::AccountId": "123456789012",
        "AWS::Partition": "aws",

        "AWS::Region": "us-east-1",

        "AWS::StackName": "local",
        "AWS::StackId": "arn:aws:cloudformation:us-east-1:123456789012:stack/"
                        "local/51af3dc0-da77-11e4-872e-1234567db123",
        "AWS::URLSuffix": "localhost"
    }

    # Only Ref is supported when resolving template parameters
    _SUPPORTED_INTRINSICS = [RefAction, SubAction]

    @staticmethod
    def get_template(template_dict, parameter_overrides=None):
        """
        Given a SAM template dictionary, return a cleaned copy of the template where SAM plugins have been run
        and parameter values have been substituted.

        Parameters
        ----------
        template_dict : dict
            unprocessed SAM template dictionary

        parameter_overrides: dict
            Optional dictionary of values for template parameters

        Returns
        -------
        dict
            Processed SAM template
        """

        template_dict = template_dict or {}
        if template_dict:
            template_dict = SamTranslatorWrapper(template_dict).run_plugins()

        template_dict = SamBaseProvider._resolve_parameters(template_dict, parameter_overrides)
        ResourceMetadataNormalizer.normalize(template_dict)

        LOG.info(str(template_dict))
        return template_dict

    @staticmethod
    def _resolve_parameters(template_dict, parameter_overrides):
        """
        In the given template, apply parameter values to resolve intrinsic functions

        Parameters
        ----------
        template_dict : dict
            SAM Template

        parameter_overrides : dict
            Values for template parameters provided by user

        Returns
        -------
        dict
            Resolved SAM template
        """

        parameter_values = SamBaseProvider._get_parameter_values(template_dict, parameter_overrides)

        supported_intrinsics = {action.intrinsic_name: action() for action in SamBaseProvider._SUPPORTED_INTRINSICS}

        # Intrinsics resolver will mutate the original template
        return IntrinsicsResolver(parameters=parameter_values, supported_intrinsics=supported_intrinsics)\
            .resolve_parameter_refs(template_dict)

    @staticmethod
    def _get_parameter_values(template_dict, parameter_overrides):
        """
        Construct a final list of values for CloudFormation template parameters based on user-supplied values,
        default values provided in template, and sane defaults for pseudo-parameters.

        Parameters
        ----------
        template_dict : dict
            SAM template dictionary

        parameter_overrides : dict
            User-supplied values for CloudFormation template parameters

        Returns
        -------
        dict
            Values for template parameters to substitute in template with
        """

        default_values = SamBaseProvider._get_default_parameter_values(template_dict)

        # NOTE: Ordering of following statements is important. It makes sure that any user-supplied values
        # override the defaults
        parameter_values = {}
        parameter_values.update(SamBaseProvider._DEFAULT_PSEUDO_PARAM_VALUES)
        parameter_values.update(default_values)
        parameter_values.update(parameter_overrides or {})

        return parameter_values

    @staticmethod
    def _get_default_parameter_values(sam_template):
        """
        Method to read default values for template parameters and return it
        Example:
        If the template contains the following parameters defined
        Parameters:
            Param1:
                Type: String
                Default: default_value1
            Param2:
                Type: String
                Default: default_value2

        then, this method will grab default value for Param1 and return the following result:
        {
            Param1: "default_value1",
            Param2: "default_value2"
        }
        :param dict sam_template: SAM template
        :return dict: Default values for parameters
        """

        default_values = {}

        parameter_definition = sam_template.get("Parameters", None)
        if not parameter_definition or not isinstance(parameter_definition, dict):
            LOG.debug("No Parameters detected in the template")
            return default_values

        for param_name, value in parameter_definition.items():
            if isinstance(value, dict) and "Default" in value:
                default_values[param_name] = value["Default"]

        LOG.debug("Collected default values for parameters: %s", default_values)
        return default_values
