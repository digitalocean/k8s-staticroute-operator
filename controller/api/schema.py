from apischema.json_schema import deserialization_schema
import yaml
import json

# WIP
# More or less primitive way of doing serialization
class OpenAPIV3Schema():
    @classmethod
    def api_schema(cls):
        return deserialization_schema(
            cls,
            all_refs=False,
            additional_properties=True,
            with_schema=False
        )

    @classmethod
    def singular(cls):
        return cls.__name__.lower()

    @classmethod
    def plural(cls):
        return f'{cls.singular()}s'

    @classmethod
    def crd_schema(cls):
        crd = {
            'apiVersion': 'apiextensions.k8s.io/v1',
            'kind': 'CustomResourceDefinition',
            'metadata': {
                'name': f'{cls.plural()}.{cls.__group__}',
            },
            'spec': {
                'group': cls.__group__,
                'scope': cls.__scope__,
                'names': {
                    'kind': cls.__name__,
                    'singular': cls.singular(),
                    'plural': cls.plural(),
                    'shortNames': cls.__short_names__,
                },
                'versions': [
                    {
                        'name': cls.__version__,
                        'served': True,
                        'storage': True,
                        'schema': {
                            'openAPIV3Schema': {
                                'type': 'object',
                                'properties': {
                                    'spec': cls.api_schema(),
                                    'status': {
                                        'x-kubernetes-preserve-unknown-fields': True,
                                        'type': 'object',
                                    },
                                },
                            },
                        },
                        'additionalPrinterColumns': cls.__additional_printer_columns__,
                    },
                ],
            },
        }
        return yaml.dump(
            yaml.load(json.dumps(crd), Loader=yaml.Loader),
            Dumper=yaml.Dumper,
        )
