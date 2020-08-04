# TODO should be flask_oso

import functools
from flask import g, current_app, _app_ctx_stack, request, Request
from werkzeug.exceptions import Forbidden

import oso
from oso import OsoException

class Oso(oso.Oso):
    """Flask specific functionality for oso."""
    def __init__(self, app=None, *args, **kwargs):
        # TODO (dhatch): Figure out how to get oso (if this isn't oso subclass)
        self._app = app

        # TODO (dhatch): A few defaults for this dependending on what
        # other frameworks are in use.
        self._get_actor = lambda: g.current_user

        if self._app is not None:
            self.init_app(self._app)

        super().__init__(*args, **kwargs)
        self.register_class(Request)

        # TODO config parameters

    ## Initialization

    def init_app(self, app):
        app.teardown_appcontext(self.teardown)
        app.before_request(self._provide_oso)

    def set_get_actor(self, func):
        """Provide a function that oso will use to get the current actor."""
        self._get_actor = func

    ## Middleware-like functions that affect every request.

    def require_authorization(self, app=None):
        """Enforce authorization on every request."""
        if app is None:
            app = self.app

        app.after_request(self._require_authorization)

    def perform_route_authorization(self, app=None):
        """Perform route authorization before every request.

        Route authorization will call :py:meth:`oso.Oso.is_allowed` with the
        current request (from ``flask.request``) as the resource and the method
        (from ``flask.request.method``) as the action.
        """
        if app is None:
            app = self.app

        app.before_request(self._perform_route_authorization)

    ## During request decorator or functions.

    def skip_authorization(self, reason=None):
        """opt-out of authorization for the current request."""
        _authorize_called()

    def authorize(self, resource, *, actor=None, action=None):
        if actor is None:
            actor = self.current_actor

        if action is None:
            action = request.method

        # TODO (dhatch): Broader resource mapping functionality?
        # Special handling for flask request as a resource.
        if resource == request:
            resource = request._get_current_object()

        allowed = self.is_allowed(actor, action, resource)
        _authorize_called()

        if not allowed:
            raise Forbidden("Not authorized")

    @property
    def app(self):
        return self._app or current_app

    @property
    def current_actor(self):
        return self._get_actor()

    ## Before / after
    def _provide_oso(self):
        if not hasattr(_app_ctx_stack.top, "oso_flask_oso"):
            _app_ctx_stack.top.oso_flask_oso = self

    def _perform_route_authorization(self):
        self.authorize(resource=request)

    def _require_authorization(self, response):
        if not request.url_rule:
            # No rule matched this request
            # Skip requiring authorization.
            # NOTE: (dhatch) Confirm this is a safe behavior, think through edge
            # cases.
            return response

        if not getattr(_app_ctx_stack.top, "oso_flask_authorize_called", False):
            raise OsoException("Authorize not called.")

        return response

    def teardown(self, exception):
        pass


# Decorators

def authorize(func=None, /, *, resource, actor=None, action=None):
    if func is not None:
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            oso = _app_ctx_stack.top.oso_flask_oso

            oso.authorize(actor=actor, action=action, resource=resource)
            return func(*args, **kwargs)

        return wrap

    return functools.partial(authorize, actor=actor, action=action, resource=resource)

def skip_authorization(func=None, /, reason=None):
    if func is not None:
        @functools.wraps(func)
        def wrap(*args, **kwargs):
            oso = _app_ctx_stack.top.oso_flask_oso
            oso.skip_authorization(reason=reason)
            return func(*args, **kwargs)

        return wrap

    return functools.partial(skip_authorization, reason=reason)


# TODO (dhatch): First attempt here, change this up...
def authorize_route(self, func=None, /, *, actor=None, action=None, resource=None):
    """Flask authorize route decorator."""
    def decorate(f):
        partial_kwargs = {}
        if actor is not None:
            partial_kwargs['actor'] = actor

        if action is not None:
            partial_kwargs['action'] = action

        if resource is not None:
            partial_kwargs['resource'] = resource

        @functools.wraps(f)
        def call(*args, **kwargs):
            oso = _app_ctx_stack.top.oso_flask_oso
            # TODO (dhatch): Customize current user
            if 'actor' not in partial_kwargs:
                partial_kwargs['actor'] = g.current_user

            if {'actor', 'action', 'resource'} - set(partial_kwargs.keys()) == set():
                # If full set of arguments are provided, just call it and continue.
                oso.is_allowed(**partial_kwargs)
                return f(*args, **kwargs)

            # Otherwise, pass a partial to be evaluated in the route body.
            partial = functools.partial(authorize, **partial_kwargs)
            result = f(*args, **kwargs, authorize=partial)

            if not is_allowed_called:
                raise OsoException("Forgot to call authorize in protected function!")

            return result

        return call

    if func is not None:
        assert actor is None
        assert action is None
        assert resource is None

        return decorate(func)

    return decorate

def _authorize_called():
    """Mark current request as authorized."""
    _app_ctx_stack.top.oso_flask_authorize_called = True

class OsoSQLAlchemy:
    """SQLAlchemy oso integration"""
    def __init__(self, oso):
        self.oso = oso

