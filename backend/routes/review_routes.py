from flask import Blueprint, request, jsonify

from supabase_client import supabase

review_bp = Blueprint(
    "review_bp",
    __name__
)

@review_bp.route("/reviews-test", methods=["GET"])
def reviews_test():
    return jsonify({
        "message": "Review routes working"
    })
    
@review_bp.route("/reviews/<int:hostel_id>", methods=["GET"])
def get_reviews(hostel_id):

    try:
        response = (
            supabase
            .table("reviews")
            .select("*")
            .eq("hostel_id", hostel_id)
            .execute()
        )

        return jsonify({
            "success": True,
            "count": len(response.data),
            "reviews": response.data
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
        
        
@review_bp.route("/reviews", methods=["POST"])
def add_review():

    data = request.get_json()

    hostel_id = data.get("hostel_id")
    reviewer_name = data.get("reviewer_name")
    review_text = data.get("review_text")
    biggest_advantage = data.get("biggest_advantage")
    biggest_problem = data.get("biggest_problem")
    unresolved_issues = data.get("unresolved_issues")
    mess_cut_available = data.get("mess_cut_available")
    rent_cut_available = data.get("rent_cut_available")
    recommend = data.get("recommend")

    if not hostel_id or not reviewer_name or not review_text:

        return jsonify({
            "success": False,
            "message": "Required fields missing"
        }), 400

    review_data = {
    "hostel_id": hostel_id,
    "reviewer_name": reviewer_name,
    "review_text": review_text,
    "biggest_advantage": biggest_advantage,
    "biggest_problem": biggest_problem,
    "unresolved_issues": unresolved_issues,
    "mess_cut_available": mess_cut_available,
    "rent_cut_available": rent_cut_available,
    "recommend": recommend
    }
    
    try:

        response = (
        supabase
        .table("reviews")
        .insert(review_data)
        .execute()
        )

        return jsonify({
        "success": True,
        "review": response.data
        }), 201

    except Exception as e:

        return jsonify({
        "success": False,
        "error": str(e)
        }), 500
        
@review_bp.route("/reviews/<int:review_id>", methods=["DELETE"])
def delete_review(review_id):

    try:

        response = (
        supabase
        .table("reviews")
        .delete()
        .eq("review_id", review_id)
        .execute()
        )
        
        if not response.data:

            return jsonify({
                "success": False,
                "message": "Review not found"
            }), 404

        return jsonify({
        "success": True,
        "message": f"Review {review_id} deleted"
        })

    except Exception as e:

        return jsonify({
        "success": False,
        "error": str(e)
        }), 500