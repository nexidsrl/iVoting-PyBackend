from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from db_controller import DBController

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('org_name')
parser.add_argument('users')

db_controller = DBController()

class NewSubmit(Resource):

    def post(self):
        args = parser.parse_args()
        print(args)
        db_controller.insertOrg(name=args['org_name'], active=0)
        org_id = db_controller.getOrgIdByName(name=args['org_name'])
        db_controller.insertHeaderList(label=args['org_name'], organization_id=org_id)
        list_id = db_controller.getHeaderListIdByLabel(label=args['org_name'])
        users=args['users'].split(',')
        for user in users:
            db_controller.insertUserOnlyCodFisType(codice_fiscale=user, type='M')
            user_id = db_controller.getUserIdByCodFIs(codice_fiscale=user)
            db_controller.insertMember(organization_id=org_id, user_id=user_id, type='M')
            db_controller.insertList(email=user, user_id=user_id, header_list_id=list_id)

        return {"status": True}


api.add_resource(NewSubmit, '/submit')


if __name__ == '__main__':
    app.run(debug=True, port=4444)
