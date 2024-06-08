# from . import bp 
# from .repo import Repo

from .exceptions import InvalidMotivation
from flask import request


from flask import jsonify, session, request, redirect, url_for
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_bcrypt import bcrypt

from flask_socketio import send, emit

# from .user import User

def register_routes(bp, socketio, service):
    @bp.route('/ping', methods=['GET'])
    def ping():
        if request.method=='GET':
            return "yes"

    @bp.route('/get/<id>', methods=['GET'])
    def get(id):
        if request.method=='GET':
            try:
                id=int(id)
                return service.get(id)
            except ValueError:
                return "Invalid ID"
            except Exception as e:
                return str(e)

    @bp.route('/get/all', methods=['GET'])
    # @jwt_required()
    def get_all():
        if request.method=='GET':
            return service.get_all_dict()

    @bp.route('/add', methods=['POST'])
    def add():
        if request.method=='POST':
            try:
                motivation_dict = service.add( request.get_json() )
                emit_client_refresh()
                return motivation_dict
            except InvalidMotivation as e:
                for err in e.args[0]:
                    print(err)
                return str(e)

    @bp.route('/remove', methods=['DELETE'])
    def remove():
        if request.method=='DELETE':
            try:
                delete_id=request.get_json()["id"]
                service.remove(delete_id)
                emit_client_refresh()
                return {}
            except Exception as e:
                return str(e)
        return 404

    @bp.route('/sort', methods=['PUT'])
    @jwt_required()
    def toggle_sort_flag():
        return "this is the return"
        if request.method=='PUT':
            service.toggle_sorting()
            return {}
        return 402
    
    @bp.route('/do_faker', methods=['GET'])
    def faker_stuff():
        # service.add_faker_data()
        service.add_secondary_faker_data()
        return {}

    @bp.route('/update/<id>', methods=['PUT'])
    @jwt_required()
    def update(id):
        if request.method=='PUT':
            id=int(id)
            response = service.update(id, request.get_json())
            emit_client_refresh()
            return response.to_dict()

    @bp.route('/page', methods=['POST'])
    @jwt_required()
    def get_page():
        if request.method=='POST':
            try:
                data_json=request.get_json()
                page_index=int(data_json["index"])
                page_size=int(data_json["size"])
                name_key=None
                if "name_key" in data_json.keys():
                    name_key=data_json["name_key"]
                strength_key=None
                if "strength_key" in data_json.keys():
                    strength_key=int(data_json["strength_key"])
                    if strength_key<0:
                        strength_key=None
                if "sort_by_name" in data_json.keys():
                    sort_by_name = bool(data_json["sort_by_name"])
                page, actual_index, max_page_size=service.get_filter_page(page_index, page_size, name_key, strength_key, sort_by_name)
                page=[ x.to_dict() for x in page]
                return {
                    "elements" : page,
                    "index": actual_index,
                    "max_page_size":max_page_size
                }
            except Exception as e:
                return str(e)
        return 404

    # @bp.route("/get/strengths", methods=['GET'])
    # def get_strengths():
    #     if request.method=='GET':
    #         ss=service.get_strenghts()
    #         return list(ss)
    #     return 402
    
    @bp.route("/founder/<id>", methods=['GET'])
    def get_founder_id(id):
        if request.method=='GET':
            try:
                return service.founder_get(id)
            except Exception as e:
                return str(e), 404 
    
    @bp.route("/founder", methods=['POST'])
    def founder_add():
        if request.method=='POST':
            try:
                founder_dict=request.get_json() 
                motivation_id=int(founder_dict['motivation_id'])
                name=str(founder_dict['name'])
                email=str(founder_dict['email'])
                service.founder_add(motivation_id, name, email)
                return {},202
            except Exception as e:
                # for err in e.args[0]:
                #     print(err)
                return {"error":str(e)}, 404
            
    @bp.route("/founder", methods=['DELETE'])
    def founder_remove():
        if request.method=='DELETE':
            try:
                delete_id=int(request.get_json()["id"])
                service.founder_remove(delete_id)
                return {},201
            except Exception as e:
                return str(e), 404
        return {}, 404

    @bp.route("/founder", methods=['PUT'])
    def founder_update():
        if request.method=="PUT":
            try:
                founder_dict=request.get_json() 
                id=int(founder_dict['id'])
                motivation_id=int(founder_dict['motivation_id'])
                name=str(founder_dict['name'])
                email=str(founder_dict['email'])
                service.founder_update(id, motivation_id, name, email)
                return {}, 202
            except Exception as e:
                return str(e), 404
    
    @bp.route("/motivation/founders/<id>", methods=['GET'])
    def get_founder_by_motivation_id(id):
        if request.method=='GET':
            try:
                founders=service.get_founders_by_motivation_id(id)
                return [x.to_dict() for x in founders]
            except Exception as e:
                return str(e), 404 

    @bp.route("/commit", methods=['GET'])
    def commit_to_db():
        service.commit_to_db()
        return {}
    
    @bp.route("/chart_data", methods=['GET'])
    def get_chart_data():
        if request.method=='GET':
            entities=service.get_all()
            ans={}
            for entity in entities:
                if entity.strength not in ans.keys():
                    ans[entity.strength]=0
                ans[entity.strength]+=1
            return sorted(
                [ {'strength':strength, 'count':ans[strength]} for strength in ans.keys()], 
                key=lambda d : d['strength']
            )

    def emit_client_refresh():
        socketio.emit("refresh", "refreshhh")

    # @bp.route("/user", methods=['POST'])
    # def add_user():
    #     try:
    #         data_json=request.get_json()
    #     except Exception as e:
    #         pass
    #     return 404
    @bp.route("/user<id>", methods=['delete'])
    def remove_user(id):
        try:
            service.user_remove(int(id))
        except Exception as e:
            pass
        return 404
    