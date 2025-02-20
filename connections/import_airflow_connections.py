import json
import subprocess

# Load the JSON file
with open("airflow_connections_backup.json", "r") as f:
    connections = json.load(f)

# Iterate over each connection
for conn in connections:
    conn_id = conn.get("conn_id", "")
    conn_type = conn.get("conn_type", "")
    host = conn.get("host", "")
    schema = conn.get("schema", None)  # Use None instead of empty string
    login = conn.get("login", None)
    password = conn.get("password", None)
    port = str(conn.get("port", "")) if conn.get("port") else None
    extra = json.dumps(conn.get("extra_dejson", {})) if conn.get("extra_dejson") else None

    # Base command
    command = ["airflow", "connections", "add", conn_id, "--conn-type", conn_type]

    # Only add arguments that are not None or empty
    if host:
        command.extend(["--conn-host", host])
    if schema:
        command.extend(["--conn-schema", schema])
    if login:
        command.extend(["--conn-login", login])
    if password:
        command.extend(["--conn-password", password])
    if port:
        command.extend(["--conn-port", port])
    if extra and extra != "{}":  # Avoid adding empty JSON "{}"
        command.extend(["--conn-extra", extra])

    print(f"Adding connection: {conn_id}")
    subprocess.run(command, check=True)

print("✅ All connections have been imported successfully!")
