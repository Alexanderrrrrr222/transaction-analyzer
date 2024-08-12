# @title
import psycopg2
from psycopg2 import sql
import requests
import datetime

conn = psycopg2.connect(
    dbname='lzkcgkmf',
    user='lzkcgkmf',
    password='JOKVdd4_rheWsndLCV8VqZ6zyD5Y0nr0',
    host='ella.db.elephantsql.com'
)
cur = conn.cursor()

api_key = '7a65bfa6-750b-4490-be79-b47a31c235a9'
endpoint = 'https://apilist.tronscanapi.com/api/transaction-info'

transaction_hash = input('Введите HASH транзакции: ')


cur.execute(
    sql.SQL("SELECT EXISTS (SELECT 1 FROM hash_table WHERE hash = %s)")
    .format(sql.Identifier('hash')),
    [transaction_hash]
)
exists = cur.fetchone()[0]

if exists:
    print('⚠️⚠️⚠️Внимание HASH уже использовался ранее при пополнении⚠️⚠️⚠️')
else:
    print('✅ HASH не использовался ранее ✅')

headers = {
    'TRON-PRO-API-KEY': api_key
}

params = {
    'hash': transaction_hash
}

response = requests.get(endpoint, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()

    if 'trc20TransferInfo' in data:
        trc20_info = data['trc20TransferInfo']
        if trc20_info:
            amount_str = trc20_info[0].get('amount_str')
            to_address = trc20_info[0].get('to_address')
            timestamp = data.get('timestamp')

            # print('Сумма в блокчейне:', amount_str)
            # print('Получатель средств:', to_address)

            if to_address != 'TM4GjqKvoneHmvMYoLVjRXMdUQo5nCe55x':
                print
                (
                    '''
                      ⚠️⚠️⚠️ Внимание:
                      Кошелёк получателя отличается от
                      TM4GjqKvoneHmvMYoLVjRXMdUQo5nCe55x ⚠️⚠️⚠️
                    '''
                )
            else:
                print
                (
                    '''
                    ✅ Перевод выполнен на актуальный кошелёк
                    TM4GjqKvoneHmvMYoLVjRXMdUQo5nCe55x ✅
                    '''
                )

                if 'confirmed' in data and 'timestamp' in data:
                    confirmed_value = data['confirmed']

                    if confirmed_value is True:
                        print('✅ Перевод выполнен успешно ✅')

                        transaction_time = datetime.datetime.fromtimestamp(
                            int(timestamp) / 1000.0
                        )
                        current_time = datetime.datetime.now()
                        transatction_delta = current_time - transaction_time
                        if (
                            transatction_delta > datetime.timedelta(hours=1)
                        ):
                            print(
                                '''
                                ⚠️⚠️⚠️ Этот перевод старше одного часа.
                                Возможно дублирование HASH от партнёра ⚠️⚠️⚠️
                                '''
                            )
                        if transatction_delta < datetime.timedelta(hours=1):
                            print('✅ Перевод выполнен недавно ✅')

                        num_amount = float(
                            amount_str[:-6] + '.' + amount_str[-6:]
                        )

                        exchange_rate = float(
                            input('Введите курс для расчета суммы: ')
                        )

                        tariff_percent = float(
                            input('Введите процент по тарифу: ')
                        )

                        total = num_amount * exchange_rate
                        total = round(total, 2)

                        total2 = total + (total * tariff_percent / 100)
                        total2 = round(total2, 2)

                        if total2.is_integer():
                            total2 = int(total2)

                        print(
                            f'''{num_amount} * {exchange_rate}
                            = {total} + {tariff_percent}% =
                            {total2 if isinstance(total2, int)
                            else total2:.2f}'''
                        )

                        cur.execute(
                            sql.SQL(
                                "INSERT INTO hash_table (hash) VALUES (%s)"
                            ).format(sql.Identifier('hash')),
                            [transaction_hash]
                        )
                        conn.commit()
                else:
                    print(
                        '''❌ Информация о подтверждении перевода отсутствует
                        в ответе API ❌'''
                    )
        else:
            print('❌ Информация о переводе TRC20 отсутствует в ответе API ❌')
    else:
        print('❌ Информация о переводе TRC20 отсутствует в ответе API ❌')
else:
    print('❌ Ошибка, возможно не доступен API:', response.status_code)

cur.close()
conn.close()
