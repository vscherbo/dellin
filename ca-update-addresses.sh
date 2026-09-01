#!/bin/bash

. /usr/local/bin/bashlib

LOG=$(namename $0).log
exec 1>>$LOG 2>&1

# Настройки подключения к PostgreSQL
export PGHOST=vm-pg-devel
export PGPORT=5432
export PGUSER=arc_energo
export PGDATABASE=arc_energo

# Скрипт для обновления адресов контрагента с сайта ДЛ
# Использование: ./ca-update-addresses.sh <CA_ID>

# Проверка наличия аргумента
if [ $# -ne 1 ]; then
    logmsg ERROR "Необходимо указать CA_ID"
    exit 1
fi

CA_ID=$1

# Проверка, что CA_ID является числом
if ! [[ $CA_ID =~ ^[0-9]+$ ]]; then
    logmsg ERROR "CA_ID должен быть числом"
    exit 1
fi

logmsg INFO "Начинаем обновление адресов для контрагента CA_ID=$CA_ID"

# Шаг 1: Получение данных с сайта ДЛ
logmsg INFO "Шаг 1: Получение данных с сайта ДЛ..."
python3 get-address.py --ca_id=$CA_ID

# Проверка успешности выполнения Python скрипта
RC=$?
if [ $RC -ne 0 ]; then
    logmsg $RC "Не удалось выполнить get-address.py"
    exit 1
fi

# Проверка наличия созданного файла
FILE_NAME="ca_${CA_ID}_addr.csv"
if [ ! -f "$FILE_NAME" ]; then
    logmsg ERROR "Файл $FILE_NAME не найден"
    exit 1
fi

logmsg INFO "Файл $FILE_NAME успешно создан"

# Шаг 2: Работа с PostgreSQL
logmsg INFO "Шаг 2: Обновление данных в PostgreSQL..."

# Удаление старых JSON данных
logmsg INFO "Удаление старых JSON данных..."
psql -c "DELETE FROM ext.dl_addresses_json WHERE ca_id=$CA_ID;"

RC=$?
if [ $RC -ne 0 ]; then
    logmsg $RC "Ошибка при удалении данных из ext.dl_addresses_json"
    exit 1
fi

# Импорт CSV файла
logmsg INFO "Импорт данных из CSV..."
psql -c "\copy ext.dl_addresses_json FROM '$FILE_NAME' WITH (FORMAT CSV, DELIMITER '^');"

RC=$?
if [ $RC -ne 0 ]; then
    logmsg $RC "Ошибка при импорте CSV файла"
    exit 1
fi

# Удаление старых адресов
logmsg INFO "Удаление старых адресов..."
psql -c "DELETE FROM ext.dl_addresses WHERE ca_id=$CA_ID;"
RC=$?
if [ $RC -ne 0 ]; then
    logmsg $RC "Ошибка при удалении данных из ext.dl_addresses"
    exit 1
fi

# Вставка новых адресов из представления
logmsg INFO "Вставка новых адресов..."
psql -c "INSERT INTO ext.dl_addresses (SELECT *, 0 FROM shp.vw_dl_addresses WHERE ca_id=$CA_ID);"
RC=$?
if [ $RC -ne 0 ]; then
    logmsg $RC "Ошибка при вставке данных в ext.dl_addresses"
    exit 1
fi

logmsg INFO "Обновление адресов для контрагента CA_ID=$CA_ID успешно завершено!"

# Опционально: удаление временного CSV файла
# read -p "Удалить временный файл $FILE_NAME? (y/n): " -n 1 -r
# echo
# if [[ $REPLY =~ ^[Yy]$ ]]; then
#     rm "$FILE_NAME"
#     logmsg INFO "Временный файл удален"
# fi
