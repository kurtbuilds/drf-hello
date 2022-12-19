from typing import Optional, List, cast, Any, Callable, get_origin, get_args, Union

from django.http import HttpRequest
from pydantic import BaseModel
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.schemas.openapi import AutoSchema
import inspect

empty = inspect.Signature.empty


def is_optional(type_):
    """Check if a type is an Optional."""
    return get_origin(type_) is Union and type(None) in get_args(type_)


def unwrap_optional(type_):
    """Unwrap an optional type."""
    if is_optional(type_):
        return [t for t in get_args(type_) if not isinstance(t, type(None))][0]
    else:
        return type_


def get_schema_for_type(type_: Any) -> Any:
    """Get the schema for a type."""
    type_ = unwrap_optional(type_)
    if issubclass(type_, BaseModel):
        return type_.schema()
    elif type_ == str:
        return {"type": "string"}
    elif type_ == int:
        return {"type": "integer"}
    elif type_ == float:
        return {"type": "number"}
    elif type_ == bool:
        return {"type": "boolean"}
    elif type_ is empty:
        return {}
    else:
        raise NotImplementedError(f"Type {type_} not implemented")


class TypedSchema(AutoSchema):
    def __init__(self, original_fn: Callable):
        super().__init__()
        self.original_fn = original_fn

    def get_operation_id(self, path, method):
        return self.original_fn.__module__.split(".", 2)[1] + '.' + self.original_fn.__name__

    def get_description(self, path, method):
        return self.original_fn.__doc__

    def get_responses(self, path, method):
        pass

    def get_filter_parameters(self, path, method):
        return super().get_filter_parameters(path, method)

    def get_pagination_parameters(self, path, method):
        return super().get_pagination_parameters(path, method)

    def get_request_body(self, path, method):
        result = super().get_request_body(path, method)
        if not result:
            return result
        signature = inspect.signature(self.original_fn)
        for media_type, schema in result["content"].items():
            properties = {}
            for param in signature.parameters.values():
                field = param.name
                properties[field] = get_schema_for_type(param.annotation)
            required = [p.name for p in signature.parameters.values()
                        if (p.default is empty and not is_optional(p.annotation))]

            schema["schema"] = {
                "type": "object",
                "properties": properties,
                "required": required,
            }
        return result


def build_view(f: Callable, methods: Optional[List[str]] = None):
    """Implementation of .view() function (from `derive_view`).

    Creates the callable that django uses for the request.
    """
    anno = f.__annotations__
    # print(f.__annotations__)

    call_dict = False
    return_val = anno.get("return")
    if return_val is not None and issubclass(return_val, BaseModel):
        call_dict = True
        # return_val = return_val.schema()

    def view(request: HttpRequest) -> Response:
        result = f(request)
        if call_dict:
            result = result.dict()
        return Response(result)

    view.schema = TypedSchema(f)

    return api_view(methods)(view)


def derive_view(methods: Optional[List[str]] = None):
    """Adds a .view() method to a function, which can be passed to path(...).

    :param methods:
    :return:
    """
    call_decorator = callable(methods)
    if call_decorator:
        f = cast(Callable, methods)
        methods = ["GET"]

        f.view = lambda: build_view(f, methods)
        return f
    else:
        def decorator(f: Callable):
            f.view = lambda: build_view(f, methods)
            return f

        return decorator


class SendSmsResponse(BaseModel):
    account_found: bool


@derive_view(["POST"])
def send_sms_code1(bare: Optional[str], mobile: str = "foo") -> SendSmsResponse:
    """ Docs n shit """
    print('hi')
    return SendSmsResponse(account_found=True)


@derive_view
def send_sms_code2(mobile: str = 'bar') -> SendSmsResponse:
    return SendSmsResponse(account_found=True)
