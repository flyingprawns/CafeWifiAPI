from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random", methods=["GET"])
def get_random_cafe():
    all_cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(all_cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all", methods=["GET"])
def get_all_cafes():
    all_cafes = db.session.query(Cafe).all()
    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])


@app.route("/search", methods=["GET"])
def get_cafe_at_location():
    query_location = request.args.get('loc')
    cafe_list = Cafe.query.filter_by(location=query_location).all()
    cafe_list = [cafe.to_dict() for cafe in cafe_list]
    if cafe_list:
        return jsonify(cafe=cafe_list)
    else:
        return jsonify(error={"Not Found": f"Sorry, no cafes were found at location: {query_location}."})


# HTTP POST - Create Record
@app.route("/add", methods=["GET", "POST"])
def post_new_cafe():
    if request.method == "POST":
        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("loc"),
            has_sockets=bool(request.form.get("sockets")),
            has_toilet=bool(request.form.get("toilet")),
            has_wifi=bool(request.form.get("wifi")),
            can_take_calls=bool(request.form.get("calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe."})
    else:
        return render_template("add.html")


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["GET", "POST"])
def update_coffee_price(cafe_id):
    cafe = db.session.query(Cafe).get(cafe_id)
    if not cafe:
        return jsonify(response={"error": f"Cafe with id {cafe_id} does not exist."})

    new_price = request.args.get('price')
    if not new_price or not new_price.isnumeric():
        return jsonify(response={"error": f"{new_price} is not a valid price."})
    cafe.coffee_price = new_price
    db.session.commit()
    return jsonify(response={"success": f"Successfully updated price for cafe {cafe.name}."})


# HTTP DELETE - Delete Record
@app.route("/remove/<int:cafe_id>", methods=["GET", "DELETE"])
def remove_cafe(cafe_id):
    secret_key = request.args.get("api_key")
    if secret_key != "SUPERSECRETKEY":
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403

    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        db.session.delete(cafe)
        db.session.commit()
        return jsonify(response={"success": f"Cafe with id {cafe_id} was deleted."}), 200
    else:
        return jsonify(response={"error": f"Cafe with id {cafe_id} does not exist."}), 404


if __name__ == '__main__':
    app.run(debug=True)
