#### author: Shengbo Ge
#### email: gesboge@gmail.com
#### Distribute under MIT License
#### #code: utf-8
#########

import requests
from PIL import Image
import base64
from io import BytesIO
import warnings
import urllib
import sys

def printer(resp):
    print('------------------------printing resp with request '+resp.url)
    print(resp.headers)
    print(resp.status_code)
    print(resp.text)
    print()

class teacher():
    def __init__(self, name, ID):
        self.name = name
        self.id = ID


def login():
    loginInfo = {'mobile':loginMobile, 'password': loginPassword, 'imageCode': loginImageCode, 'key':loginKey}
    resp = mySession.post(httpsURL+'/rest/parentrest/api/parent/login',headers=headers,data=loginInfo,verify=False)
    print('Logging...\n')
    if resp.status_code == 200:
        pass
    elif resp.status_code == 400:
        if resp.json()['msg'] == 'INVALID_INPUT:EXCEED_LOGIN_FAIL_NUM':
            params = {'_':'1477729194641'}
            headers['Content-Type'] = None
            headers['Content-Length'] = None
            resp = mySession.get(httpsURL+'/rest/parentrest/api/verifycode/image',headers=headers,params=params,verify=False)
            im = Image.open(BytesIO(base64.b64decode(resp.json()['data']['imageCode'].split(',')[1])))
            im.show(im)
            loginInfo['imageCode'] = input('please input the verify code:\n')
            loginInfo['key'] = resp.json()['data']['key']
            resp = mySession.post(httpsURL+'/rest/parentrest/api/parent/login',headers=headers,data=loginInfo,verify=False)
            if resp.json()['msg'] == 'OK':
                pass
            if resp.json()['msg'] == 'INVALID_INPUT:LOGIN_FAIL':
                print('ERROR: Incorrect mobile number or password. Please check and rerun this script',file=sys.stderr)
                exit()
            else:
                print('ERROR: unsupported login response\n', file=sys.stderr)
                exit()
    else:
        print('ERROR: unspported login response\n', file=sys.stderr)
        exit()
    respjson = resp.json()['data']
    cookies['familyId'] = str(respjson['familyId'])
    cookies['parentId'] = str(respjson['id'])
    cookies['studentId'] = str(respjson['studentIds'][0])
    cookies['userId'] = str(respjson['studentIds'][0])
    cookies['userToken'] = str(respjson['token'])
    cookies['Authorization'] = '\"'+str(resp.headers['authorization'])+'\"'
    cookies['userName'] = '%E9%BB%84%E7%9D%BF%E7%A5%BA'
    resp = mySession.get(httpURL+'/parent/home',headers=headers,cookies=cookies,verify=False)
    if resp.status_code == 200:
        print('login successful')

def getTimeScheduleByTeacher(teacher):
    scheduleRequest = { 'mode' :'1', 
        'seaType':'3',
        'teacherId': teacher.id,
        'week':'2',
        'day':'日期不限',
        'timeStart':'起始时间',
        'timeEnd':'截止时间',
        'courseType':'MAJOR',
        'currNum':'1',
        'isPageDo':'-1',
        'idx':'2'
        }
    headers['Content-Type']='application/x-www-form-urlencoded; charset=UTF-8'
    resp = mySession.post(httpURL+'/parent/preschedule/gettimeslot',headers=headers,cookies=cookies,data=urllib.parse.urlencode(scheduleRequest),verify=False)
    return resp.json()['data']

######################### start registering
def registerClass():
    print('start registering\n')
    for weekDay in recommandedDay:
        isClassBooked = False
        print('----------------registering class on Weekday: ' + str(weekDay))
        for teacher in recommandedTeacher:
            print('start looking at teacher: ' + teacher.name)
            timeSlots = getTimeScheduleByTeacher(teacher)
            for time in recommandedTime:
                print('start looking at Time: ' + time)
                if 'status' in timeSlots[timeSchedule[time]][weekDay]:
                    if timeSlots[timeSchedule[time]][weekDay]['status'] == 'AVAILABLE':
                        bookRequest ={ 'onlineClassId' : timeSlots[timeSchedule[time]][weekDay]['id'],
                                      'oldOnlineClassId' : timeSlots[timeSchedule[time]][weekDay]['oid'],
                                      'courseType' : 'MAJOR'
                                      }
                        resp = mySession.post(httpURL+'/parent/book',headers=headers,cookies=cookies,data=urllib.parse.urlencode(bookRequest),verify=False)
                        if resp.status_code == 200:
                            print('SUCCESS: schedule on weekday '+str(weekDay)+' Time ' + time + ' booked\n')
                            isClassBooked = True
                            break
                        else:
                            print('ERROR: schedule on weekday '+str(weekDay)+' Time ' + time + 'is available but can not be booked', file=sys.stderr)
                    else:
                        print('FAIL: schedule on weekday '+str(weekDay)+' Time ' + time + ' is already booked by someone\n')
                else:
                    print('FAIL: schedule on weekday '+str(weekDay)+' Time ' + time + ' is not available for this teacher\n')
            if isClassBooked:
                break
        if isClassBooked:  
            print('----------------your class on Weekday ' + str(weekDay) +' is booked at ' + time + '. Teacher: '+ teacher.name)    
        else:
            print('----------------your class on Weekday ' + str(weekDay) +' failed to book.', file=sys.stderr)
###################### register complete

if __name__ =='__main__':
    warnings.filterwarnings("ignore")
    
    
    # DATA
    ##########################################################
    loginMobile = ''    # modify this
    loginPassword = ''  # modify this
    loginImageCode = '' # do not modify this
    loginKey = ''       # do not modify this
    
    if not loginMobile or not loginPassword:
        print('You must modify your mobile number and password before log in!', file=sys.stderr)
        exit()
    
    # SCHEDULE: ORDER MATTERS    # modify these
    recommandedDay = []      # 1 for Monday, 2 for Tuesday, .... , 7 for Sunday e.g. [5, 6] means register class on Friday and Saturday
    recommandedTeacher = [teacher('laura Stanley','1579411'), teacher('Cherry R','1494191'), teacher('Kaitlyn M K','1516031')]  # sample teachers and their id. You can add yours
    recommandedTime = []    # time in 24-hour-clock. only valid class time is supported. e.g. ['19:00', '19:30', '20:00'] means register class on 19:00, 19:30 or 20:00, and 19:00 is preferred than others
    
    if not recommandedDay or not recommandedTime:
        print('You must modify your recommanded class day and time and before log in!', file=sys.stderr)
        exit()
    
    ##########################################################
    
    timeSchedule = {'9:00':0,'9:30':1, '10:00':2, '10:30':3, '11:00':4, '11:30':5, '12:00':6, '12:30':7, '13:00':8, '13:30':9, '14:00':10, '14:30':11, '15:00':12, '15:30':13, '16:00':14, '16:30':15, '17:00':16, '17:30':17, '18:00':18, '18:30':19, '19:00':20, '19:30':21, '20:00':22, '20:30':23, '21:00': 24, '21:30':25}
    httpURL = 'http://www.vipkid.com.cn'
    httpsURL = 'https://www.vipkid.com.cn'
    headers = {
        'Host': 'www.vipkid.com.cn',
        'Accept': '*/*',
        'Origin': 'https://www.vipkid.com.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.8,zh;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        'DNT':'1'
    }
    cookies = {}
    mySession = requests.Session()
    
    login()
    registerClass()