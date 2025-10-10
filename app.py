from flask import Flask
from flask_restful import Api, Resource


app = Flask(__name__)
api = Api(app)


class HelloWorld(Resource):
    def get(self):
        return {"message": "Hello, world"}


api.add_resource(HelloWorld, "/test")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5005, debug=True)
