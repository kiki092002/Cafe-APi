import random

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean

app = Flask(__name__)


# CREATE DB
class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
'''read_record(): search for random cafe'''


@app.route("/random", methods=["GET"])
def read_record():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)
    return jsonify(cafe={
        "id": random_cafe.id,
        "name": random_cafe.name,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,
        "has_sockets": random_cafe.has_sockets,
        "has_toilet": random_cafe.has_toilet,
        "has_wifi": random_cafe.has_wifi,
        "can_take_calls": random_cafe.can_take_calls,
        "seats": random_cafe.seats,
        "coffee_price": random_cafe.coffee_price,
    })


'''get_all(): get all the cafes information'''


@app.route("/all", methods=["GET"])
def get_all():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    list_cafes = []
    for cafe in all_cafes:
        list_cafes.append(cafe.to_dict())
    return jsonify(cafes=list_cafes)


'''search_loc(): search for the specific cafe's location '''


@app.route("/search")
def search_loc():
    q = request.args.get("loc")
    result = db.session.execute(db.select(Cafe).where(Cafe.location == q))
    all_cafes = result.scalars().all()
    if all_cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])
    else:
        return jsonify(error={"Not Found": "Sorry,we don't have a cafe at that location,"}), 404


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def create_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        has_sockets=request.form.get("has_sockets"),
        has_toilet=request.form.get("has_toilet"),
        has_wifi=request.form.get("has_wifi"),
        can_take_calls=request.form.get("can_take_call"),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price")
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(respone={"success": "Successfully added the new cafe."})


# HTTP PUT(update entire data to replace previous one)/PATCH(update piece of data) - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_cafe_id(cafe_id):
    q = request.args.get("new_price")
    cafe = db.session.get(Cafe, cafe_id)
    if cafe:
        cafe.coffee_price = q
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}),200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}),404


# HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
