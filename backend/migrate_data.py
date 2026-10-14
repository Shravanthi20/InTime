import csv
import os
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
DATA_IN_HOSP = os.path.join(ROOT_DIR, "Data", "InTime_hospitals_v1.csv")
DATA_IN_STAT = os.path.join(ROOT_DIR, "Data", "InTime_hospital_status_v1.csv")
DATA_OUT_HOSP = os.path.join(BASE_DIR, "data", "hospitals.csv")
DATA_OUT_STAT = os.path.join(BASE_DIR, "data", "hospital_status.csv")

def main():
    print("Reading from full database...")
    hospitals = []
    with open(DATA_IN_HOSP, "r") as fin:
        reader = csv.DictReader(fin)
        for row in reader:
            h_id = row["hospital_id"]
            name = row["hospital_name"]
            h_type = row["hospital_type"]
            trauma = "True" if row.get("trauma_center") == "1" else "False"
            
            specs = []
            if row.get("trauma_center") == "1": specs.append("TRAUMA")
            if row.get("cardiology") == "1": specs.append("CARDIOLOGY")
            if row.get("neurology") == "1": specs.append("NEUROLOGY")
            if row.get("orthopedics") == "1": specs.append("ORTHOPEDICS")
            if row.get("general_surgery") == "1": specs.append("GENERAL_SURGERY")
            
            specialists = "|".join(specs) if specs else "GENERAL"
            hospitals.append([h_id, name, h_type, trauma, specialists])

    print(f"Mapped {len(hospitals)} hospitals.")
    
    with open(DATA_OUT_HOSP, "w", newline='') as fout:
        writer = csv.writer(fout)
        writer.writerow(["hospital_id", "name", "type", "trauma_capability", "specialists"])
        writer.writerows(hospitals)

    status_map = {}
    with open(DATA_IN_STAT, "r") as fin:
        reader = csv.DictReader(fin)
        for row in reader:
            ts = row.get("timestamp", "00:00")
            if " " in ts:
                ts = ts.split(" ")[1][:5]
            status_map[row["hospital_id"]] = {
                "timestamp": ts,
                "icu_available": row.get("icu_available", "0"),
                "er_occupancy": row.get("er_occupancy", "0.5")
            }

    print(f"Mapped status for {len(status_map)} hospitals.")

    with open(DATA_OUT_STAT, "w", newline='') as fout:
        writer = csv.writer(fout)
        writer.writerow(["hospital_id", "timestamp", "icu_available", "er_occupancy"])
        for h_id in sorted(status_map.keys()):
            s = status_map[h_id]
            writer.writerow([h_id, s["timestamp"], s["icu_available"], s["er_occupancy"]])
            
    print("Migration complete. Mock DB updated.")

if __name__ == "__main__":
    main()
