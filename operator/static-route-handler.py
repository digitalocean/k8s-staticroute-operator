import kopf
from pyroute2 import IPRoute


def create_static_route(body, destination, gateway, logger):
    status = 'Unknown'

    with IPRoute() as ipr:
        try:
            ipr.route("add", dst=destination, gateway=gateway)
            logger.info(f"Route - dst: {destination}, gateway: {gateway} created successfully!")
            kopf.info(
                body,
                reason='RouteCreationSucceeded',
                message=f"Destination {destination} will be routed via {gateway} gateway now."
            )
            status = 'Ready'
        except Exception as ex:
            logger.error(f"Route creation failed! Error message: {ex}")
            kopf.exception(body, reason='RouteCreationFailed', message=f"{ex}")
            status = 'NotReady'
    return status

def delete_static_route(destination, gateway, logger):
    with IPRoute() as ipr:
        try:
            ipr.route("del", dst=destination, gateway=gateway)
            logger.info(f"Route - dst: {destination}, gateway: {gateway} deleted successfully!")
        except Exception as ex:
            logger.error(f"Route deletion failed! Error message: {ex}")

@kopf.on.resume('kopf.dev', 'staticroutes')
@kopf.on.create('kopf.dev', 'staticroutes')
def create_fn(body, spec, logger, **kwargs):
    status = create_static_route(body, spec['destination'], spec['gateway'], logger)
    return {'routeStatus': status}

@kopf.on.update('kopf.dev', 'staticroutes')
def update_fn(body, old, new, logger, **kwargs):
    delete_static_route(old['spec']['destination'], old['spec']['gateway'], logger)
    status = create_static_route(body, new['spec']['destination'], new['spec']['gateway'], logger)
    return {'routeStatus': status}

@kopf.on.delete('kopf.dev', 'staticroutes')
def delete(spec, logger, **kwargs):
    delete_static_route(spec['destination'], spec['gateway'], logger)
