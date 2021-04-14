import cv2
import numpy as np
import imutils
import os
import shutil
import requests



#khởi tạo kích thước của kí tự trên biển số
digit_w =30
digit_h =60

#Ba hàm này đưa về giá trị cho mỗi cột (x, y, ký tự) nhằm để vào hàm sort(key=) để sắp xếp
def takeSecond(elem):
    return elem[1]

def takeFirst(elem):
    return elem[0]

def takeChar(elem):
    return elem[2]

def Pretreatment(imgLP):

    #tiền xử lí ảnh
    #Đưa ảnh màu về ảnh xám
    grayImg = cv2.cvtColor(imgLP, cv2.COLOR_BGR2GRAY) 

    #Làm mịn và cân bằng sáng, nhưng vì thấy không hiệu quả lắm nên không dùng nữa
    #thường đối số sẽ là 9,75,75 hoặc 15,75,75. Để biết các đối số của bilateralFilter, có thể nghiên cứu tài liệu OpenCV
    noise_removal = cv2.bilateralFilter(grayImg,9,75,75)
    #Lấy ảnh khử nhiễu ở trên để cân bằng sáng
    equal_histogram = cv2.equalizeHist(noise_removal)

    #Phân ngưỡng ảnh xám
    ret, binImg = cv2.threshold(noise_removal, 100, 255, cv2.THRESH_BINARY_INV+ cv2.THRESH_OTSU)

    #Khử những chi tiết không mong muốn, đối số đầu tiên chỉ định hình mong muốn, đối số thứ hai chỉ định kích thước
    kerel3 = cv2.getStructuringElement(cv2.MORPH_RECT,(1,4))
    #từ kerel3 thu được ở trên, t làm nổi bật những chi tiết mong muốn
    binImg = cv2.morphologyEx(binImg,cv2.MORPH_DILATE,kerel3)
    
    return binImg

def contours_detect(binImg):
    #tìm contour
    #cnts, _ = cv2.findContours(binImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts, _ = cv2.findContours(binImg, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    #tạo ảnh tạm để giữ ảnh gốc k bị edit
    return cnts
def draw_rects_on_img(img, cnts):
    imgtemp=img.copy()
    cv2.drawContours(imgtemp,cnts,-1,(0,120,0),1)
    return imgtemp

    #cv2.imshow('Number on License plate ',imgtemp)
    # print (cnts);

#khởi tạo 
plate_number=''
coorarr=[]
firstrow=[]
lastrow=[]
model_svm =cv2.ml.SVM_load('D:\MyCode\python\demo\PTIT-VNeseLicensePlate\svm.xml')
plate_cascade = cv2.CascadeClassifier("D:\MyCode\python\demo\PTIT-VNeseLicensePlate\cascade2.xml")



def find_number(cnts,binImg,imgtemp,imgNomarl):
    count=0
    global plate_number
    global coorarr
    global firstrow
    global lastrow
    #duyệt từng cái contour
    # folder = './number/'
    # for filename in os.listdir(folder):
    #     file_path = os.path.join(folder, filename)
    #     try:
    #         if os.path.isfile(file_path) or os.path.islink(file_path):
    #             os.unlink(file_path)
    #         elif os.path.isdir(file_path):
    #             shutil.rmtree(file_path)
    #     except Exception as e:
    #         print('Failed to delete %s. Reason: %s' % (file_path, e))
    (himg,wimg,chanel)=imgtemp.shape
    if(wimg/himg >2):
        #Tính kích thước tương đối của số so với kích thước của biển số trong oto
        hf=himg*0.6 
        hl=himg*0.8
    else:
        #Tính kích thước tương đối của số so với kích thước của biển số trong xe máy
        hf=0.3*himg
        hl=0.4*himg
    plate_number = ''
    for c in (cnts):
        x,y,w,h=cv2.boundingRect(c)
        
        #Loại bỏ những c không chứa ký tự: Một ký tự phải có 1.5 < dài/rộng < 4
        if h/w >1.5 and h/w <4 and h>=hf or cv2.contourArea(c)>4500 and h<= hl: #cái này áp dụng cho cả biển xe máy xe hơi
        #if h/w >1.5 and h/w <4 and h>= hf and h<= hl:
            #print(cv2.contourArea(c))
            #2500 là kích thước tối thiểu của diện tích contour đảm bảo cho các contour "rác" không nhận diện
            #7000 là kích thước tối đa của contour số đảm bảo không nhận diện contour "rác" có cỡ lớn, chủ yếu đến từ viền biển số

            #Đóng khung cho kí tự
            cv2.rectangle(imgtemp, (x, y), (x + w, y + h), (0, 0, 255),2)
            #crop thành những số riêng lẻ
            crop=imgtemp[y:y+h, x:x+w]
            #dùng để ghi vào thư mục number
            count+=1
            cv2.imwrite('./number/number%d.jpg'% count,crop)
            #lưu vào mảng tọa độ để tí xài

            #tách số và predict
            #sao chép cái ảnh bin để khỏi hư cái kia :)) hơi dài nhưng an toàn
            binImgtemp=binImg
            #cắt ra từng số như cái crop ở trên nhưng t dùng biến khác để bây đỡ rối
            curr_num=binImgtemp[y:y+h, x:x+w]
            #xử lí để tí nữa đưa cái này vào hàm nó ràng buộc input phải kiểu dữ liệu như v
            #đầu tiên là resize lại cho nó cùng kích thước nhau cũng như= kích thước khi train
            curr_num=cv2.resize(curr_num,dsize=(digit_w,digit_h))
            _, curr_num=cv2.threshold(curr_num,30,255,cv2.THRESH_BINARY)
            #chuyển thành numpy để tí xài tạo thàn h mảng numpy
            curr_num= np.array(curr_num,dtype=np.float32)
            #chuyển ảnh 2D sang 1D để dùng SVM nhận diện số
            curr_num=curr_num.reshape(-1,digit_w*digit_h)

            #train
            #dùng file document  đã tạo ra từ train SVM 
            result=model_svm.predict(curr_num)[-1]
            result= int(result[0,0])

            if result<=9: 
                result= str(result)
            else:
                result=chr(result)
                
            #này dùng viết lên màn hình thui ae
            coorarr.append((x,y,result))
            cv2.putText(imgtemp,result,(x-50,y+50),cv2.FONT_HERSHEY_COMPLEX,3,(0, 255, 0), 2, cv2.LINE_AA)
    #sắp xếp theo y, nhằm lấy hàng đầu tiên với y thấp nhất
    coorarr.sort(key=takeSecond)
    #Lấy ra 4 giá trị đầu tiên có y thấp nhất, nhằm đưa về hàng đầu
    firstrow = coorarr[:4]
    #Sắp xếp lại hàng đầu từ trái qua phải
    firstrow.sort(key=takeFirst)
    #tương tự với hàng sau
    lastrow = coorarr[4:]
    lastrow.sort(key=takeFirst)


    #    Đưa từng hàng vào 
    for x, y, c in firstrow:
        plate_number+=c
    for x, y, c in lastrow:
        plate_number+=c
    # cv2.imshow("2", imgtemp)
    return imgtemp, plate_number

def sortNumber():
    global plate_number
    global coorarr
    #do t thêm dấu cách nên t cắt dấu cắt dư
    stringarr=plate_number.strip()
    #tạo thành 1 cái list trong python 
    stringarr=stringarr.split(" ")
    #sắp xếp lại các con số theo y
    for i in range(len(coorarr)):
        #so sánh tọa độ y
        for j in range(i+1,len(coorarr)):
            # nếu y của i > y của j 
            if coorarr[i][1]- coorarr[j][1] >15:
                temp=stringarr[i]
                stringarr[i]=stringarr[j]
                stringarr[j]=temp
                tempp=coorarr[i]
                coorarr[i]=coorarr[j]
                coorarr[j]=tempp
            elif coorarr[i][0]- coorarr[j][0] >0:
                temp=stringarr[i]
                stringarr[i]=stringarr[j]
                stringarr[j]=temp
                tempp=coorarr[i]
                coorarr[i]=coorarr[j]
                coorarr[j]=tempp
            
    #sau khi sắp xếp tao cho nó thành string lại nè
    plate_number=''.join(stringarr)
    return plate_number

def detect(img):
    (himg,wimg,chanel)=img.shape
    if(wimg/himg >2):
        img=cv2.resize(img,dsize=(1000,200))
    else:
        img=cv2.resize(img,dsize=(800,500))

    binImg=Pretreatment(img)
    cnts=contours_detect(binImg)
    # print("cnts: ",cnts)
    imgtemp=draw_rects_on_img(img,cnts)
    # cv2.imshow("123", imgtemp)
    
    imgtemp2, sort_number = find_number(cnts,binImg,imgtemp,img)
    # sort_number = sortNumber();
    print('bien so xe: ',sort_number)
    plate_number=''
    coorarr.clear()
    return sort_number

def findLP_img(OriImg): #find License plate
    # xóa thư mục (reset) "number" để lưu số đã cắt
    # shutil.rmtree('./number', ignore_errors=True)
    # tạo thư mục number
    # os.mkdir('number')

    #nhận diện biển trong img
    plates = plate_cascade.detectMultiScale(OriImg, 1.1, 3)
    #Tạo ảnh trước khi cắt
    img = OriImg
    #in vùng chứa biển số và cắt
    for (x,y,w,h) in plates:
        cv2.rectangle(OriImg,(x,y),(x+w,y+h),(255,0,0),1)
        img = OriImg[y:y+h, x:x+w]

        plate_num = detect(img)
        
        cv2.putText(OriImg, plate_num, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,0,0), 2)
    cv2.imshow("Original image", OriImg)
    # cv2.imshow("crop",img)
    return img

def video_webcam():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        print(ret)
        # print(frame)
        # frame = cv2.flip(frame, 1)
        img = findLP_img(frame)
        # cv2.imshow('img', frame)
        key = cv2.waitKey(1)
        if key == ord("q"):
            break

    cv2.destroyAllWindows()

def video_playback(source):
    cap = cv2.VideoCapture(source)
    while True:
        ret, frame = cap.read()
        frame = cv2.resize(frame,dsize=(1280 ,720))
        # print(ret)
        # print(frame)
        # frame = cv2.flip(frame, 1)
        img = findLP_img(frame)
        # cv2.imshow('img', frame)
        key = cv2.waitKey(1)
        if key == ord("q"):
            break

    cv2.destroyAllWindows()

def ipCam():
    while True:
        # Lấy từ ip nội bộ của camera, ở đây sử dụng phần mềm ip camera cho android nên việc kết nối khá đơn giản
        # nên chuyển độ phân giải về thấp để mượt hơn

        #Gọi ip, đưa kết quả từ web (là hình ảnh) về
        img_res = requests.get("http://192.168.12.101:8080/shot.jpg")
        # img_res = requests.get("http://192.168.7.105:8081/video")
        # img_res = requests.get("http://192.168.12.101:8080/video")
        img_arr = np.array(bytearray(img_res.content), dtype = np.uint8)

        img = cv2.imdecode(img_arr,-1) 

        img = findLP_img(img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

def pic(OriImg):
    #Tìm biển số
    img=findLP_img(OriImg)
    #resize lại hình
    (himg,wimg,chanel)=img.shape
    if(wimg/himg >2):
        img=cv2.resize(img,dsize=(1000,200))
    else:
        img=cv2.resize(img,dsize=(800,500))
    #cv2.imshow('Image',img)

    #img - Ảnh đã đc khoang vùng biển số và cắt ra
    # Xử lí ảnh img thành ảnh binary - ảnh trắng đen đưa vào binImg
    #binImg=Pretreatment(img);   

    #tìm viền cho các số trong binImg và lưu ds các vitri của viền vào cnts
    #cnts=contours_detect(binImg) 

    #imgtemp=draw_rects_on_img(img,cnts)# tiến hành tô viền cho img theo mảng cnts tìm đc
    # cv2.imshow('before_Sort',imgtemp)

    # tìm số và vẽ khung cho số 
    # trả về hình đã được tô viền, vẽ khung và tìm đc số vào imgtemp
    #trả về các số tìm được trên hình và các số này được 
    #       sắp xếp theo tọa độ trên-->dưới, trái--> phải lưu vào biến sort_number 
      
    #imgtemp, sort_number=find_number(cnts,binImg,imgtemp)
                                           
    # Xuất các hình và output số xe

    #cv2.imshow('binary',binImg)
    #cv2.imshow('result',imgtemp)
    #print('bien so xe: ',sort_number)

    #mở thư mục number để xe,
    # os.startfile('number')
    cv2.waitKey()
    cv2.destroyAllWindows()

if __name__ == "__main__":

    OriImg = cv2.imread(r'D:\MyCode\python\demo\PTIT-VNeseLicensePlate\Bike_back\48.jpg',1);
    #OriImg = cv2.imread('./img/xh1.jpg',1);
    # video_playback(r'D:\MyCode\python\demo\PTIT-VNeseLicensePlate\video\cv2.mp4')
    #
    # video_webcam()
    # ipCam()
    pic(OriImg)
    
