from dataclasses import dataclass, field
from apischema import schema
from ..schema import OpenAPIV3Schema


@dataclass
class StaticRoute(OpenAPIV3Schema):
    __group__ = 'networking.digitalocean.com'
    __version__ = 'v1'
    __scope__ = 'Cluster'
    __short_names__ = ['sr']

    __additional_printer_columns__ = [
        {
            'name': 'Destination',
            'type': 'string',
            'description': 'Destination host/subnet',
            'jsonPath': '.spec.destination',
        },
        {
            'name': 'Gateway',
            'type': 'string',
            'description': 'Gateway to route through',
            'jsonPath': '.spec.gateway',
        },
        {
            'name': 'Age',
            'type': 'date',
            'jsonPath': '.metadata.creationTimestamp',
        }
    ]

    destination: str = field(
        metadata=schema(
            description='Destination host/subnet to route through the gateway (required)',
            pattern='^([0-9]{1,3}\.){3}[0-9]{1,3}$|^([0-9]{1,3}\.){3}[0-9]{1,3}(\/([0-9]|[1-2][0-9]|3[0-2]))?$'
        )
    )
    gateway: str = field(
        metadata=schema(
            description='Gateway to route through (required)',
            pattern='^([0-9]{1,3}\.){3}[0-9]{1,3}$'
        )
    )
