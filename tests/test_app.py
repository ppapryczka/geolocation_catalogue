import pytest
import responses
from .conftest import (
    IP_STACK_RESPONSES,
    TEST_IP_STACK_API_ACCESS_KEY,
    insert_into_database,
    get_ip_geolocation_from_db,
)
from geolocation_catalogue.schemas import GeolocationSchema
from fastapi import Response
from copy import deepcopy
from fastapi import status


def check_response_against_data(response: Response, ip: str, data: dict) -> None:
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json["ip"] == ip
    for k in response_json["geolocation"]:
        assert response_json["geolocation"][k] == data[k]


def check_response_again_database(response: Response, ip: str) -> None:
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    geolocation = get_ip_geolocation_from_db(ip=ip)
    assert geolocation
    for k in response_json["geolocation"]:
        assert response_json["geolocation"][k] == geolocation.geolocation[k]


@pytest.mark.parametrize("address", ["155.52.187.7", "google.com"])
def test_get_address_geolocation_empty_catalogue(test_app, address: str) -> None:
    response = test_app.get("/address", params={"address": address})
    assert response.status_code == 404
    assert response.json()["detail"] == "Geolocation for address not found."


@pytest.mark.parametrize(
    "address", ["http://test.123/aaa", "http://test.com/aaa", "155.52.187.7.2"]
)
def test_get_address_geolocation_wrong_address_value(test_app, address: str) -> None:
    response = test_app.get("/address", params={"address": address})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "ip, ip_stack_response", [(k, IP_STACK_RESPONSES[k]) for k in IP_STACK_RESPONSES]
)
@responses.activate
def test_get_address_geolocation_empty_catalogue_ip_stack_call_on(
    test_app_ip_stack_on, ip: str, ip_stack_response: dict
) -> None:
    responses.add(
        responses.GET,
        f"https://api.ipstack.com/{ip}?access_key={TEST_IP_STACK_API_ACCESS_KEY}&fields=main",
        json=ip_stack_response,
        status=200,
    )

    response = test_app_ip_stack_on.get("/address", params={"address": ip})

    check_response_against_data(response, ip, ip_stack_response)


@pytest.mark.parametrize(
    "ip, ip_stack_response", [(k, IP_STACK_RESPONSES[k]) for k in IP_STACK_RESPONSES]
)
def test_get_address_geolocation(test_app, ip, ip_stack_response):
    insert_into_database(ip, ip_stack_response)

    response = test_app.get("/address", params={"address": ip})

    check_response_against_data(response, ip, ip_stack_response)


@pytest.mark.parametrize(
    "ip, ip_stack_response", [(k, IP_STACK_RESPONSES[k]) for k in IP_STACK_RESPONSES]
)
def test_put_address_geolocation_new_entry(test_app, ip, ip_stack_response):
    data = GeolocationSchema(**ip_stack_response)
    response = test_app.put("/address", params={"address": ip}, json=data.model_dump())

    check_response_against_data(response, ip, ip_stack_response)
    check_response_again_database(response, ip)


@pytest.mark.parametrize(
    "ip, ip_stack_response", [(k, IP_STACK_RESPONSES[k]) for k in IP_STACK_RESPONSES]
)
def test_put_address_geolocation_update_entry(test_app, ip, ip_stack_response):
    insert_into_database(ip, ip_stack_response)

    request_data = deepcopy(ip_stack_response)
    request_data["city"] = "test"
    data = GeolocationSchema(**request_data)
    response = test_app.put("/address", params={"address": ip}, json=data.model_dump())

    check_response_against_data(response, ip, request_data)
    check_response_again_database(response, ip)


@pytest.mark.parametrize("ip", list(IP_STACK_RESPONSES))
def test_delete_address_geolocation_not_existing(test_app, ip):
    response = test_app.delete("/address", params={"address": ip})

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "ip, ip_stack_response", [(k, IP_STACK_RESPONSES[k]) for k in IP_STACK_RESPONSES]
)
def test_delete_address_geolocation_existing(test_app, ip, ip_stack_response):
    insert_into_database(ip, ip_stack_response)
    response = test_app.delete("/address", params={"address": ip})

    assert response.status_code == status.HTTP_204_NO_CONTENT
