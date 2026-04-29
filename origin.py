import csv
import re
from pprint import pprint

def normalize_name(contact):
    full_name_tokens = " ".join(contact[:3]).strip().split()
    lastname  = full_name_tokens[0] if len(full_name_tokens) > 0 else ""
    firstname = full_name_tokens[1] if len(full_name_tokens) > 1 else ""
    surname   = full_name_tokens[2] if len(full_name_tokens) > 2 else ""
    rest = contact[3:] if len(contact) > 3 else []
    while len(rest) < 4:
        rest.append("")
    return [lastname, firstname, surname] + rest[:4]

def normalize_phone(phone):
    if not phone:
        return ""
    phone = phone.strip()
    ext_match = re.search(r'(доб\.?\s*)(\d+)', phone, re.IGNORECASE)
    ext = ""
    if ext_match:
        ext = " доб." + ext_match.group(2)
        phone = re.sub(r'доб\.?\s*\d+', '', phone, flags=re.IGNORECASE)
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 11 and digits[0] in ('7', '8'):
        digits = digits[1:]
        number = f"+7({digits[0:3]}){digits[3:6]}-{digits[6:8]}-{digits[8:10]}"
    elif len(digits) == 10:
        number = f"+7({digits[0:3]}){digits[3:6]}-{digits[6:8]}-{digits[8:10]}"
    else:
        number = phone
    return number + ext

# Чтение
with open("phonebook_raw.csv", encoding="utf-8") as f:
    rows = csv.reader(f, delimiter=",")
    contacts_list = list(rows)

pprint(contacts_list)

# Заголовок
header = []
if contacts_list and contacts_list[0][0].lower() == 'lastname':
    header = contacts_list[0]
    data_rows = contacts_list[1:]
else:
    data_rows = contacts_list

# Нормализация
normalized = []
for row in data_rows:
    while len(row) < 7:
        row.append("")
    row = normalize_name(row)
    row[5] = normalize_phone(row[5])
    normalized.append(row)

# Объединение дублей по ФАМИЛИИ, ИМЕНИ, ОТЧЕСТВУ (три поля)
unique = {}
for row in normalized:
    # ключ – кортеж из трёх строк (lastname, firstname, surname)
    key = (row[0].lower(), row[1].lower(), row[2].lower())
    if key not in unique:
        unique[key] = row[:]
    else:
        existing = unique[key]
        # Объединяем поля: organization, position, phone, email (индексы 3..6)
        for i in range(3, 7):
            if not existing[i] and row[i]:
                existing[i] = row[i]

# Результат с заголовком
result = []
if header:
    result.append(header)
result.extend(unique.values())

# Сохранение
with open("phonebook.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerows(result)

print("Готово. Результат в phonebook.csv")
pprint(result)