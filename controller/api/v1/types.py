from dataclasses import dataclass, field
from apischema import schema
from typing import NewType
from ..schema import OpenAPIV3Schema


# Static route API representation
# Final CRD is generated upon below dataclass via `make manifests` command
# WIP


@dataclass
class StaticRoute(OpenAPIV3Schema):
    __group__ = "networking.digitalocean.com"
    __version__ = "v1"
    __scope__ = "Cluster"
    __short_names__ = ["sr"]

    __additional_printer_columns__ = [
        {
            "name": "Age",
            "type": "date",
            "priority": 0,
            "jsonPath": ".metadata.creationTimestamp",
        },
        {
            "name": "Destinations",
            "type": "string",
            "priority": 1,
            "description": "Destination host(s)/subnet(s)",
            "jsonPath": ".spec.destinations",
        },
        {
            "name": "Gateway",
            "type": "string",
            "priority": 1,
            "description": "Gateway to route through",
            "jsonPath": ".spec.gateway",
        },
        {
            "name": "ClusterService",
            "type": "string",
            "priority": 1,
            "description": "Cluster Service to route to (i.e. wireguard service)",
            "jsonPath": ".spec.clusterservice",
        },
    ]

    Destination = NewType("Destination", str)
    schema(
        pattern="^([0-9]{1,3}\.){3}[0-9]{1,3}$|^([0-9]{1,3}\.){3}[0-9]{1,3}(\/([0-9]|[1-2][0-9]|3[0-2]))?$",
    )(Destination)

    destinations: list[Destination] = field(
        metadata=schema(
            description="Destination host(s)/subnet(s) to route through the gateway (required)",
        )
    )
    gateway: str = field(
        metadata=schema(
            description="Gateway to route through (required (unless using ClusterService) )",
            pattern="^([0-9]{1,3}\.){3}[0-9]{1,3}$",
        )
    )
    clusterservice: str = field(
        metadata=schema(
            description="ClusterService to route through (required (unless using Gateway) )",
            example="wireguard.namespace<.svc.cluster.local>",
            pattern="^([a-z0-9\.]+)$",
        )
    )
