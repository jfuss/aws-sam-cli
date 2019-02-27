from unittest import TestCase

from samcli.commands.local.lib.sam_base_provider import SamBaseProvider


class TestTemplateWithSub(TestCase):

    def test_template_with_sub(self):
        template = {
            "Resources": {
                "FunctionA": {
                    "Type": "AWS::Serverless::Function",
                    "Properties": {
                        "Runtime": "python3.7",
                        "Handler": {
                            "Fn::Sub":
                                "Here is some string"
                        }
                    }
                }
            }
        }

        normailzed_template = SamBaseProvider.get_template(template)

        self.assertEqual("Here is some string", normailzed_template["Resources"]["FunctionA"]['Properties']['Handler'])

    def test_template_with_sub_default_value_sub(self):
        template = {
            "Resources": {
                "FunctionA": {
                    "Type": "AWS::Serverless::Function",
                    "Properties": {
                        "Runtime": "python3.7",
                        "Handler": {
                            "Fn::Sub":
                                "Here is some string ${AWS::Region}"
                        }
                    }
                }
            }
        }

        normailzed_template = SamBaseProvider.get_template(template)

        self.assertEqual("Here is some string us-east-1", normailzed_template["Resources"]["FunctionA"]['Properties']['Handler'])

    def test_template_with_sub_parameter_overrode_value(self):
        template = {
            "Parameters": {
                "Handler": {
                    "Type": "String",
                }
            },
            "Resources": {
                "FunctionA": {
                    "Type": "AWS::Serverless::Function",
                    "Properties": {
                        "Runtime": "python3.7",
                        "Handler": {
                            "Fn::Sub":
                                "Here is some string ${Handler}"
                        }
                    }
                }
            }
        }

        normailzed_template = SamBaseProvider.get_template(template, {'Handler': "MyCustomHandler"})

        self.assertEqual("Here is some string MyCustomHandler", normailzed_template["Resources"]["FunctionA"]['Properties']['Handler'])

    def test_template_with_sub_parameter_default_value(self):
        template = {
            "Parameters": {
                "Handler": {
                    "Type": "String",
                    "Default": "MyDefaultHandler"
                }
            },
            "Resources": {
                "FunctionA": {
                    "Type": "AWS::Serverless::Function",
                    "Properties": {
                        "Runtime": "python3.7",
                        "Handler": {
                            "Fn::Sub":
                                "Here is some string ${Handler}"
                        }
                    }
                }
            }
        }

        normailzed_template = SamBaseProvider.get_template(template)

        self.assertEqual("Here is some string MyDefaultHandler", normailzed_template["Resources"]["FunctionA"]['Properties']['Handler'])
