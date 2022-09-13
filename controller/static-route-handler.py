import kopf
from pyroute2 import IPRoute
from api.v1.types import StaticRoute
from constants import DEFAULT_GW_CIDR, NOT_USABLE_IP_ADDRESS, ROUTE_READY_MSG, ROUTE_NOT_READY_MSG


# =================================== Static route management ===========================================
#
# Works the same way as Linux `ip route` subcommands:
#  - "add":     Adds a new entry in the Linux routing table (must not exist beforehand)
#  - "change":  Changes an entry from the the Linux routing table (must exist beforehand)
#  - "delete":  Deletes an entry from the Linux routing table (must exist beforehand)
#  - "replace": Replaces an entry from the Linux routing table if it exists, creates a new one otherwise
#
# =======================================================================================================

def manage_static_route(operation, destination, gateway, logger=None):
    operation_success = False
    message = ''

    # We don't want to mess with default GW settings, or with '0.0.0.0' IP address
    if DEFAULT_GW_CIDR in destination or NOT_USABLE_IP_ADDRESS in destination:
        operation_success = False
        message = f"Route {operation} request denied - dest: {destination}, gateway: {gateway}!"
        if logger is not None:
            logger.error(message)
        return (operation_success, message)

    with IPRoute() as ipr:
        try:
            ipr.route(operation, dst=destination, gateway=gateway)
            operation_success = True
            message = f"Success - Dest: {destination}, gateway: {gateway}, operation: {operation}."
            if logger is not None:
                logger.info(message)
        except Exception as ex:
            operation_success = False
            message = f"Route {operation} failed! Error message: {ex}"
            if logger is not None:
                logger.error(message)

    return (operation_success, message)


# ============================== Create Handler =====================================
#
# Default behavior is to "add" the static route specified in our CRD only!
# If the static route already exists, it will not be overwritten.
#
# ===================================================================================

@kopf.on.resume(StaticRoute.__group__, StaticRoute.__version__, StaticRoute.__name__)
@kopf.on.create(StaticRoute.__group__, StaticRoute.__version__, StaticRoute.__name__)
def create_fn(body, spec, logger, **kwargs):
    add_operation_succeeded, message = manage_static_route(
        operation="add",
        destination=spec['destination'],
        gateway=spec['gateway'],
        logger=logger
    )

    if not add_operation_succeeded:
        kopf.exception(
            body,
            reason='RouteCreateFailed',
            message=message
        )
        return ROUTE_NOT_READY_MSG

    kopf.info(
        body,
        reason='RouteCreateSucceeded',
        message=message
    )
    return ROUTE_READY_MSG


# ============================== Update Handler =====================================
#
# Default behavior is to update/replace the static route specified in our CRD only!
#
# ===================================================================================

@kopf.on.update(StaticRoute.__group__, StaticRoute.__version__, StaticRoute.__name__)
def update_fn(body, old, new, logger, **kwargs):
    delete_operation_succeeded, message = manage_static_route(
        operation="del",
        destination=old['spec']['destination'],
        gateway=old['spec']['gateway'],
        logger=logger
    )

    add_operation_succeeded, message = manage_static_route(
        operation="add",
        destination=new['spec']['destination'],
        gateway=new['spec']['gateway'],
        logger=logger
    )

    # 'delete' op may fail because route is not allowed, or doesn't exist anymore 
    # 'add' op status is most relevant
    if not add_operation_succeeded:
        kopf.exception(
            body,
            reason='RouteUpdateFailed',
            message=message
        )
        return ROUTE_NOT_READY_MSG

    kopf.info(
        body,
        reason='RouteUpdateSucceeded',
        message=message
    )
    return ROUTE_READY_MSG


# ============================== Delete Handler =====================================
#
# Default behavior is to delete the static route specified in our CRD only!
#
# ===================================================================================

@kopf.on.delete(StaticRoute.__group__, StaticRoute.__version__, StaticRoute.__name__)
def delete(body, spec, logger, **kwargs):
    delete_operation_succeeded, message = manage_static_route(
        operation="del",
        destination=spec['destination'],
        gateway=spec['gateway'],
        logger=logger
    )

    if not delete_operation_succeeded:
        kopf.exception(
            body,
            reason='RouteDeleteFailed',
            message=message
        )
