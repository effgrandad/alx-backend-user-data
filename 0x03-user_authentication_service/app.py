#!/usr/bin/env python3
"""
Flask app module
"""

from flask import Flask, request, jsonify, make_response, abort
from auth import Auth

app = Flask(__name__)
AUTH = Auth()


@app.route("/methods=['GET']")
def welcome() -> str:
    """
    Welcome route

    Returns:
        dict: A JSON payload with the message "Bienvenue"
    """
    return jsonify({"message": "Bienvenue"})


@app.route("/users", methods=["POST"])
def register_user():
    """
    Register a new user
    """
    email = request.form.get("email")
    password = request.form.get("password")

    try:
        user = AUTH.register_user(email, password)
        return jsonify({"email": email, "message": "user created"})
    except ValueError as err:
        return jsonify({"message": str(err)}), 400


@app.route('/sessions', methods=['POST'])
def login():
    """
    Generates a login function responding to the POST /sessions route.
    """
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        abort(400)

    if AUTH.valid_login(email, password):
        session_id = AUTH.create_session(email)
        response = jsonify({'email': email, 'message': 'logged in'})
        response.set_cookie('session_id', session_id)
        return response
    else:
        abort(401)


@app.route('/sessions', methods=['DELETE'])
def logout():
    """
    Creates destroy session
    """
    session_id = request.cookies.get('session_id')
    if session_id:
        user = AUTH.get_user_from_session_id(session_id)
        if user:
            AUTH.destroy_session(user.id)
            return redirect('/')
        else:
            abort(403)
    else:
        abort(403)


@app.route("/profile", methods=["GET"])
def profile():
    """
    Generates a profile function that responds to the GET /profile route.
    """
    session_id = request.cookies.get("session_id")

    if session_id is None or session_id not in users:
        abort(403)
    user_data = users[session_id]
    if user_data is None:
        abort(403)

    email = user_data["email"]
    return jsonify({"email": email}), 200


@app.route('/reset_password', methods=['POST'])
def get_reset_password_token():
    """
    Generates function responding to the POST /reset_password route.
    """
    email = request.form.get('email')
    try:
        reset_token = AUTH.get_reset_password_token(email)
    except ValueError:
        return jsonify({"error": "Email not registered"}), 403
    return jsonify({"email": email, "reset_token": reset_token}), 200


@app.route('/reset_password', methods=['PUT'])
def update_password():
    """
    generate function responding to the PUT /reset_password route.
    """
    try:
        email = request.form.get('email')
        reset_token = request.form.get('reset_token')
        new_password = request.form.get('new_password')

        AUTH.update_password(reset_token, new_password)

        return jsonify({"email": email, "message": "Password updated"}), 200
    except ValueError:
        return jsonify({"message": "Invalid reset token"}), 403


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
