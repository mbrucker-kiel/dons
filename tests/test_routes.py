from app import create_app


def test_home_route():
    app = create_app()
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200


def test_menu_route():
    app = create_app()
    client = app.test_client()
    response = client.get("/speisekarte")
    assert response.status_code == 200
