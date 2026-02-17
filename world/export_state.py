import json
from evennia.objects.models import ObjectDB

data = []
for obj in ObjectDB.objects.all():
    entry = {
        "dbref": obj.id,
        "key": obj.key,
        "typeclass": obj.typeclass_path,
        "location": obj.db_location_id,
        "destination": obj.db_destination_id,
        "home": obj.db_home_id,
        "aliases": list(obj.aliases.all()),
    }
    data.append(entry)

with open("world/current_state.json", "w") as f:
    json.dump(data, f, indent=2)

print(f"Exported {len(data)} objects to world/current_state.json")
