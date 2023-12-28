import os

from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient import discovery


load_dotenv()

EMAIL_USER = os.environ["EMAIL"]
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

info = {
    "type": os.environ["TYPE"],
    "project_id": os.environ["PROJECT_ID"],
    "private_key_id": os.environ["PRIVATE_KEY_ID"],
    "private_key": os.environ["PRIVATE_KEY"],
    "client_email": os.environ["CLIENT_EMAIL"],
    "client_id": os.environ["CLIENT_ID"],
    "auth_uri": os.environ["AUTH_URI"],
    "token_uri": os.environ["TOKEN_URI"],
    "auth_provider_x509_cert_url": os.environ["AUTH_PROVIDER_X509_CERT_URL"],
    "client_x509_cert_url": os.environ["CLIENT_X509_CERT_URL"],
}


def auth():
    """Функция авторизации."""
    credentials = Credentials.from_service_account_info(info=info, scopes=SCOPES)
    # Создаём экземпляр класса Resource.
    service = discovery.build("sheets", "v4", credentials=credentials)
    return service, credentials


def create_spreadsheet(service):
    """Функция создания документа."""
    spreadsheet_body = {
        "properties": {  # Свойства документа
            "title": "Бюджет путешествий",
            "locale": "ru_RU",
        },
        "sheets": [
            {
                "properties": {
                    "sheetType": "GRID",
                    "sheetId": 0,
                    "title": "Отпуск 2077",
                    "gridProperties": {"rowCount": 100, "columnCount": 100},
                }
            }
        ],
    }
    request = service.spreadsheets().create(body=spreadsheet_body)
    response = request.execute()
    spreadsheet_id = response["spreadsheetId"]
    print("https://docs.google.com/spreadsheets/d/" + spreadsheet_id)
    return spreadsheet_id


def set_user_permissions(spreadsheet_id, credentials):
    permissions_body = {
        "type": "user",  # Тип учетных данных.
        "role": "writer",  # Права доступа для учётной записи.
        "emailAddress": EMAIL_USER,
    }

    drive_service = discovery.build("drive", "v3", credentials=credentials)

    drive_service.permissions().create(
        fileId=spreadsheet_id, body=permissions_body, fields="id"
    ).execute()


def spreadsheet_update_values(service, spreadsheetId):
    table_values = [
        ["Бюджет путешествий"],
        ["Весь бюджет", "5000"],
        ["Все расходы", "=SUM(E7:E30)"],
        ["Остаток", "=B2-B3"],
        ["Расходы"],
        ["Описание", "Тип", "Кол-во", "Цена", "Стоимость"],
        ["Перелет", "Транспорт", "2", "400", "=C7*D7"],
    ]

    request_body = {"majorDimension": "ROWS", "values": table_values}
    request = (
        service.spreadsheets()
        .values()
        .update(
            spreadsheetId=spreadsheetId,
            range="Отпуск 2077!A1:F20",
            valueInputOption="USER_ENTERED",
            body=request_body,
        )
    )
    request.execute()


def read_values(service, spreadsheet_id):
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range="Лист1!A1:F10")
        .execute()
    )
    return result["values"]


service, credentials = auth()
spreadsheetId = create_spreadsheet(service)
set_user_permissions(spreadsheetId, credentials)
spreadsheet_update_values(service, spreadsheetId)
