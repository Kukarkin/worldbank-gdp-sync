
import os
import requests
import pandas as pd
import boto3
from io import StringIO
from datetime import datetime, timedelta

bucket_name = os.environ.get('YANDEX_BUCKET_NAME', 'worldbank-data')
access_key_id = os.environ.get('YANDEX_ACCESS_KEY_ID', 'your-access-key-here')
secret_access_key = os.environ.get('YANDEX_SECRET_ACCESS_KEY', 'your-secret-key-here')
endpoint_url = os.environ.get('YANDEX_ENDPOINT_URL', 'https://storage.yandexcloud.net')

def get_worldbank_gdp():
    url = 'https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.PP.KD?format=json&per_page=20000'
    response = requests.get(url)
    data = response.json()

    if not data or len(data) < 2:
        raise Exception('Ошибка получения данных API')


    update_time = (datetime.utcnow() + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S')

    rows = []
    for item in data[1]:
        if item['value'] is not None:
            rows.append({
                'Country ID': item['country']['id'],
                'Country Name': item['country']['value'],
                'Year': item['date'],
                'GDP PPP constant 2021 $': item['value'],
                'Updated At': update_time
            })

    df = pd.DataFrame(rows)
    return df

def upload_to_s3(df):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)

    s3 = boto3.client('s3',
                      endpoint_url=endpoint_url,
                      aws_access_key_id=access_key_id,
                      aws_secret_access_key=secret_access_key)

    s3.put_object(Bucket=bucket_name, Key='worldbank_gdp.csv', Body=csv_buffer.getvalue())
    print(f'Файл успешно загружен в бакет {bucket_name}')

if __name__ == "__main__":
    df = get_worldbank_gdp()
    upload_to_s3(df)
