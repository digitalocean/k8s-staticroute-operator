DEFAULT_GW_CIDR = "0.0.0.0/0"
NOT_USABLE_IP_ADDRESS = "0.0.0.0"

ROUTE_READY_MSG = "Ready"
ROUTE_NOT_READY_MSG = "NotReady"
ROUTE_EVT_MSG = {
    "add": {"success": "RouteCreateSucceeded", "failure": "RouteCreateFailed"},
    "del": {"success": "RouteDeleteSucceeded", "failure": "RouteDeleteFailed"},
}
