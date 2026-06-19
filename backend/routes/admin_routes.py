from flask import Blueprint, jsonify, request
from supabase_client import supabase

admin_bp = Blueprint(
    "admin_bp",
    __name__
)

@admin_bp.route("/admin/test", methods=["GET"])
def admin_test():
    return jsonify({
        "success": True,
        "message": "Admin routes working"
    }), 200
    
@admin_bp.route("/admin/login", methods=["POST"])
def admin_login():

    try:

        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({
                "success": False,
                "message": "Username and password are required"
            }), 400

        admin_response = (
            supabase
            .table("admins")
            .select("*")
            .eq("username", username)
            .execute()
        )

        if not admin_response.data:
            return jsonify({
                "success": False,
                "message": "Invalid username or password"
            }), 401

        admin = admin_response.data[0]

        if admin["password_hash"] != password:
            return jsonify({
                "success": False,
                "message": "Invalid username or password"
            }), 401

        return jsonify({
            "success": True,
            "message": "Login successful"
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
        
@admin_bp.route("/admin/hostels", methods=["POST"])
def add_hostel():

    try:

        data = request.get_json()

        # Hostel Details
        hostel_name = data.get("hostel_name")
        hostel_type = data.get("hostel_type")
        address = data.get("address")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        contact_number = data.get("contact_number")
        distance_from_college = data.get("distance_from_college")
        vacancies = data.get("vacancies")
        advance_amount = data.get("advance_amount")

        # Facilities
        wifi = data.get("wifi")
        mess = data.get("mess")
        parking = data.get("parking")
        gym = data.get("gym")
        attached_bathroom = data.get("attached_bathroom")
        washing_machine = data.get("washing_machine")
        cleaning_service = data.get("cleaning_service")
        study_area = data.get("study_area")
        hot_water = data.get("hot_water")
        water_bill_included = data.get("water_bill_included")
        electricity_bill_included = data.get("electricity_bill_included")
        laundry_stone = data.get("laundry_stone")
        bed = data.get("bed")
        study_table = data.get("study_table")
        cupboard = data.get("cupboard")
        shared_kitchen = data.get("shared_kitchen")
        gas_connection = data.get("gas_connection")
        appliances_allowed = data.get("appliances_allowed")
        other = data.get("other")

        # Room Types
        room_types = data.get("room_types")

        if not all([
            hostel_name,
            hostel_type,
            distance_from_college,
            vacancies is not None,
            room_types
        ]):
            return jsonify({
                "success": False,
                "message": "Missing required fields"
            }), 400

        # Insert Hostel
        hostel_response = (
            supabase
            .table("hostels")
            .insert({
                "hostel_name": hostel_name,
                "hostel_type": hostel_type,
                "address": address,
                "latitude": latitude,
                "longitude": longitude,
                "contact_number": contact_number,
                "distance_from_college": distance_from_college,
                "vacancies": vacancies,
                "advance_amount": advance_amount,
                
            })
            .execute()
        )

        hostel_id = hostel_response.data[0]["hostel_id"]

        # Insert Facilities
        (
            supabase
            .table("facilities")
            .insert({
                "hostel_id": hostel_id,
                "mess": mess,
                "attached_bathroom": attached_bathroom,
                "wifi": wifi,
                "washing_machine": washing_machine,
                "cleaning_service": cleaning_service,
                "study_area": study_area,
                "parking": parking,
                "hot_water": hot_water,
                "water_bill_included": water_bill_included,
                "electricity_bill_included": electricity_bill_included,
                "laundry_stone": laundry_stone,
                "gym": gym,
                "bed": bed,
                "study_table": study_table,
                "cupboard": cupboard,
                "shared_kitchen": shared_kitchen,
                "gas_connection": gas_connection,
                "appliances_allowed": appliances_allowed,
                "other": other
            })
            .execute()
        )

        # Insert Room Types
        for room in room_types:

            (
                supabase
                .table("room_types")
                .insert({
                    "hostel_id": hostel_id,
                    "room_type": room["room_type"],
                    "monthly_rent": room["monthly_rent"]
                })
                .execute()
            )

        return jsonify({
            "success": True,
            "message": "Hostel created successfully",
            "hostel_id": hostel_id
        }), 201

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
        
@admin_bp.route("/admin/hostels/<int:hostel_id>", methods=["DELETE"])
def delete_hostel(hostel_id):

    try:

        hostel_response = (
            supabase
            .table("hostels")
            .select("hostel_id")
            .eq("hostel_id", hostel_id)
            .execute()
        )

        if not hostel_response.data:
            return jsonify({
                "success": False,
                "message": "Hostel not found"
            }), 404

        (
            supabase
            .table("reviews")
            .delete()
            .eq("hostel_id", hostel_id)
            .execute()
        )

        (
            supabase
            .table("ratings")
            .delete()
            .eq("hostel_id", hostel_id)
            .execute()
        )

        (
            supabase
            .table("room_types")
            .delete()
            .eq("hostel_id", hostel_id)
            .execute()
        )

        (
            supabase
            .table("facilities")
            .delete()
            .eq("hostel_id", hostel_id)
            .execute()
        )

        (
            supabase
            .table("hostels")
            .delete()
            .eq("hostel_id", hostel_id)
            .execute()
        )

        return jsonify({
            "success": True,
            "message": "Hostel deleted successfully"
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
        
@admin_bp.route("/admin/hostels", methods=["GET"])
def get_admin_hostels():

    try:

        response = (
            supabase
            .table("hostels")
            .select("""
                hostel_id,
                hostel_name,
                hostel_type,
                distance_from_college,
                vacancies,

                ratings (
                    overall_rating
                ),

                room_types (
                    monthly_rent
                )
            """)
            .execute()
        )

        hostels = []

        for hostel in response.data:

            overall_rating = None

            if hostel.get("ratings"):
                ratings = hostel["ratings"]

                if len(ratings) > 0:
                    overall_rating = ratings[0].get(
                        "overall_rating"
                    )

            lowest_rent = None

            if hostel.get("room_types"):

                rents = [
                    room["monthly_rent"]
                    for room in hostel["room_types"]
                    if room["monthly_rent"] is not None
                ]

                if rents:
                    lowest_rent = min(rents)

            hostels.append({
                "hostel_id": hostel["hostel_id"],
                "hostel_name": hostel["hostel_name"],
                "hostel_type": hostel["hostel_type"],
                "distance_from_college":
                    hostel["distance_from_college"],
                "vacancies":
                    hostel["vacancies"],
                "overall_rating":
                    overall_rating,
                "lowest_rent":
                    lowest_rent
            })

        return jsonify({
            "success": True,
            "count": len(hostels),
            "hostels": hostels
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
        
@admin_bp.route("/admin/hostels/<int:hostel_id>", methods=["PUT"])
def update_hostel(hostel_id):

    try:

        data = request.get_json()

        hostel_response = (
            supabase
            .table("hostels")
            .select("hostel_id")
            .eq("hostel_id", hostel_id)
            .execute()
        )

        if not hostel_response.data:
            return jsonify({
                "success": False,
                "message": "Hostel not found"
            }), 404

        # Update Hostel
        (
            supabase
            .table("hostels")
            .update({
                "hostel_name": data.get("hostel_name"),
                "hostel_type": data.get("hostel_type"),
                "address": data.get("address"),
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "contact_number": data.get("contact_number"),
                "distance_from_college": data.get("distance_from_college"),
                "vacancies": data.get("vacancies"),
                "advance_amount": data.get("advance_amount")
            })
            .eq("hostel_id", hostel_id)
            .execute()
        )

        # Update Facilities
        (
            supabase
            .table("facilities")
            .update({
                "mess": data.get("mess"),
                "attached_bathroom": data.get("attached_bathroom"),
                "wifi": data.get("wifi"),
                "washing_machine": data.get("washing_machine"),
                "cleaning_service": data.get("cleaning_service"),
                "study_area": data.get("study_area"),
                "parking": data.get("parking"),
                "hot_water": data.get("hot_water"),
                "water_bill_included": data.get("water_bill_included"),
                "electricity_bill_included": data.get("electricity_bill_included"),
                "laundry_stone": data.get("laundry_stone"),
                "gym": data.get("gym"),
                "bed": data.get("bed"),
                "study_table": data.get("study_table"),
                "cupboard": data.get("cupboard"),
                "shared_kitchen": data.get("shared_kitchen"),
                "gas_connection": data.get("gas_connection"),
                "appliances_allowed": data.get("appliances_allowed"),
                "other": data.get("other")
            })
            .eq("hostel_id", hostel_id)
            .execute()
        )

        # Replace Room Types
        (
            supabase
            .table("room_types")
            .delete()
            .eq("hostel_id", hostel_id)
            .execute()
        )

        room_types = data.get("room_types", [])

        for room in room_types:

            (
                supabase
                .table("room_types")
                .insert({
                    "hostel_id": hostel_id,
                    "room_type": room["room_type"],
                    "monthly_rent": room["monthly_rent"]
                })
                .execute()
            )

        return jsonify({
            "success": True,
            "message": "Hostel updated successfully"
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500