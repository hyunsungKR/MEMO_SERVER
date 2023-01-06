from flask import request
from flask_restful import Resource

from mysql_connection import get_connection
from mysql.connector import Error
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

class MemoListResource(Resource) : 
    

    # API를 처리하는 함수 개발
    # HTTP Method를 보고! 똑같이 만들어준다.

    # jwt 토큰이 필수라는 뜻! : 토큰이 없으면 이 API는 실행이 안 된다.
    @jwt_required()
    def post(self) :




        # 1. 클라이언트가 보내준 데이터가 있으면
        #    그 데이터를 받아준다.
        data = request.get_json()

        # 1-1 헤더에JWT 토큰이 있으면 토큰 정보를 받아준다
        user_id = get_jwt_identity()



        # 2. 이 레시피정보를 DB에 저장해야한다.
        
        try :
            ### 1. DB에 연결
            connection = get_connection()

            ### 2. 쿼리문 만들기
            query = '''insert into memo
                    (userId,title,date,content)
                    values
                    (%s,%s,%s,%s);'''
            ### 3. 쿼리에 매칭되는 변수 처리 해준다. 튜플로!
            record = ( user_id,data['title'],data['date'],data['content'] )

            ### 4. 커서를 가져온다.
            cursor=connection.cursor()

            ### 5. 쿼리문을 커서로 실행한다.
            cursor.execute(query, record)

            ### 6. 커밋을 해줘야 DB에 완전히 반영된다.
            connection.commit()

            ### 7. 자원 해제
            cursor.close()
            connection.close()

        except Error as e :

            print(e)
            cursor.close()
            connection.close()

            return{"result" : "fail", "error" : str(e)} , 500



        # API를 끝낼때는
        # 클라이언트에 보내줄 정보(json)와 http 상태 코드를
        # 리턴한다.
        return {"result" : "success"} , 200

    def get(self) :
        # 1. 클라이언트로부터 데이터를 받아온다.
        # 없다.

        # 클라이언트에서 쿼리스트링으로 보내는 데이터는
        # request.args에 들어있다.

        offset = request.args.get('offset')
        limit=request.args.get('limit')



        # 2. db에 저장된 데이터를 가져온다.
        try :
            connection = get_connection()

            query = '''select *
                        from memo
                        order by date desc
                        limit '''+ offset +''','''+ limit +''';'''

            ## 중요!!!! select 문은 
            ## 커서를 가져올 때 dictionary = True로 해준다
            cursor = connection.cursor(dictionary=True)

            cursor.execute(query)

            result_list=cursor.fetchall()

            print(result_list)
            
            # 중요 ! db에서 가져온 timestamp는
            # 파이썬에서 datetime으로 자동 변환된다.
            # 그런데 문제는 !!! 우리는 json으로
            # 클라이언트한테 데이터를 보내줘야 하는데
            # datetime은 json으로 보낼 수 없다.
            # 따라서 시간을 문자열로 변환해서 보내준다.
            i = 0
            for row in result_list :
                result_list[i]['createdAt']=row['createdAt'].isoformat()
                result_list[i]['updatedAt']=row['updatedAt'].isoformat()
                result_list[i]['date']=row['date'].isoformat()
                i = i+1




            cursor.close()
            connection.close()
        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return{"result":"fail","error":str(e)}, 500
        
        return {"result" : 'seccess','items':result_list,'count':len(result_list)}, 200


class MemoResource(Resource) :
    @jwt_required()
    def put(self, memo_id) : 

        data = request.get_json()

        user_id = get_jwt_identity()

        try : 
            connection = get_connection()
            query = '''update memo
                    set
                    title = %s,
                    date = %s,
                    content = %s
                    where id = %s and userId = %s;'''
            
            record = (data['title'],data['date'],data['content'],memo_id,user_id)

            cursor = connection.cursor()

            cursor.execute(query, record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {'result' : 'fail', 'error' : str(e)}, 500

        return {'result' : 'success' }, 200

    @jwt_required()
    def delete(self,memo_id) :

        user_id=get_jwt_identity()

        try :
            connection = get_connection()
            query = '''delete from memo
                    where id = %s and userId = %s;'''
            record = (memo_id,user_id)

            cursor = connection.cursor()

            cursor.execute(query,record)

            connection.commit()

            cursor.close()
            connection.close()
        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return{'result':'fail','error':str(e)}, 500

        return {'result':'success'},200    




class FollowMemoListResource(Resource) :
    @jwt_required()
    def get(self) :

        offset=request.args.get('offset')
        limit=request.args.get('limit')

        user_id=get_jwt_identity()
        
        try :
            connection = get_connection()
            query = '''select u.nickname,m.title,m.date,m.content,m.createdAt,f.followeeId,m.id as memoId
                    from follow f
                    join user u
                    on f.followerId=u.id
                    join memo m
                    on m.userId = f.followeeId
                    where f.followerId = %s
                    order by m.date desc
                    limit '''+ offset +''', '''+ limit +''' ;'''
            record = (user_id,)
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query,record)
            result_list=cursor.fetchall()

            i = 0
            for row in result_list :
                result_list[i]['createdAt']=row['createdAt'].isoformat()
                result_list[i]['date']=row['date'].isoformat()
                i = i+1
            cursor.close()
            connection.close()
        
        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return{'error':str(e)},500



        return{'result':'success','items':result_list,'count':len(result_list)},200