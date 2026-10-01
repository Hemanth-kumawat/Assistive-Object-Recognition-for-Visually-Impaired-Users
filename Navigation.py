from flask import Flask, request, jsonify, Response
from flask_cors import CORS

import requests
import threading
import time
import math


# ============================================================
# FLASK
# ============================================================

app = Flask(__name__)
CORS(app)


# ============================================================
# CONFIGURATION
# ============================================================

PORT = 5002

# OpenStreetMap Nominatim
NOMINATIM_URL = "https://nominatim.openstreetmap.org"

# OpenStreetMap routing service - walking
OSRM_URL = "https://routing.openstreetmap.de/routed-foot"

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

    "route": None,

    "steps": [],

    "current_step": 0,

    "distance_meters": None,

    "duration_seconds": None,

    "status": "idle",

    "last_update": None
}


state_lock = threading.Lock()


# ============================================================
# KNOWN DESTINATIONS
# ============================================================

KNOWN_DESTINATIONS = {

    "kgreddy": {
        "name":
            "KG Reddy College of Engineering "
            "and Technology",

        "latitude":
            17.33564,

        "longitude":
            78.28941
    },

    "kgreaddy": {
        "name":
            "KG Reddy College of Engineering "
            "and Technology",

        "latitude":
            17.33564,

        "longitude":
            78.28941
    },

    "kg reddy": {
        "name":
            "KG Reddy College of Engineering "
            "and Technology",

        "latitude":
            17.33564,

        "longitude":
            78.28941
    },

    "kg reddy college": {
        "name":
            "KG Reddy College of Engineering "
            "and Technology",

        "latitude":
            17.33564,

        "longitude":
            78.28941
    },

    "kgrcet": {
        "name":
            "KG Reddy College of Engineering "
            "and Technology",

        "latitude":
            17.33564,

        "longitude":
            78.28941
    }
}


# ============================================================
# DESTINATION RESOLVER
# ============================================================

def resolve_known_destination(destination):

    if not destination:
        return None

    key = (
        destination
        .strip()
        .lower()
    )

    if key in KNOWN_DESTINATIONS:

        return KNOWN_DESTINATIONS[key]

    if (
        "kg reddy" in key
        or "kgreddy" in key
        or "kgrcet" in key
    ):

        return KNOWN_DESTINATIONS["kgreddy"]

    return None


# ============================================================
# GEOCODING
# ============================================================

def geocode_destination(destination):

    known = resolve_known_destination(
        destination
    )

    if known:

        return {
            "latitude":
                known["latitude"],

            "longitude":
                known["longitude"],

            "display_name":
                known["name"]
        }


    try:

        response = requests.get(

            f"{NOMINATIM_URL}/search",

            params={
                "q":
                    destination,

                "format":
                    "json",

                "limit":
                    1,

                "countrycodes":
                    "in"
            },

            headers=HEADERS,

            timeout=15
        )

        response.raise_for_status()

        results = response.json()

        if not results:

            print(
                "❌ Destination not found:",
                destination
            )

            return None


        result = results[0]

        return {

            "latitude":
                float(result["lat"]),

            "longitude":
                float(result["lon"]),

            "display_name":
                result.get(
                    "display_name",
                    destination
                )
        }


    except Exception as error:

        print(
            "❌ Geocoding error:",
            error
        )

        return None


# ============================================================
# DISTANCE BETWEEN TWO GPS POINTS
# ============================================================

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):

    earth_radius = 6371000

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)

    delta_lat = math.radians(
        lat2 - lat1
    )

    delta_lon = math.radians(
        lon2 - lon1
    )

    a = (
        math.sin(delta_lat / 2) ** 2
        +
        math.cos(lat1_rad)
        *
        math.cos(lat2_rad)
        *
        math.sin(delta_lon / 2) ** 2
    )

    c = (
        2
        *
        math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a)
        )
    )

    return earth_radius * c


# ============================================================
# ROUTE CALCULATION
# ============================================================

def calculate_route(
    start_lat,
    start_lon,
    destination_lat,
    destination_lon
):

    try:

        coordinates = (
            f"{start_lon},{start_lat};"
            f"{destination_lon},{destination_lat}"
        )


        url = (
            f"{OSRM_URL}/route/v1/driving/"
            f"{coordinates}"
        )


        params = {

            "overview":
                "full",

            "steps":
                "true",

            "geometries":
                "geojson",

            "alternatives":
                "false"
        }


        print()
        print(
            "🗺️ Calculating route..."
        )

        print(
            "Start:",
            start_lat,
            start_lon
        )

        print(
            "Destination:",
            destination_lat,
            destination_lon
        )


        response = requests.get(

            url,

            params=params,

            timeout=30
        )


        response.raise_for_status()

        data = response.json()


        if data.get("code") != "Ok":

            print(
                "❌ Routing service:",
                data.get("code")
            )

            return None


        routes = data.get(
            "routes",
            []
        )


        if not routes:

            print(
                "❌ No route found."
            )

            return None


        route = routes[0]

        steps = []


        for leg in route.get(
            "legs",
            []
        ):

            for step in leg.get(
                "steps",
                []
            ):

                instruction = (
                    build_instruction(
                        step
                    )
                )


                steps.append({

                    "instruction":
                        instruction,

                    "distance_meters":
                        step.get(
                            "distance",
                            0
                        ),

                    "duration_seconds":
                        step.get(
                            "duration",
                            0
                        ),

                    "type":
                        step.get(
                            "maneuver",
                            {}
                        ).get(
                            "type"
                        ),

                    "modifier":
                        step.get(
                            "maneuver",
                            {}
                        ).get(
                            "modifier"
                        ),

                    "name":
                        step.get(
                            "name",
                            ""
                        ),

                    "location":
                        step.get(
                            "maneuver",
                            {}
                        ).get(
                            "location"
                        )

                })


        return {

            "distance_meters":
                route.get(
                    "distance",
                    0
                ),

            "duration_seconds":
                route.get(
                    "duration",
                    0
                ),

            "geometry":
                route.get(
                    "geometry"
                ),

            "steps":
                steps
        }


    except Exception as error:

        print(
            "❌ Route calculation error:",
            error
        )

        return None


# ============================================================
# HUMAN NAVIGATION INSTRUCTION
# ============================================================

def build_instruction(step):

    maneuver = step.get(
        "maneuver",
        {}
    )


    maneuver_type = maneuver.get(
        "type",
        ""
    )


    modifier = maneuver.get(
        "modifier",
        ""
    )


    road_name = step.get(
        "name",
        ""
    )


    distance = step.get(
        "distance",
        0
    )


    if distance >= 1000:

        distance_text = (
            f"{distance / 1000:.1f} kilometers"
        )

    else:

        distance_text = (
            f"{round(distance)} meters"
        )


    if maneuver_type == "arrive":

        return (
            "You have arrived "
            "at your destination."
        )


    if maneuver_type == "depart":

        if road_name:

            return (
                f"Start on {road_name} "
                f"and continue for "
                f"{distance_text}."
            )

        return (
            f"Start moving forward "
            f"for {distance_text}."
        )


    if maneuver_type == "roundabout":

        if road_name:

            return (
                f"Enter the roundabout "
                f"and continue toward "
                f"{road_name}."
            )

        return (
            "Enter the roundabout."
        )


    if maneuver_type == "fork":

        if modifier:

            direction = (
                modifier
                .replace("-", " ")
            )

            return (
                f"Keep {direction} "
                f"for {distance_text}."
            )


    if modifier:

        direction = (
            modifier
            .replace("-", " ")
        )


        if road_name:

            return (
                f"Turn {direction} "
                f"onto {road_name} "
                f"and continue for "
                f"{distance_text}."
            )


        return (
            f"Turn {direction} "
            f"and continue for "
            f"{distance_text}."
        )


    if road_name:

        return (
            f"Continue on {road_name} "
            f"for {distance_text}."
        )


    return (
        f"Continue for "
        f"{distance_text}."
    )


# ============================================================
# UPDATE CURRENT STEP
# ============================================================

def update_current_step():

    with state_lock:

        if not navigation_state[
            "active"
        ]:

            return


        location = navigation_state[
            "current_location"
        ]


        steps = navigation_state[
            "steps"
        ]


        current_index = navigation_state[
            "current_step"
        ]


        if not location or not steps:

            return


        if current_index >= len(steps):

            return


        step = steps[current_index]

        step_location = step.get(
            "location"
        )


        if not step_location:

            return


        try:

            step_lon = float(
                step_location[0]
            )

            step_lat = float(
                step_location[1]
            )

        except Exception:

            return


        distance = calculate_distance(

            location["latitude"],

            location["longitude"],

            step_lat,

            step_lon
        )


        # Once within 35 metres of the
        # maneuver point, advance.

        if (
            distance < 35
            and
            current_index
            <
            len(steps) - 1
        ):

            navigation_state[
                "current_step"
            ] += 1


            print(
                "➡️ Next navigation step:",
                navigation_state[
                    "current_step"
                ]
            )


# ============================================================
# HEALTH
# ============================================================

@app.route(
    "/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "status":
            "online",

        "service":
            "ULTRON Navigation Engine",

        "port":
            PORT
    })


# ============================================================
# HOME
# ============================================================

@app.route(
    "/",
    methods=["GET"]
)
def home():

    return jsonify({

        "service":
            "ULTRON Navigation Engine",

        "status":
            "online",

        "endpoints": {

            "health":
                "/health",

            "gps":
                "/gps",

            "start_navigation":
                "/start_navigation",

            "navigation_status":
                "/navigation_status",

            "last_summary":
                "/last_summary",

            "next_instruction":
                "/next_instruction",

            "stop_navigation":
                "/stop_navigation",

            "route":
                "/route",

            "location":
                "/current_location"
        }
    })


# ============================================================
# GPS / LIVE MAP PAGE
# ============================================================

@app.route(
    "/gps",
    methods=["GET"]
)
def gps_page():

    html = r"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width,
             initial-scale=1.0"
>

<title>ULTRON Navigation</title>


<link
    rel="stylesheet"
    href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
/>


<script
    src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js">
</script>


<style>

* {
    box-sizing: border-box;
}


body {

    margin: 0;

    background:
        #05070b;

    color: white;

    font-family:
        Arial,
        sans-serif;

}


#map {

    width: 100%;

    height: 65vh;

}


.panel {

    padding: 18px;

    background:
        #101820;

}


.title {

    font-size: 28px;

    font-weight: bold;

    color: #00ffff;

}


.status {

    margin-top: 10px;

    padding: 12px;

    border-radius: 10px;

    background:
        rgba(
            0,
            255,
            255,
            0.08
        );

}


.info {

    display: grid;

    grid-template-columns:
        repeat(
            3,
            1fr
        );

    gap: 10px;

    margin-top: 12px;

}


.card {

    padding: 12px;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.12
        );

    border-radius: 10px;

}


.label {

    color: #8fa0aa;

    font-size: 13px;

}


.value {

    margin-top: 5px;

    font-size: 17px;

}


.instruction {

    margin-top: 15px;

    padding: 16px;

    border-radius: 12px;

    background:
        rgba(
            0,
            255,
            120,
            0.10
        );

    color: #00ff88;

    font-size: 19px;

}


button {

    padding:
        10px 18px;

    margin:
        5px;

    border: none;

    border-radius:
        8px;

    cursor:
        pointer;

    font-size:
        15px;

}


.start {

    background:
        #00ffff;

    color:
        #000;

}


.stop {

    background:
        #ff4444;

    color:
        white;

}


@media (
    max-width: 700px
) {

    .info {

        grid-template-columns:
            1fr;

    }

    #map {

        height: 55vh;

    }

}


</style>

</head>


<body>


<div id="map"></div>


<div class="panel">

<div class="title">

🤖 ULTRON Navigation

</div>


<div id="status"
     class="status">

Requesting GPS...

</div>


<div class="info">


<div class="card">

<div class="label">
CURRENT LOCATION
</div>

<div
    id="location"
    class="value"
>
Waiting...
</div>

</div>


<div class="card">

<div class="label">
DESTINATION
</div>

<div
    id="destination"
    class="value"
>
Not set
</div>

</div>


<div class="card">

<div class="label">
DISTANCE
</div>

<div
    id="distance"
    class="value"
>
--
</div>

</div>


</div>


<div
    id="instruction"
    class="instruction"
>

Waiting for navigation...

</div>


<button
    class="start"
    onclick="requestGPS()"
>

📍 Start GPS

</button>


<button
    class="stop"
    onclick="stopNavigation()"
>

🛑 Stop Navigation

</button>


</div>


<script>


let map;

let currentMarker;

let destinationMarker;

let routeLine;

let watchId = null;


const defaultCenter =
    [
        17.33564,
        78.28941
    ];


function initializeMap() {

    map = L.map(
        "map"
    ).setView(
        defaultCenter,
        14
    );


    L.tileLayer(

        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",

        {

            maxZoom:
                19,

            attribution:
                "&copy; OpenStreetMap contributors"

        }

    ).addTo(map);

}


function setCurrentLocation(
    latitude,
    longitude
) {

    const position =
        [
            latitude,
            longitude
        ];


    if (!currentMarker) {

        currentMarker =
            L.marker(
                position
            )
            .addTo(map)
            .bindPopup(
                "📍 Your location"
            );

    } else {

        currentMarker.setLatLng(
            position
        );

    }


    map.setView(
        position,
        16
    );


    document.getElementById(
        "location"
    ).innerText =
        latitude.toFixed(6)
        +
        ", "
        +
        longitude.toFixed(6);

}


function drawRoute(
    geometry
) {

    if (!geometry) {
        return;
    }


    if (routeLine) {

        map.removeLayer(
            routeLine
        );

    }


    if (
        geometry.type
        !==
        "LineString"
    ) {

        return;

    }


    const coordinates =
        geometry.coordinates.map(
            function(point) {

                return [
                    point[1],
                    point[0]
                ];

            }
        );


    routeLine =
        L.polyline(

            coordinates,

            {

                weight:
                    6,

                opacity:
                    0.85

            }

        ).addTo(map);


    map.fitBounds(
        routeLine.getBounds(),
        {
            padding:
                [30, 30]
        }
    );

}


function setDestination(
    latitude,
    longitude,
    name
) {

    const position =
        [
            latitude,
            longitude
        ];


    if (
        destinationMarker
    ) {

        destinationMarker
            .setLatLng(
                position
            );

    } else {

        destinationMarker =
            L.marker(
                position
            )
            .addTo(map)
            .bindPopup(
                "🎯 "
                + name
            );

    }


    document.getElementById(
        "destination"
    ).innerText =
        name;

}


function updateNavigation() {

    fetch(
        "/last_summary"
    )

    .then(
        response =>
            response.json()
    )

    .then(
        data => {

            if (
                data.current_location
            ) {

                setCurrentLocation(

                    data.current_location
                        .latitude,

                    data.current_location
                        .longitude

                );

            }


            if (
                data.destination
            ) {

                document.getElementById(
                    "destination"
                ).innerText =
                    data.destination;

            }


            if (
                data.distance_meters
                !==
                null
            ) {

                let distance =
                    data.distance_meters;


                if (
                    distance >= 1000
                ) {

                    document.getElementById(
                        "distance"
                    ).innerText =
                        (
                            distance / 1000
                        ).toFixed(2)
                        +
                        " km";

                } else {

                    document.getElementById(
                        "distance"
                    ).innerText =
                        Math.round(
                            distance
                        )
                        +
                        " m";

                }

            }


            document.getElementById(
                "status"
            ).innerText =

                data.active
                ?
                "🟢 NAVIGATION ACTIVE"
                :
                "⚪ NAVIGATION INACTIVE";


            if (
                data.next_instruction
            ) {

                let instruction =
                    data.next_instruction;


                if (
                    typeof instruction
                    ===
                    "object"
                ) {

                    instruction =
                        instruction.instruction
                        ||
                        "";

                }


                document.getElementById(
                    "instruction"
                ).innerText =
                    instruction;

            }

        }

    )

    .catch(
        function(error) {

            console.log(
                "Navigation update:",
                error
            );

        }
    );


    fetch(
        "/route"
    )

    .then(
        response =>
            response.json()
    )

    .then(
        data => {

            if (
                data.success
                &&
                data.route
            ) {

                drawRoute(
                    data.route
                );

            }

        }
    )

    .catch(
        function() {}
    );

}


function sendLocation(
    position
) {

    const latitude =
        position.coords.latitude;


    const longitude =
        position.coords.longitude;


    setCurrentLocation(
        latitude,
        longitude
    );


    document.getElementById(
        "status"
    ).innerText =
        "🟢 GPS ONLINE";


    fetch(

        "/update_location",

        {

            method:
                "POST",

            headers: {

                "Content-Type":
                    "application/json"

            },

            body:
                JSON.stringify({

                    latitude:
                        latitude,

                    longitude:
                        longitude

                })

        }

    )

    .then(
        response =>
            response.json()
    )

    .then(
        data => {

            console.log(
                "GPS update:",
                data
            );

            updateNavigation();

        }
    )

    .catch(
        error => {

            console.log(
                "GPS server error:",
                error
            );

        }
    );

}


function locationError(
    error
) {

    document.getElementById(
        "status"
    ).innerText =

        "❌ GPS error: "
        +
        error.message;

}


function requestGPS() {

    if (
        !navigator.geolocation
    ) {

        document.getElementById(
            "status"
        ).innerText =
            "❌ GPS not supported.";

        return;

    }


    document.getElementById(
        "status"
    ).innerText =
        "📡 Searching for GPS...";


    if (
        watchId !== null
    ) {

        navigator.geolocation
            .clearWatch(
                watchId
            );

    }


    watchId =
        navigator.geolocation
            .watchPosition(

                sendLocation,

                locationError,

                {

                    enableHighAccuracy:
                        true,

                    maximumAge:
                        5000,

                    timeout:
                        30000

                }

            );

}


function stopNavigation() {

    fetch(

        "/stop_navigation",

        {

            method:
                "POST"

        }

    )

    .then(
        response =>
            response.json()
    )

    .then(
        data => {

            document.getElementById(
                "status"
            ).innerText =
                "🛑 Navigation stopped.";

            document.getElementById(
                "instruction"
            ).innerText =
                "Navigation stopped.";

        }
    );

}


initializeMap();

requestGPS();

setInterval(
    updateNavigation,
    3000
);

</script>


</body>

</html>
"""

    return Response(
        html,
        mimetype="text/html"
    )


# ============================================================
# UPDATE GPS
# ============================================================

@app.route(
    "/update_location",
    methods=["POST"]
)
def update_location():

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "success":
                False,

            "error":
                "No location data."

        }), 400


    latitude = data.get(
        "latitude"
    )

    longitude = data.get(
        "longitude"
    )


    try:

        latitude = float(
            latitude
        )

        longitude = float(
            longitude
        )

    except Exception:

        return jsonify({

            "success":
                False,

            "error":
                "Invalid GPS coordinates."

        }), 400


    with state_lock:

        navigation_state[
            "current_location"
        ] = {

            "latitude":
                latitude,

            "longitude":
                longitude

        }

        navigation_state[
            "last_update"
        ] = time.time()


    print(
        f"📍 GPS: "
        f"{latitude:.6f}, "
        f"{longitude:.6f}"
    )


    # --------------------------------------------------------
    # Recalculate active route
    # --------------------------------------------------------

    if navigation_state[
        "active"
    ]:

        destination = (
            navigation_state[
                "destination_coordinates"
            ]
        )


        if destination:

            route = calculate_route(

                latitude,

                longitude,

                destination[
                    "latitude"
                ],

                destination[
                    "longitude"
                ]

            )


            if route:

                with state_lock:

                    navigation_state[
                        "route"
                    ] = route[
                        "geometry"
                    ]

                    navigation_state[
                        "steps"
                    ] = route[
                        "steps"
                    ]

                    navigation_state[
                        "distance_meters"
                    ] = route[
                        "distance_meters"
                    ]

                    navigation_state[
                        "duration_seconds"
                    ] = route[
                        "duration_seconds"
                    ]

                    navigation_state[
                        "current_step"
                    ] = 0

                    navigation_state[
                        "status"
                    ] = "route_updated"


    return jsonify({

        "success":
            True,

        "latitude":
            latitude,

        "longitude":
            longitude

    })


# ============================================================
# START NAVIGATION
# ============================================================

@app.route(
    "/start_navigation",
    methods=["POST"]
)
def start_navigation():

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "success":
                False,

            "error":
                "No JSON data."

        }), 400


    destination = data.get(
        "destination"
    )


    if not destination:

        return jsonify({

            "success":
                False,

            "error":
                "Destination required."

        }), 400


    current = navigation_state[
        "current_location"
    ]


    if not current:

        return jsonify({

            "success":
                False,

            "error":
                "GPS location is not available. "
                "Open /gps first and allow "
                "location access."

        }), 400


    print()
    print(
        "========================================"
    )
    print(
        "🧭 NAVIGATION REQUEST"
    )
    print(
        "========================================"
    )

    print(
        "Destination:",
        destination
    )

    print(
        "Current:",
        current
    )


    destination_data = (
        geocode_destination(
            destination
        )
    )


    if not destination_data:

        return jsonify({

            "success":
                False,

            "error":
                "Destination could not be found."

        }), 404


    route = calculate_route(

        current[
            "latitude"
        ],

        current[
            "longitude"
        ],

        destination_data[
            "latitude"
        ],

        destination_data[
            "longitude"
        ]

    )


    if not route:

        return jsonify({

            "success":
                False,

            "error":
                "No route could be calculated."

        }), 404


    with state_lock:

        navigation_state[
            "active"
        ] = True

        navigation_state[
            "destination"
        ] = destination_data[
            "display_name"
        ]

        navigation_state[
            "destination_coordinates"
        ] = {

            "latitude":
                destination_data[
                    "latitude"
                ],

            "longitude":
                destination_data[
                    "longitude"
                ]

        }

        navigation_state[
            "route"
        ] = route[
            "geometry"
        ]

        navigation_state[
            "steps"
        ] = route[
            "steps"
        ]

        navigation_state[
            "current_step"
        ] = 0

        navigation_state[
            "distance_meters"
        ] = route[
            "distance_meters"
        ]

        navigation_state[
            "duration_seconds"
        ] = route[
            "duration_seconds"
        ]

        navigation_state[
            "status"
        ] = "navigation_started"


    print()
    print(
        "========================================"
    )
    print(
        "🟢 NAVIGATION ACTIVE"
    )
    print(
        "========================================"
    )

    print(
        "Destination:",
        navigation_state[
            "destination"
        ]
    )

    print(
        "Distance:",
        round(
            route[
                "distance_meters"
            ]
        ),
        "meters"
    )

    print(
        "Duration:",
        round(
            route[
                "duration_seconds"
            ] / 60
        ),
        "minutes"
    )

    print(
        "Steps:",
        len(
            route[
                "steps"
            ]
        )
    )

    print(
        "========================================"
    )
    print()


    return jsonify({

        "success":
            True,

        "destination":
            navigation_state[
                "destination"
            ],

        "distance_meters":
            route[
                "distance_meters"
            ],

        "duration_seconds":
            route[
                "duration_seconds"
            ],

        "steps":
            route[
                "steps"
            ],

        "route":
            route[
                "geometry"
            ]

    })


# ============================================================
# BACKWARD-COMPATIBLE ENDPOINT
# ============================================================

@app.route(
    "/receive_location",
    methods=["POST"]
)
def receive_location():

    return start_navigation()


# ============================================================
# NAVIGATION STATUS
# ============================================================

@app.route(
    "/navigation_status",
    methods=["GET"]
)
def navigation_status():

    return last_summary()


# ============================================================
# LAST SUMMARY
# ============================================================

@app.route(
    "/last_summary",
    methods=["GET"]
)
def last_summary():

    with state_lock:

        active = navigation_state[
            "active"
        ]

        destination = navigation_state[
            "destination"
        ]

        current_location = navigation_state[
            "current_location"
        ]

        distance = navigation_state[
            "distance_meters"
        ]

        duration = navigation_state[
            "duration_seconds"
        ]

        status = navigation_state[
            "status"
        ]

        steps = navigation_state[
            "steps"
        ]

        current_step = navigation_state[
            "current_step"
        ]


    next_instruction = None


    if (
        steps
        and
        current_step < len(steps)
    ):

        next_instruction = steps[
            current_step
        ]


    return jsonify({

        "active":
            active,

        "current_location":
            current_location,

        "destination":
            destination,

        "distance_meters":
            distance,

        "duration_seconds":
            duration,

        "status":
            status,

        "current_step":
            current_step,

        "total_steps":
            len(steps),

        "next_instruction":
            next_instruction

    })


# ============================================================
# NEXT INSTRUCTION
# ============================================================

@app.route(
    "/next_instruction",
    methods=["GET"]
)
def next_instruction():

    with state_lock:

        if not navigation_state[
            "active"
        ]:

            return jsonify({

                "active":
                    False,

                "instruction":
                    ""

            })


        steps = navigation_state[
            "steps"
        ]

        current_step = navigation_state[
            "current_step"
        ]


        if (
            not steps
            or
            current_step >= len(steps)
        ):

            return jsonify({

                "active":
                    True,

                "instruction":
                    "You are approaching your destination."

            })


        step = steps[
            current_step
        ]


        return jsonify({

            "active":
                True,

            "instruction":
                step.get(
                    "instruction",
                    ""
                ),

            "distance_meters":
                step.get(
                    "distance_meters",
                    0
                ),

            "step":
                current_step,

            "total_steps":
                len(steps)

        })


# ============================================================
# CURRENT LOCATION
# ============================================================

@app.route(
    "/current_location",
    methods=["GET"]
)
def current_location():

    with state_lock:

        return jsonify({

            "location":
                navigation_state[
                    "current_location"
                ]

        })


# ============================================================
# ROUTE
# ============================================================

@app.route(
    "/route",
    methods=["GET"]
)
def get_route():

    with state_lock:

        route = navigation_state[
            "route"
        ]

        distance = navigation_state[
            "distance_meters"
        ]

        duration = navigation_state[
            "duration_seconds"
        ]


    if route is None:

        return jsonify({

            "success":
                False,

            "message":
                "No route available."

        }), 404


    return jsonify({

        "success":
            True,

        "route":
            route,

        "distance_meters":
            distance,

        "duration_seconds":
            duration

    })


# ============================================================
# STOP NAVIGATION
# ============================================================

@app.route(
    "/stop_navigation",
    methods=["POST"]
)
def stop_navigation():

    with state_lock:

        navigation_state[
            "active"
        ] = False

        navigation_state[
            "status"
        ] = "stopped"

        navigation_state[
            "steps"
        ] = []

        navigation_state[
            "current_step"
        ] = 0

        navigation_state[
            "route"
        ] = None

        navigation_state[
            "distance_meters"
        ] = None

        navigation_state[
            "duration_seconds"
        ] = None


    print(
        "🛑 Navigation stopped."
    )


    return jsonify({

        "success":
            True,

        "message":
            "Navigation stopped."

    })


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    print()
    print(
        "=========================================="
    )
    print(
        "       🤖 ULTRON NAVIGATION ENGINE"
    )
    print(
        "=========================================="
    )

    print()

    print(
        "🌐 Server:"
    )

    print(
        "   http://127.0.0.1:5002"
    )

    print()

    print(
        "📍 Live GPS + Map:"
    )

    print(
        "   http://127.0.0.1:5002/gps"
    )

    print()

    print(
        "❤️ Health:"
    )

    print(
        "   http://127.0.0.1:5002/health"
    )

    print()

    print(
        "=========================================="
    )

    print()


    app.run(

        host="0.0.0.0",

        port=PORT,

        debug=False,

        threaded=True

    )