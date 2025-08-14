import csv
from datetime import datetime, timedelta
import random

# Initial 100 records (provided above)
initial_records = [
    # (Insert the 100 rows from the artifact above here manually if needed, or skip and let the script generate all)
]

# Lists for generating unique data
first_names = ["Aarav", "Bina", "Chirag", "Diya", "Eshan", "Falgun", "Gita", "Hari", "Isha", "Jivan",
               "Kamal", "Laxmi", "Manish", "Nisha", "Om", "Puja", "Raju", "Sita", "Tara", "Umesh",
               "Vikram", "Wina", "Xavi", "Yogesh", "Zara", "Aakash", "Bina", "Chitra", "Dev", "Esha"]
last_names = ["Sharma", "Gurung", "Thapa", "Rana", "Adhikari", "Pandey", "Shrestha", "Joshi", "Karki",
              "Pradhan", "Basnet", "Dahal", "Gautam", "Khadka", "Shahi", "Bista", "Koirala", "Maharjan",
              "Poudel", "Regmi", "Sapkota", "Thapa", "Rana", "Adhikari", "Pandey"]
cities = ["Kathmandu", "Pokhara", "Lalitpur", "Biratnagar", "Bhairahawa", "Hetauda", "Butwal",
          "Dhangadhi", "Janakpur", "Nepalgunj", "Bhaktapur", "Itahari", "Dharan", "Birtamod"]
postal_codes = ["44600", "00987", "55700", "33001", "98001", "60012", "44001", "00976", "56001",
                "34002", "44800", "97700", "56700", "23400"]
streets = ["Himalayan Rd", "Sagarmatha St", "Everest Ln", "Annapurna Ave", "Langtang Dr", "Manaslu Rd",
           "Dhaulagiri St", "Kanchenjunga Ln", "Makalu Ave", "Gaurishankar Dr"]

# Generate 1,500 records (including the initial 100 if added manually)
records = initial_records.copy()  # Start with initial 100 if provided
start_idx = len(initial_records) + 1
start_date = datetime(2025, 8, 1)

used_emails = {f"{first_name.lower()}.{last_name.lower()}{i:03d}@example.com"
               for i in range(1, start_idx) for first_name in first_names for last_name in last_names}

for i in range(start_idx, 1501):
    while True:
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        email = f"{first_name.lower()}.{last_name.lower()}{i:03d}@example.com"
        if email not in used_emails:
            used_emails.add(email)
            break

    address = f"{random.randint(100, 999)} {random.choice(streets)}"
    postal_code = random.choice(postal_codes)
    city = random.choice(cities)
    paid = random.choice([True, False])
    stripe_id = f"pi_unique_3{i:06d}" if paid else ""
    created = start_date + timedelta(days=random.randint(0, 365), hours=random.randint(8, 20))
    updated = created  # Same as created for simplicity

    records.append({
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "address": address,
        "postal_code": postal_code,
        "city": city,
        "paid": paid,
        "created": created.strftime("%Y-%m-%d %H:%M:%S"),
        "updated": updated.strftime("%Y-%m-%d %H:%M:%S"),
        "stripe_id": stripe_id
    })

# Write to CSV
with open("order_unique_1500_sample.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["first_name", "last_name", "email", "address",
                                           "postal_code", "city", "paid", "created",
                                           "updated", "stripe_id"])
    writer.writeheader()
    writer.writerows(records)

print("Generated order_unique_1500_sample.csv with 1,500 unique records.")
