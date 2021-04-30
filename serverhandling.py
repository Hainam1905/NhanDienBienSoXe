from firebase import firebase
import keyboard

def getBikeListkey(firebase):
    bikelistkey=firebase.get('/bikelist/','')
    bikelistkey=str(bikelistkey)
    bikelistkey=bikelistkey.split('\'')
    bikelistkey=bikelistkey[1]
    return bikelistkey

def getScanBike(firebase):
    scanbike= firebase.get('/bike/','')
    scanbike=str(scanbike)
    scanbike=scanbike.split('\'')
    scanbike=scanbike[3]
    return scanbike

def getScanBikeKey(firebase):
    scanbikekey= firebase.get('/bike/','')
    scanbikekey=str(scanbikekey)
    scanbikekey=scanbikekey.split('\'')
    scanbikekey=scanbikekey[1]
    return scanbikekey

def getBikeList(firebase):
    bikelist= firebase.get('/bikelist/','')
    bikelist=str(bikelist)
    bikelist=bikelist.split('[')
    bikelist=bikelist[1].split(']')
    bikelist=bikelist[0]
    bikelist=bikelist.replace('\'',"")
    bikelist=bikelist.replace(' ',"")
    bikelist=list(bikelist.split(","))
    return bikelist

def getBooleankey(firebase):
    booleankey= firebase.get('/boolean/','')
    booleankey=str(booleankey)
    booleankey=booleankey.split('\'')
    booleankey=booleankey[1]
    return booleankey


# b = "Hello, World!"
# print(b[:len(b)-1])
def checkexistbike(scanbike,bikelist):
    for index in range(len(bikelist)):
        scanbiketmp=scanbike[:len(scanbike)-1]
        itemtmp=bikelist[index][:len(bikelist[index])-1]
        if scanbiketmp == itemtmp:
            return True
    return False



def Handling(firebase,scanbike,bikelist,scanbikekey,booleankey):
    while True:
        if keyboard.is_pressed('q'):
            print("Closing sever")
            break
        # print("sever is listening")
        scanbike=getScanBike(firebase)
        if scanbike !="": 
            bikelist=getBikeList(firebase)
            isexist=False
            for index in range(len(bikelist)):
                scanbiketmp=scanbike[:len(scanbike)-1]
                itemtmp=bikelist[index][:len(bikelist[index])-1]
                if scanbiketmp == itemtmp:
                    print("Yes, Xe da co trong he thong")
                    isexist=True
                    # scanbikekey= scanbike[len(scanbike)-1:len(scanbike)]
                    # itemkey= bikelist[index][len(bikelist[index])-1:len(bikelist[index])]

                    scanbikekey= scanbike.split('-')
                    scanbikekey= scanbikekey[1]
                    itemkey= bikelist[index].split('-')
                    itemkey= itemkey[1]


                    if scanbikekey==itemkey:
                        print("Key đúng")
                        firebase.put('/boolean/',booleankey,"1")
                        bikelist.remove(scanbike)
                        firebase.put('/bike/',getScanBikeKey(firebase),"")
                        firebase.put('/bikelist/',getBikeListkey(firebase),bikelist)
                    else :
                        print("key sai")
                        firebase.put('/boolean/',booleankey,"0")
                        firebase.put('/bike/',getScanBikeKey(firebase),"")
                    break
            if isexist== False:
                print("xe chua co trong he thong")
                firebase.put('boolean',booleankey,"2")
                bikelist.append(scanbike)
                firebase.put('/bike/',getScanBikeKey(firebase),"")
                firebase.put('/bikelist/',getBikeListkey(firebase),bikelist)



            # if checkexistbike(scanbike,bikelist):
            #     print("Yes, Xe da co trong he thong")
            #     print("Tien hanh kiem tra !")



                # vese=input("nhập số vé xe để kiểm tra: ")
                # if (int)(vese) == bikelist.index(scanbike) :
                #     print("Số vé đúng bạn có thể lấy xe")
                #     bikelist.remove(scanbike)
                #     print(bikelist)
                #     firebase.put('/bikelist/',getBikeListkey(firebase),bikelist) 
                # else:
                #     print("Số vé nhập sai bạn không thể lấy xe")
                # firebase.put('/bike/',getScanBikeKey(firebase),"")
            # else:
            #     print("Xe chua co trong he thong")
                # firebase.put('boolean',booleankey,"2")
                # bikelist.append(scanbike)
                # firebase.put('/bike/',getScanBikeKey(firebase),"")
                # firebase.put('/bikelist/',getBikeListkey(firebase),bikelist)


   
# print(bikelistrs)
# firebase.put('/bikelist/',bikelistkey,bikelistrs) 


if __name__ == "__main__":
    print("Sever opened")
    firebase = firebase.FirebaseApplication('https://htpt-ae43c.firebaseio.com/', None)
    bikelist=getBikeList(firebase)
    scanbike=getScanBike(firebase)
    scanbikekey=getScanBikeKey(firebase)
    booleankey=getBooleankey(firebase)
    Handling(firebase,scanbike,bikelist,scanbikekey,booleankey)

    # firebase.put('/bikelist/',getBikeListkey(firebase),["bienso1","bienso2"]) 



    # print(getBooleankey(firebase))