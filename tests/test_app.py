from copy import deepcopy

import pytest
import responses
from fastapi import Response, status
from fastapi.testclient import TestClient

from geolocation_catalogue.schemas import GeolocationSchema

from .conftest import (
    IP_STACK_RESPONSES,
    TEST_IP_STACK_API_ACCESS_KEY,
    get_ip_geolocation_from_db,
    insert_into_database,
)


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
def test_get_address_geolocation_empty_catalogue(
    test_app: TestClient, address: str
) -> None:
    response = test_app.get("/address", params={"address": address})
    assert response.status_code == 404
    assert response.json()["detail"] == "Geolocation for address not found."


@pytest.mark.parametrize(
    "address", ["http://test.123/aaa", "http://test.com/aaa", "155.52.187.7.2"]
)
def test_get_address_geolocation_wrong_address_value(
    test_app: TestClient, address: str
) -> None:
    response = test_app.get("/address", params={"address": address})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize(
    "ip, ip_stack_response", [(k, IP_STACK_RESPONSES[k]) for k in IP_STACK_RESPONSES]
)
@responses.activate
def test_get_address_geolocation_empty_catalogue_ip_stack_call_on(
    test_app_ip_stack_on: TestClient, ip: str, ip_stack_response: dict
) -> None:
    responses.add(
        responses.GET,
        f"https://api.ipstack.com/{ip}?access_key={TEST_IP_STACK_API_ACCESS_KEY}&fields=main",
        json=ip_stack_response,
        status=200,
    )

    response = test_app_ip_stack_on.get("/address", params={"address": ip})

    check_response_against_data(response, ip, ip_stack_response)


@responses.activate
def test_get_address_geolocation_ip_stack_call_on_not_found_error(
    test_app_ip_stack_on: TestClient,
) -> None:
    ip = "216.58.209.4"
    ip_stack_not_found = {
        "success": False,
        "error": {"code": 404, "type": "404_not_found", "info": ""},
    }

    responses.add(
        responses.GET,
        f"https://api.ipstack.com/{ip}?access_key={TEST_IP_STACK_API_ACCESS_KEY}&fields=main",
        json=ip_stack_not_found,
        status=200,
    )

    response = test_app_ip_stack_on.get("/address", params={"address": ip})
    assert response.status_code == status.HTTP_404_NOT_FOUND


@responses.activate
def test_get_address_geolocation_ip_stack_call_on_success_false(
    test_app_ip_stack_on: TestClient,
) -> None:
    ip = "216.58.209.4"
    ip_stack_106 = {
        "success": False,
        "error": {
            "code": 106,
            "type": "invalid_ip_address",
            "info": "The IP Address supplied is invalid.",
        },
    }

    responses.add(
        responses.GET,
        f"https://api.ipstack.com/{ip}?access_key={TEST_IP_STACK_API_ACCESS_KEY}&fields=main",
        json=ip_stack_106,
        status=200,
    )

    response = test_app_ip_stack_on.get("/address", params={"address": ip})
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.parametrize(
    "ip, ip_stack_response", [(k, IP_STACK_RESPONSES[k]) for k in IP_STACK_RESPONSES]
)
def test_get_address_geolocation(
    test_app: TestClient, ip: str, ip_stack_response: dict
) -> None:
    insert_into_database(ip, ip_stack_response)

    response = test_app.get("/address", params={"address": ip})

    check_response_against_data(response, ip, ip_stack_response)


@pytest.mark.parametrize(
    "ip, ip_stack_response", [(k, IP_STACK_RESPONSES[k]) for k in IP_STACK_RESPONSES]
)
def test_put_address_geolocation_new_entry(
    test_app: TestClient, ip: str, ip_stack_response: dict
) -> None:
    data = GeolocationSchema(**ip_stack_response)
    response = test_app.put("/address", params={"address": ip}, json=data.model_dump())

    check_response_against_data(response, ip, ip_stack_response)
    check_response_again_database(response, ip)


@pytest.mark.parametrize(
    "ip, ip_stack_response", [(k, IP_STACK_RESPONSES[k]) for k in IP_STACK_RESPONSES]
)
def test_put_address_geolocation_update_entry(
    test_app: TestClient, ip: str, ip_stack_response: dict
) -> None:
    insert_into_database(ip, ip_stack_response)

    request_data = deepcopy(ip_stack_response)
    request_data["city"] = "test"
    data = GeolocationSchema(**request_data)
    response = test_app.put("/address", params={"address": ip}, json=data.model_dump())

    check_response_against_data(response, ip, request_data)
    check_response_again_database(response, ip)


@pytest.mark.parametrize("ip", list(IP_STACK_RESPONSES))
def test_delete_address_geolocation_not_existing(test_app: TestClient, ip: str) -> None:
    response = test_app.delete("/address", params={"address": ip})

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.parametrize(
    "ip, ip_stack_response", [(k, IP_STACK_RESPONSES[k]) for k in IP_STACK_RESPONSES]
)
def test_delete_address_geolocation_existing(
    test_app: TestClient, ip: str, ip_stack_response: dict
) -> None:
    insert_into_database(ip, ip_stack_response)
    response = test_app.delete("/address", params={"address": ip})

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not get_ip_geolocation_from_db(ip)


def test_delete_address_geolocation_multiple_existing(test_app: TestClient) -> None:
    for k in IP_STACK_RESPONSES:
        insert_into_database(k, IP_STACK_RESPONSES[k])

    ip = list(IP_STACK_RESPONSES.keys())[0]
    response = test_app.delete("/address", params={"address": ip})

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not get_ip_geolocation_from_db(ip)
