from flask import Blueprint, jsonify, request
from supabase_client import supabase

hostel_bp = Blueprint(
    "hostel_bp",
    __name__
)

@hostel_bp.route("/hostels", methods=["GET"])
def get_hostels():

    try:

        search = request.args.get("search")
        gender = request.args.get("gender")
        sort_by = request.args.get("sort")
        #vacant = request.args.get("vacant")
        sort_fields = []
        if sort_by:
            sort_fields = [
                field.strip()
                for field in sort_by.split(",")
            ]
        allowed_sorts = {
            "distance",
            "rating",
            "rent_asc",
            "rent_desc"
        }

        for field in sort_fields:
            if field not in allowed_sorts:
                return jsonify({
                    "success": False,
                    "message": f"Invalid sort: {field}"
                }), 400

        max_budget = request.args.get("max_budget")
        max_distance = request.args.get("max_distance")
        wifi = request.args.get("wifi", "").lower()
        mess = request.args.get("mess", "").lower()
        parking = request.args.get("parking", "").lower()
        gym = request.args.get("gym", "").lower()
        laundry = request.args.get("laundry", "").lower()

        try:
            if max_budget:
                max_budget = float(max_budget)

        except ValueError:
            return jsonify({
                "success": False,
                "message": "Invalid filter value"
            }), 400

        try:
            page = int(request.args.get("page", 1))
            limit = int(request.args.get("limit", 20))
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Invalid page or limit"
            }), 400
        limit = min(limit, 100)
        if page < 1:
            page = 1
        if limit < 1:
            limit = 20
        
        query = (
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
                    room_type,
                    monthly_rent
                ),

                facilities (
                    wifi,
                    mess,
                    parking,
                    gym,
                    washing_machine
                )
            """)
        )

        if search:
            query = query.ilike(
                "hostel_name",
                f"%{search}%"
            )

        if gender:
            query = query.eq(
                "hostel_type",
                gender
            )

        try:
            if max_distance:
                max_distance = float(max_distance)
                query = query.lte("distance_from_college", max_distance)
        except ValueError:
            return jsonify({
                "success": False,
                "message": "Invalid max_distance value"
            }), 400

        response = query.execute()
        hostels = []
        for hostel in response.data:
            # rating
            overall_rating = None
            ratings = hostel.get("ratings")
            if ratings:
                if isinstance(ratings, list):
                    overall_rating = ratings[0].get("overall_rating")
                else:
                    overall_rating = ratings.get("overall_rating")

            # lowest rent
            lowest_rent = None
            if hostel.get("room_types"):
                rents = [
                    room["monthly_rent"]
                    for room in hostel["room_types"]
                    if room["monthly_rent"] is not None
                ]
                if rents:
                    lowest_rent = min(rents)
            facilities = hostel.get("facilities") or {}

            hostels.append({
                "hostel_id": hostel["hostel_id"],
                "hostel_name": hostel["hostel_name"],
                "hostel_type": hostel["hostel_type"],
                "distance_from_college": hostel.get("distance_from_college"),
                "vacancies": hostel.get("vacancies"),
                "overall_rating": overall_rating,
                "lowest_rent": lowest_rent,
                "facilities": facilities
            })

        # --------------------
        # FILTERS
        # --------------------
        # Budget
        if max_budget is not None:
            hostels = [
                hostel
                for hostel in hostels
                if hostel["lowest_rent"] is not None
                and hostel["lowest_rent"] <= max_budget
            ]
        
        # Wifi
        if wifi == "true":
            hostels = [
                hostel
                for hostel in hostels
                if hostel["facilities"].get("wifi") == True
            ]
        # Mess
        if mess == "true":
            hostels = [
                hostel
                for hostel in hostels
                if hostel["facilities"].get("mess") == True
            ]
        # Parking
        if parking == "true":
            hostels = [
                hostel
                for hostel in hostels
                if hostel["facilities"].get("parking") == True
            ]
        # Gym
        if gym == "true":
            hostels = [
                hostel
                for hostel in hostels
                if hostel["facilities"].get("gym") == True
            ]
        # Laundry
        if laundry == "true":
            hostels = [
                hostel
                for hostel in hostels
                if hostel["facilities"].get("washing_machine") == True
            ]

        # --------------------
        # SORT_BY
        # --------------------
        for field in reversed(sort_fields):

            if field == "distance":
                hostels.sort(
                    key=lambda x:
                    x["distance_from_college"]
                    if x["distance_from_college"] is not None
                    else float("inf")
                )

            elif field == "rating":
                hostels.sort(
                    key=lambda x:
                    x["overall_rating"]
                    if x["overall_rating"] is not None
                    else 0,
                    reverse=True
                )

            elif field == "rent_asc":
                hostels.sort(
                    key=lambda x:
                    x["lowest_rent"]
                    if x["lowest_rent"] is not None
                    else float("inf")
                )

            elif field == "rent_desc":
                hostels.sort(
                    key=lambda x:
                    x["lowest_rent"]
                    if x["lowest_rent"] is not None
                    else 0,
                    reverse=True
                )

        for hostel in hostels:
            hostel.pop("room_types", None)
            #hostel.pop("facilities", None)

        # --------------------
        # PAGINATION
        # --------------------

        start = (page - 1) * limit
        end = start + limit

        paginated_hostels = hostels[start:end]

        return jsonify({
            "success": True,
            "count": len(hostels),   # total results after filtering
            "page": page,
            "limit": limit,
            "total_pages": (
                len(hostels) + limit - 1
            ) // limit,
            "filters": {
                "search": search,
                "gender": gender,
                "max_budget": max_budget,
            },

            "hostels": paginated_hostels
        }), 200

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
@hostel_bp.route("/hostels/<int:hostel_id>", methods=["GET"])
def get_hostel_details(hostel_id):

    try:

        hostel_response = (
            supabase
            .table("hostels")
            .select("*")
            .eq("hostel_id", hostel_id)
            .execute()
        )

        if not hostel_response.data:
            return jsonify({
                "success": False,
                "message": "Hostel not found"
            }), 404
        hostel = hostel_response.data[0]

        # Room Types
        room_types_response = (
            supabase
            .table("room_types")
            .select("*")
            .eq("hostel_id", hostel_id)
            .execute()
        )
        room_types = room_types_response.data

        # Facilities
        facilities_response = (
            supabase
            .table("facilities")
            .select("*")
            .eq("hostel_id", hostel_id)
            .execute()
        )

        facilities = (
            facilities_response.data[0]
            if facilities_response.data
            else None
        )

        # Ratings
        ratings_response = (
            supabase
            .table("ratings")
            .select("*")
            .eq("hostel_id", hostel_id)
            .execute()
        )
        rating = (
            ratings_response.data[0]
            if ratings_response.data
            else None
        )
        return jsonify({
            "success": True,
            "hostel": hostel,
            "room_types": room_types,
            "facilities": facilities,
            "rating": rating
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    
@hostel_bp.route("/compare", methods=["GET"])
def compare_hostels():
    try:
        hostel1_id = request.args.get("hostel1")
        hostel2_id = request.args.get("hostel2")

        if not hostel1_id or not hostel2_id:
            return jsonify({
                "success": False,
                "message": "hostel1 and hostel2 are required"
            }), 400

        hostel1_response = (
            supabase
            .table("hostels")
            .select("*")
            .eq("hostel_id", hostel1_id)
            .execute()
        )

        hostel2_response = (
            supabase
            .table("hostels")
            .select("*")
            .eq("hostel_id", hostel2_id)
            .execute()
        )

        if not hostel1_response.data:
            return jsonify({
                "success": False,
                "message": "Hostel 1 not found"
            }), 404

        if not hostel2_response.data:
            return jsonify({
                "success": False,
                "message": "Hostel 2 not found"
            }), 404

        hostel1 = hostel1_response.data[0]
        hostel2 = hostel2_response.data[0]

        facilities1 = (
        supabase
        .table("facilities")
        .select("*")
        .eq("hostel_id", hostel1_id)
        .execute()
    )

        facilities1 = (
            facilities1.data[0]
            if facilities1.data
            else None
        )

        facilities2 = (
            supabase
            .table("facilities")
            .select("*")
            .eq("hostel_id", hostel2_id)
            .execute()
        )

        facilities2 = (
            facilities2.data[0]
            if facilities2.data
            else None
        )

        room_types1 = (
            supabase
            .table("room_types")
            .select("*")
            .eq("hostel_id", hostel1_id)
            .execute()
        )
        room_types1 = room_types1.data
        room_types2 = (
            supabase
            .table("room_types")
            .select("*")
            .eq("hostel_id", hostel2_id)
            .execute()
        )
        room_types2 = room_types2.data

        rating1 = (
            supabase
            .table("ratings")
            .select("*")
            .eq("hostel_id", hostel1_id)
            .execute()
        )
        rating1 = (
            rating1.data[0]
            if rating1.data
            else None
        )
        rating2 = (
            supabase
            .table("ratings")
            .select("*")
            .eq("hostel_id", hostel2_id)
            .execute()
        )

        rating2 = (
            rating2.data[0]
            if rating2.data
            else None
        )

        def build_comparison_hostel(
            hostel,
            facilities,
            rating,
            room_types
        ):

            rents = [
                room["monthly_rent"]
                for room in room_types
                if room.get("monthly_rent") is not None
            ]

            lowest_rent = (
                min(rents)
                if rents
                else None
            )

            return {
                "hostel_id": hostel["hostel_id"],
                "hostel_name": hostel["hostel_name"],
                "hostel_type": hostel["hostel_type"],

                "overall_rating": (
                    rating.get("overall_rating")
                    if rating
                    else None
                ),

                "lowest_rent": lowest_rent,

                "address": hostel.get("address"),
                "distance_from_college": hostel.get(
                    "distance_from_college"
                ),
                "vacancies": hostel.get("vacancies"),

                "wifi": (
                    facilities.get("wifi")
                    if facilities
                    else None
                ),

                "mess": (
                    facilities.get("mess")
                    if facilities
                    else None
                ),

                "parking": (
                    facilities.get("parking")
                    if facilities
                    else None
                ),

                "laundry": (
                    facilities.get("washing_machine")
                    if facilities
                    else None
                ),

                "water_bill_included": (
                    facilities.get("water_bill_included")
                    if facilities
                    else None
                ),

                "electricity_bill_included": (
                    facilities.get(
                        "electricity_bill_included"
                    )
                    if facilities
                    else None
                )
            }

        comparison_hostel1 = build_comparison_hostel(
            hostel1,
            facilities1,
            rating1,
            room_types1
        )

        comparison_hostel2 = build_comparison_hostel(
            hostel2,
            facilities2,
            rating2,
            room_types2
        )

        return jsonify({
            "success": True,
            "hostel1": comparison_hostel1,
            "hostel2": comparison_hostel2
        }), 200

    except Exception as e:
        return jsonify({
                "success": False,
                "error": str(e)
            }), 500