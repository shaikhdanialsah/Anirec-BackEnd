# reviews.py

from flask import Blueprint, jsonify, request
from database import get_db_connection

# Create a Blueprint for reviews
reviews_bp = Blueprint('reviews', __name__)

# Get reviews for a specific anime
@reviews_bp.route('/api/reviews/<int:anime_id>', methods=['GET'])
def get_reviews(anime_id):
    try:
        # Establish database connection
        conn = get_db_connection()
        cur = conn.cursor()

        # Fetch reviews for the specified anime ID
        cur.execute('''
            SELECT "review".id, "review".anime_id, "review".user_id, "users".name, "review".comment, "review".created_at, "users".profile_picture, "users".wallpaper, "users".favourites_count, "users".reviews_count
            FROM "review"
            JOIN "users" ON "review".user_id = "users".id
            WHERE "review".anime_id = %s
            ORDER BY "review".created_at DESC
        ''', (anime_id,))
        reviews = cur.fetchall()

        # Format the response to include detailed review data
        review_list = [
            {
                "id": review[0],
                "anime_id": review[1],
                "user_id": review[2],
                "name": review[3],
                "comment": review[4],
                "created_at": review[5],
                "profile_picture": review[6],
                "wallpaper": review[7],
                "favourites_count":review[8],
                "reviews_count":review[9]
            }
            for review in reviews
        ]

        cur.close()
        conn.close()

        return jsonify({"reviews": review_list}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Failed to fetch reviews"}), 500

# Add a review for an anime
@reviews_bp.route('/api/add-review', methods=['POST'])
def add_review():
    try:
        # Parse JSON request data
        data = request.get_json()
        user_id = data.get('user_id')
        anime_id = data.get('anime_id')
        comment = data.get('comment')

        # Validate input data
        if not user_id or not anime_id or not comment:
            return jsonify({"error": "Missing required fields: user_id, anime_id, or comment"}), 400

        # Establish database connection
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert review into the database
        cur.execute(
            '''
            INSERT INTO "review" (user_id, anime_id, comment, created_at)
            VALUES (%s, %s, %s, NOW())
            ''',
            (user_id, anime_id, comment)
        )
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({"message": "Review added successfully!"}), 200
    except Exception as e:
        print(f"Error adding review: {e}")
        return jsonify({"error": "Failed to add review"}), 500

# Get reviews made by a specific user
@reviews_bp.route('/api/user-reviews/<int:user_id>', methods=['GET'])
def get_user_reviews(user_id):
    try:
        # Establish database connection
        conn = get_db_connection()
        cur = conn.cursor()

        # Fetch reviews for the specified user ID
        cur.execute('''
            SELECT 
                "review".id, 
                "review".anime_id, 
                "anime".title, 
                "review".comment, 
                "review".created_at,
                "review".user_id,
                "users".name,
                "users".profile_picture
            FROM "review"
            JOIN "anime" ON "review".anime_id = "anime".anime_id
            JOIN "users" ON "review".user_id = "users".id
            WHERE "users".id = %s
            ORDER BY "review".created_at DESC
        ''', (user_id,))
        reviews = cur.fetchall()

        # Format the response to include detailed review data
        review_list = [
            {
                "id": review[0],
                "anime_id": review[1],
                "title": review[2],
                "comment": review[3],
                "created_at": review[4],
                "user_id": review[5],
                "name": review[6],
                "profile_picture": review[7],
            }
            for review in reviews
        ]

        cur.close()
        conn.close()

        return jsonify({"reviews": review_list}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Failed to fetch reviews"}), 500
    
# Delete a review by review_id
@reviews_bp.route('/api/delete-review', methods=['DELETE'])
def delete_review():
    try:
        # Parse JSON request data
        data = request.get_json()
        review_id = data.get('review_id')

        # Validate input data
        if not review_id:
            return jsonify({"error": "Missing required field: review_id"}), 400

        # Establish database connection
        conn = get_db_connection()
        cur = conn.cursor()

        # Delete the review that matches the review_id
        cur.execute('''
            DELETE FROM "review"
            WHERE "id" = %s
        ''', (review_id,))
        
        # Commit the transaction
        conn.commit()

        # Check if the review was deleted
        if cur.rowcount == 0:
            return jsonify({"error": "No review found with the specified review_id"}), 404

        cur.close()
        conn.close()

        return jsonify({"message": "Review deleted successfully!"}), 200
    except Exception as e:
        print(f"Error deleting review: {e}")
        return jsonify({"error": "Failed to delete review"}), 500

