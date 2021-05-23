from firebase import firebase
import json
firebase = firebase.FirebaseApplication('https://htpt-ae43c.firebaseio.com/', None)
firebasers=firebase.get('/bike/','')
firebasers=str(firebasers)
firebasers=firebasers.split('\'')
firebasers=firebasers[1]

# number=0
# while True:
#     firebase.put('/bike/',rs,number)
#     number=number+1   


# def putnewbike(date,numplate):
#     data= {date,}

# arr.append("new") 
# arr=['51L14625','51L14626','51L14627','51L14628','51L14629']
# arr.append("new")
# data =  { '17_10_2020': arr}
# firebase.post('/bike/','bienso6')    


# firebase.put('/bike/'+rs+'/','17_10_2020',[0,0,0,0])
# result = firebase.get('/bike/', '')
# print(rs)

