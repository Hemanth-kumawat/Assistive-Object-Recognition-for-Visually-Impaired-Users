from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import math
import time

app = Flask(__name__)
CORS(app)

PORT = 5002

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OSRM_URL = "https://routing.openstreetmap.de/routed-foot/route/v1/driving"

HEADERS = {
    "User-Agent": "ULTRON-Assistive-AI/1.0"
}

# ============================================================
# NAVIGATION STATE
# ============================================================

navigation_state = {
    "active": False,
    "current_location": None,
    "destination": None,
    "destination_coordinates": None,
    "route": [],
    "steps": [],
    "current_step": 0,
    "distance_meters": 0,
    "duration_seconds": 0,
    "status": "idle",
    "last_update": None
}


# ============================================================
# KNOWN DESTINATIONS
# ============================================================

KNOWN_DESTINATIONS = {
    "kgreddy": {
        "name": "KG Reddy College of Engineering and Technology",
        "latitude": 17.33564,
        "longitude": 78.28941
    },
    "kgreaddy": {
        "name": "KG Reddy College of Engineering and Technology",
        "latitude": 17.33564,
        "longitude": 78.28941
    },
    "kg reddy": {
        "name": "KG Reddy College of Engineering and Technology",
        "latitude": 17.33564,
        "longitude": 78.28941
    },
    "kg reddy college": {
        "name": "KG Reddy College of Engineering and Technology",
        "latitude": 17.33564,
        "longitude": 78.28941
    },
    "kgrcet": {
        "name": "KG Reddy College of Engineering and Technology",
        "latitude": 17.33564,
        "longitude": 78.28941
    }
}


# ============================================================
# HELPERS
# ============================================================

def normalize_destination(destination):
    return " ".join(destination.lower().strip().split())


def resolve_known_destination(destination):
    key = normalize_destination(destination)

    if key in KNOWN_DESTINATIONS:
        return KNOWN_DESTINATIONS[key]

    if (
        "kg reddy" in key
        or "kgreddy" in key
        or "kgrcet" in key
    ):
        return KNOWN_DESTINATIONS["kgreddy"]

    return None


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(dlambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# ============================================================
# GEOCODING
# ============================================================

def geocode_destination(destination):
    known = resolve_known_destination(destination)

    if known:
        return {
            "name": known["name"],
            "latitude": known["latitude"],
            "longitude": known["longitude"]
        }

    try:
        response = requests.get(
            NOMINATIM_URL,
            params={
                "q": destination,
                "format": "json",
                "limit": 1
            },
            headers=HEADERS,
            timeout=10
        )

        if response.status_code != 200:
            return None

        results = response.json()

        if not results:
            return None

        result = results[0]

        return {
            "name": result.get("display_name", destination),
            "latitude": float(result["lat"]),
            "longitude": float(result["lon"])
        }

    except Exception as e:
        print("Geocoding error:", e)
        return None


# ============================================================
# ROUTING
# ============================================================

def calculate_route(start_lat, start_lon, end_lat, end_lon):

    coordinates = (
        f"{start_lon},{start_lat};"
        f"{end_lon},{end_lat}"
    )

    url = f"{OSRM_URL}/{coordinates}"

    try:
        response = requests.get(
            url,
            params={
                "overview": "full",
                "steps": "true",
                "geometries": "geojson"
            },
            headers=HEADERS,
            timeout=20
        )

        print("OSRM status:", response.status_code)

        if response.status_code != 200:
            print("OSRM response:", response.text[:500])
            return None

        data = response.json()

        if data.get("code") != "Ok":
            print("OSRM error:", data)
            return None

        routes = data.get("routes", [])

        if not routes:
            return None

        route = routes[0]

        geometry = route.get("geometry", {}).get("coordinates", [])

        route_points = [
            {
                "latitude": point[1],
                "longitude": point[0]
            }
            for point in geometry
        ]

        steps = []

        for leg in route.get("legs", []):
            for step in leg.get("steps", []):

                maneuver = step.get("maneuver", {})

                steps.append({
                    "instruction": build_instruction(step),
                    "distance_meters": step.get("distance", 0),
                    "duration_seconds": step.get("duration", 0),
                    "latitude": maneuver.get("location", [0, 0])[1],
                    "longitude": maneuver.get("location", [0, 0])[0]
                })

        return {
            "route": route_points,
            "steps": steps,
            "distance_meters": route.get("distance", 0),
            "duration_seconds": route.get("duration", 0)
        }

    except Exception as e:
        print("Routing error:", e)
        return None


# ============================================================
# NAVIGATION INSTRUCTIONS
# ============================================================

def build_instruction(step):

    maneuver = step.get("maneuver", {})
    maneuver_type = maneuver.get("type", "")
    modifier = maneuver.get("modifier", "")

    distance = step.get("distance", 0)

    if distance >= 1000:
        distance_text = f"{distance / 1000:.1f} kilometers"
    else:
        distance_text = f"{int(distance)} meters"

    if maneuver_type == "depart":
        return f"Start navigation and continue for {distance_text}."

    if maneuver_type == "arrive":
        return "You have arrived at your destination."

    if maneuver_type == "turn":

        direction = modifier.replace("-", " ")

        return (
            f"Turn {direction} and continue "
            f"for {distance_text}."
        )

    if maneuver_type == "continue":
        return f"Continue straight for {distance_text}."

    if maneuver_type == "roundabout":
        return f"Enter the roundabout and continue for {distance_text}."

    if maneuver_type == "merge":
        return f"Merge and continue for {distance_text}."

    return f"Continue for {distance_text}."


# ============================================================
# UPDATE CURRENT NAVIGATION STEP
# ============================================================

def update_current_step():

    location = navigation_state["current_location"]

    if not location:
        return

    steps = navigation_state["steps"]
    current_step = navigation_state["current_step"]

    if current_step >= len(steps):
        return

    step = steps[current_step]

    distance = calculate_distance(
        location["latitude"],
        location["longitude"],
        step["latitude"],
        step["longitude"]
    )

    # Move to next instruction when close to maneuver
    if distance <= 35 and current_step < len(steps) - 1:
        navigation_state["current_step"] += 1


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():
    return jsonify({
        "service": "ULTRON Navigation Engine",
        "status": "online",
        "port": PORT
    })


# ============================================================
# HEALTH
# ============================================================

@app.route("/health")
def health():
    return jsonify({
        "success": True,
        "status": "online",
        "service": "ULTRON Navigation Engine",
        "port": PORT
    })


# ============================================================
# UPDATE GPS LOCATION
# ============================================================

@app.route("/update_location", methods=["POST"])
def update_location():

    data = request.get_json(silent=True) or {}

    try:
        latitude = float(data["latitude"])
        longitude = float(data["longitude"])

        navigation_state["current_location"] = {
            "latitude": latitude,
            "longitude": longitude
        }

        navigation_state["last_update"] = time.time()

        if navigation_state["active"]:
            update_current_step()

        return jsonify({
            "success": True,
            "latitude": latitude,
            "longitude": longitude
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


# ============================================================
# RECEIVE LOCATION
# ============================================================

@app.route("/receive_location", methods=["POST"])
def receive_location():
    return update_location()


# ============================================================
# CURRENT LOCATION
# ============================================================

@app.route("/current_location")
def current_location():

    location = navigation_state["current_location"]

    if not location:
        return jsonify({
            "success": False,
            "error": "GPS location not available"
        }), 404

    return jsonify({
        "success": True,
        "latitude": location["latitude"],
        "longitude": location["longitude"]
    })


# ============================================================
# START NAVIGATION
# ============================================================

@app.route("/start_navigation", methods=["POST"])
def start_navigation():

    data = request.get_json(silent=True) or {}

    destination = data.get("destination", "").strip()

    if not destination:
        return jsonify({
            "success": False,
            "error": "Destination is required"
        }), 400

    current = navigation_state["current_location"]

    if not current:
        return jsonify({
            "success": False,
            "error": "Current GPS location is not available. Open /gps first."
        }), 400

    destination_data = geocode_destination(destination)

    if not destination_data:

        return jsonify({
            "success": False,
            "error": f"Destination '{destination}' could not be found"
        }), 404

    route_data = calculate_route(
        current["latitude"],
        current["longitude"],
        destination_data["latitude"],
        destination_data["longitude"]
    )

    if not route_data:

        return jsonify({
            "success": False,
            "error": "Could not calculate walking route"
        }), 500

    navigation_state["active"] = True
    navigation_state["destination"] = destination_data["name"]

    navigation_state["destination_coordinates"] = {
        "latitude": destination_data["latitude"],
        "longitude": destination_data["longitude"]
    }

    navigation_state["route"] = route_data["route"]
    navigation_state["steps"] = route_data["steps"]

    navigation_state["current_step"] = 0
    navigation_state["distance_meters"] = route_data["distance_meters"]
    navigation_state["duration_seconds"] = route_data["duration_seconds"]

    navigation_state["status"] = "navigating"

    navigation_state["last_update"] = time.time()

    return jsonify({
        "success": True,
        "message": f"Navigation started to {destination_data['name']}",
        "destination": destination_data,
        "distance_meters": route_data["distance_meters"],
        "duration_seconds": route_data["duration_seconds"],
        "steps": route_data["steps"],
        "route": route_data["route"]
    })


# ============================================================
# NAVIGATION STATUS
# ============================================================

@app.route("/navigation_status")
def navigation_status():

    update_current_step()

    current_instruction = None

    if (
        navigation_state["steps"]
        and navigation_state["current_step"]
        < len(navigation_state["steps"])
    ):
        current_instruction = navigation_state["steps"][
            navigation_state["current_step"]
        ]["instruction"]

    return jsonify({
        "success": True,
        "active": navigation_state["active"],
        "status": navigation_state["status"],
        "destination": navigation_state["destination"],
        "current_location": navigation_state["current_location"],
        "destination_coordinates":
            navigation_state["destination_coordinates"],
        "current_step": navigation_state["current_step"],
        "total_steps": len(navigation_state["steps"]),
        "current_instruction": current_instruction,
        "distance_meters": navigation_state["distance_meters"],
        "duration_seconds": navigation_state["duration_seconds"]
    })


# ============================================================
# NEXT INSTRUCTION
# ============================================================

@app.route("/next_instruction")
def next_instruction():

    update_current_step()

    steps = navigation_state["steps"]
    index = navigation_state["current_step"]

    if not steps:
        return jsonify({
            "success": False,
            "error": "No active navigation route"
        }), 404

    if index >= len(steps):
        return jsonify({
            "success": True,
            "instruction": "You have arrived at your destination."
        })

    return jsonify({
        "success": True,
        "step": index + 1,
        "instruction": steps[index]["instruction"],
        "distance_meters": steps[index]["distance_meters"]
    })


# ============================================================
# LAST SUMMARY
# ============================================================

@app.route("/last_summary")
def last_summary():

    location = navigation_state["current_location"]

    if not location:
        return jsonify({
            "success": False,
            "message": "GPS location not available"
        })

    destination = navigation_state["destination_coordinates"]

    distance_remaining = None

    if destination:

        distance_remaining = calculate_distance(
            location["latitude"],
            location["longitude"],
            destination["latitude"],
            destination["longitude"]
        )

    return jsonify({
        "success": True,
        "active": navigation_state["active"],
        "status": navigation_state["status"],
        "destination": navigation_state["destination"],
        "current_location": location,
        "distance_remaining_meters": distance_remaining,
        "current_instruction": (
            navigation_state["steps"]
            [navigation_state["current_step"]]["instruction"]
            if navigation_state["steps"]
            and navigation_state["current_step"] < len(navigation_state["steps"])
            else None
        )
    })


# ============================================================
# ROUTE
# ============================================================

@app.route("/route")
def route():

    return jsonify({
        "success": True,
        "route": navigation_state["route"],
        "steps": navigation_state["steps"],
        "current_step": navigation_state["current_step"]
    })


# ============================================================
# STOP NAVIGATION
# ============================================================

@app.route("/stop_navigation", methods=["POST", "GET"])
def stop_navigation():

    navigation_state["active"] = False
    navigation_state["status"] = "stopped"

    navigation_state["destination"] = None
    navigation_state["destination_coordinates"] = None

    navigation_state["route"] = []
    navigation_state["steps"] = []

    navigation_state["current_step"] = 0

    return jsonify({
        "success": True,
        "message": "Navigation stopped"
    })


# ============================================================
# GPS WEB PAGE
# ============================================================

@app.route("/gps")
def gps_page():

    return """
<!DOCTYPE html>
<html>
<head>
    <title>ULTRON GPS Navigation</title>

    <meta name="viewport"
          content="width=device-width, initial-scale=1.0">

    <link rel="stylesheet"
          href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>

    <style>

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #111;
            color: white;
        }

        #map {
            height: 70vh;
            width: 100%;
        }

        #panel {
            padding: 15px;
        }

        button {
            padding: 12px 20px;
            margin: 5px;
            font-size: 16px;
            border-radius: 8px;
            border: none;
        }

        #status {
            font-size: 20px;
            margin-bottom: 10px;
        }

    </style>
</head>

<body>

<div id="panel">

    <div id="status">
        GPS OFFLINE
    </div>

    <button onclick="startGPS()">
        Start GPS
    </button>

    <button onclick="stopNavigation()">
        Stop Navigation
    </button>

    <div id="info">
        Waiting for GPS...
    </div>

</div>

<div id="map"></div>

<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<script>

let map = L.map("map").setView(
    [17.33564, 78.28941],
    15
);

L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        attribution: "© OpenStreetMap contributors"
    }
).addTo(map);

let marker = null;
let watchId = null;
let destinationMarker = null;
let routeLine = null;

function startGPS() {

    if (!navigator.geolocation) {

        document.getElementById("status").innerText =
            "GPS NOT SUPPORTED";

        return;
    }

    document.getElementById("status").innerText =
        "GPS STARTING...";

    watchId = navigator.geolocation.watchPosition(

        function(position) {

            let latitude = position.coords.latitude;
            let longitude = position.coords.longitude;

            document.getElementById("status").innerText =
                "GPS ONLINE";

            document.getElementById("info").innerText =
                "Latitude: " + latitude.toFixed(6) +
                " | Longitude: " + longitude.toFixed(6);

            if (!marker) {

                marker = L.marker([
                    latitude,
                    longitude
                ]).addTo(map);

            } else {

                marker.setLatLng([
                    latitude,
                    longitude
                ]);

            }

            map.setView([
                latitude,
                longitude
            ]);

            fetch("/update_location", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    latitude: latitude,
                    longitude: longitude
                })

            });

        },

        function(error) {

            document.getElementById("status").innerText =
                "GPS ERROR: " + error.message;

        },

        {
            enableHighAccuracy: true,
            maximumAge: 1000,
            timeout: 10000
        }

    );
}


function stopNavigation() {

    if (watchId !== null) {

        navigator.geolocation.clearWatch(watchId);
        watchId = null;

    }

    fetch("/stop_navigation", {
        method: "POST"
    });

    document.getElementById("status").innerText =
        "NAVIGATION STOPPED";
}


function updateRoute() {

    fetch("/route")
    .then(response => response.json())
    .then(data => {

        if (!data.success || !data.route.length) {
            return;
        }

        let points = data.route.map(point => [
            point.latitude,
            point.longitude
        ]);

        if (routeLine) {
            routeLine.remove();
        }

        routeLine = L.polyline(points).addTo(map);

    });

}


function updateStatus() {

    fetch("/last_summary")
    .then(response => response.json())
    .then(data => {

        if (!data.success) {
            return;
        }

        let text = "";

        if (data.destination) {

            text +=
                "Destination: " +
                data.destination +
                "<br>";

        }

        if (data.distance_remaining_meters !== null) {

            text +=
                "Distance remaining: " +
                Math.round(
                    data.distance_remaining_meters
                ) +
                " meters<br>";

        }

        if (data.current_instruction) {

            text +=
                "Instruction: " +
                data.current_instruction;

        }

        document.getElementById("info").innerHTML =
            text;

    });

}


setInterval(updateRoute, 2000);
setInterval(updateStatus, 1000);

</script>

</body>
</html>
"""


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("ULTRON NAVIGATION ENGINE")
    print("=" * 60)
    print(f"Server running on http://127.0.0.1:{PORT}")
    print(f"GPS page: http://127.0.0.1:{PORT}/gps")
    print("=" * 60)

    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False,
        threaded=True
    )