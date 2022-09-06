import kopf
from pyroute2 import IPRoute
from api.v1.types import StaticRoute

ROUTE_READY_MSG = {'routeStatus': 'Ready'}
ROUTE_NOT_READY_MSG = {'routeStatus': 'NotReady'}


def create_static_route(destination, gateway, logger=None):
    success = False
    message = ''

    with IPRoute() as ipr:
        try:
            ipr.route("add", dst=destination, gateway=gateway)
            success = True
            message = f"Route - dst: {destination}, gateway: {gateway} created successfully!"
            if logger is not None:
                logger.info(message)
        except Exception as ex:
            success = False
            message = f"Route create failed! Error message: {ex}"
            if logger is not None:
                logger.error(message)

    return (success, message)


def delete_static_route(destination, gateway, logger=None):
    success = False
    message = ''

    with IPRoute() as ipr:
        try:
            ipr.route("del", dst=destination, gateway=gateway)
            success = True
            message = f"Route - dst: {destination}, gateway: {gateway} deleted successfully!"
            if logger is not None:
                logger.info(message)
        except Exception as ex:
            success = False
            message = f"Route delete failed! Error message: {ex}"
            if logger is not None:
                logger.error(message)

    return (success, message)


@kopf.on.resume(StaticRoute.__group__, StaticRoute.__version__, StaticRoute.__name__)
@kopf.on.create(StaticRoute.__group__, StaticRoute.__version__, StaticRoute.__name__)
def create_fn(body, spec, logger, **kwargs):
    route_add_succeeded, message = create_static_route(
        spec['destination'],
        spec['gateway'],
        logger
    )

    if not route_add_succeeded:
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


@kopf.on.update(StaticRoute.__group__, StaticRoute.__version__, StaticRoute.__name__)
def update_fn(body, old, new, logger, **kwargs):
    route_delete_succeeded, message = delete_static_route(
        old['spec']['destination'],
        old['spec']['gateway'],
        logger
    )

    if not route_delete_succeeded:
        kopf.exception(
            body,
            reason='RouteDeleteFailed',
            message=message
        )
        return ROUTE_NOT_READY_MSG

    route_add_succeeded, message = create_static_route(
        new['spec']['destination'],
        new['spec']['gateway'],
        logger
    )

    if not route_add_succeeded:
        kopf.exception(
            body,
            reason='RouteCreateFailed',
            message=message
        )
        return ROUTE_NOT_READY_MSG

    kopf.info(
        body,
        reason='RouteUpdateSucceeded',
        message=message
    )
    return ROUTE_READY_MSG


@kopf.on.delete(StaticRoute.__group__, StaticRoute.__version__, StaticRoute.__name__)
def delete(body, spec, logger, **kwargs):
    route_delete_succeeded, message = delete_static_route(
        spec['destination'],
        spec['gateway'],
        logger
    )

    if not route_delete_succeeded:
        kopf.exception(
            body,
            reason='RouteDeleteFailed',
            message=message
        )
