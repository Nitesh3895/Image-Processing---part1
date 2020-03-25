import hashlib
import sys
import pdb
import os
import cv2
import random
import glob
import shutil
from collections import Counter
import imagehash
from  PIL import Image

# assert len(sys.argv) >2 or len(sys.argv)==1, "Enter appropriate arguments Eg. python3 assignment.py option1"
# print(sys.argv)
def CreateData():
    DATA_FOLDER = os.path.join(os.getcwd(), "RAW_DATA")
    AUGUMENTED_DATA_FOLDER = os.path.join(os.getcwd(), "augmentedData")
    img_list = []
    print("Startng to add data by randomly resizing the images")
    for sub_folder in os.listdir(DATA_FOLDER):
        for index, image_name in enumerate(os.listdir(os.path.join(DATA_FOLDER, sub_folder))):
            src_image_path = os.path.join(DATA_FOLDER, sub_folder, image_name)
            des_image_path = os.path.join(AUGUMENTED_DATA_FOLDER, sub_folder, sub_folder + "_" + str(index) + ".png")
            resized_image_path = os.path.join(AUGUMENTED_DATA_FOLDER, sub_folder, sub_folder + "_resized" + str(index) + ".png")

            if not os.path.exists(os.path.join(AUGUMENTED_DATA_FOLDER, sub_folder)):
                os.makedirs(os.path.join(AUGUMENTED_DATA_FOLDER, sub_folder))  

            img_list.append(des_image_path)
            img_list.append(resized_image_path)

            src_img = cv2.imread(src_image_path)
            resized_img = cv2.resize(src_img, (random.randint(1366-150, 1366+150), random.randint(768-100, 768+100)))

            cv2.imwrite(resized_image_path, resized_img)
            cv2.imwrite(des_image_path, src_img)
    return img_list

def CreateDuplicateImages(img_list, duplicate_percent=0.1):
    print("Starting Duplicates Images addition to test the duplicate elimination flow")
    duplicateimg_list = random.sample(img_list, int(len(img_list)*duplicate_percent))
    
    duplicate_img_list = []
    for src_path in duplicateimg_list:
        duplicate_path = "/".join(src_path.split("/")[:-1])
        duplicate_img = "duplicate_" +src_path.split("/")[-1].split(".")[0] + "." + src_path.split("/")[-1].split(".")[1]
        duplicate_path = duplicate_path + "/" + duplicate_img
        duplicate_img_list.append(duplicate_path)
    #     print(src_path, duplicate_path)
        shutil.copy(src_path, duplicate_path)
    return duplicate_img_list

def getImageHash(img_path):
    with open(img_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def findDuplicate(entire_img_list):
    duplicatePredList = []
    imgHashDict = {}
    for index, i in enumerate(entire_img_list):
        imgHash = getImageHash(i)
        if imgHash not in imgHashDict: 
            imgHashDict[imgHash] = index
        else:
#             duplicatePredList.append((index,imgHashDict[imgHash]))
#             duplicatePredList.append([i, entire_img_list[imgHashDict[imgHash]]])
            if "duplicate" in i:
                duplicatePredList.append(i)
            else:
                duplicatePredList.append(entire_img_list[imgHashDict[imgHash]])
    return duplicatePredList, imgHashDict


def getSimilarity(img1, img2):
    kp_1, desc_1 = sift.detectAndCompute(img1, None)
    kp_2, desc_2 = sift.detectAndCompute(img2, None)

    matches = flann.knnMatch(desc_1, desc_2, k=2)
    good_points = []
    ratio = 0.6
    for m, n in matches:
        if m.distance < ratio * n.distance:
            good_points.append(m)
    print(len(good_points), len(kp_1), len(kp_2))
    percent_similarity = len(good_points) / min(len(kp_1), len(kp_2)) * 100
    return percent_similarity

def multipop(yourlist, itemstopop):
    result = []
    itemstopop.sort()
    itemstopop = itemstopop[::-1]
    for x in itemstopop:
        result.append(yourlist.pop(x))
    return result


def getCategoryMatches(sorted_entire_img_list):
    sample_img_path = random.sample(sorted_entire_img_list, 1)[0]
    hash2 = imagehash.dhash(Image.open(sample_img_path))
    for i in range(len(sorted_entire_img_list)):
        img_path1 = sorted_entire_img_list[i]
        hash1 = imagehash.dhash(Image.open(img_path1))
        if (hash1 - hash2) <= 12:
            index_list.append(i)
    return index_list


def createVideo(img_list, filename="sample.avi", img_size=(640, 480)):
#     height, width, channels = cv2.imread(img_list[0]).shape
    video = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'DIVX'), 15, img_size)
    for i in sorted(img_list, key=lambda x: os.path.getmtime(x)):
        img = cv2.imread(i)
        img = cv2.resize(img, img_size)
        video.write(img)

    cv2.destroyAllWindows()
    video.release()
def getComparison(img_path1, img_path2):
    hash1 = imagehash.dhash(Image.open(img_path1))
    hash2 = imagehash.dhash(Image.open(img_path2))
    return (hash1 - hash2)

def getTotalComparison(img_path, mainCategoryList):
    count = []
    for db_img_path in mainCategoryList:
        hashDiff = getComparison(img_path, db_img_path)
        print("Image hash Calc for ", img_path.split("/")[-1], db_img_path.split("/")[-1], hashDiff)
        if hashDiff <=8:
            count.append(True)
    print("Count in getTotalComparison", count.count(True))
    return count.count(True)
def assignCategory(category, rawCategoriesList, testCategory):
    print(testCategory, rawCategoriesList)
    poll = [0, 0, 0, 0, 0]
    list = random.sample(category[testCategory], int(len(category[testCategory]) * .25))
    if len(list) == 0:
        list = category[testCategory]
    for img_path in list:
        count = []
        for i in range(0,5):
            count.append(getTotalComparison(img_path, category[rawCategoriesList[i]]))
        poll[count.index(max(count))] += 1
    return count.index(max(count))
if __name__ == "__main__":
    assert len(sys.argv)==2, "Enter appropriate arguments Eg. python3 assignment.py option1"
    if os.path.exists(os.path.join(os.getcwd(), "augmentedData")):
        shutil.rmtree(os.path.join(os.getcwd(), "augmentedData"))
    #PrepareDate
    print("Creating Data of the variouos screenshots taken")
    img_list = CreateData()
    duplicate_img_list = CreateDuplicateImages(img_list)
    entire_img_list = glob.glob(os.path.join(os.getcwd(), "augmentedData/*/*.png"))
    if sys.argv[-1] == "option1":
        #Find the duplicates which were added by CreateDuplicateImages function and assert the duplicatePredList and duplicate_img_list
        print("Finding the duplicates that were added manually")
        duplicatePredList, imgHashDict = findDuplicate(entire_img_list)
        assert sorted(duplicatePredList) == sorted(duplicate_img_list), "Duplicate Identification failure Please check"
        print("Duplicates successfully detected")
        result = list((Counter(entire_img_list) - Counter(duplicatePredList)).elements())
        createVideo(result, filename='videoWithoutDuplicate.avi')
    elif sys.argv[-1] == "option2":
        # sift = cv2.xfeatures2d.SIFT_create()
        # index_params = dict(algorithm=0, trees=5)
        # search_params = dict()
        # flann = cv2.FlannBasedMatcher(index_params, search_params)

        OUTPUT_PATH = ""

        category = {}
        categoryIndex = 0
        sorted_entire_img_list = entire_img_list
        import time

        print("Segregating the Images to different Categories via image hash")
        while len(sorted_entire_img_list) != 0:
            # print(len(sorted_entire_img_list))
            categoryIndex += 1
            index_list = []

            s_time = time.time()
            index_list = getCategoryMatches(sorted_entire_img_list)
            e_time = time.time()
            elementList = multipop(list(sorted_entire_img_list), index_list)
            category[categoryIndex] = elementList
            sorted_entire_img_list = list((Counter(sorted_entire_img_list) - Counter(elementList)).elements())
            E_time = time.time()
            # print(e_time-s_time, E_time-e_time)
        rawCategoriesList = sorted(category, key=lambda key: len(category[key]), reverse=True)

        print("Different Categories created. ")
        print("Starting Video Creation")


        for i in category:
            if len(category[i]) <=4:
                continue
            if not os.path.exists(os.path.join(os.getcwd(), "videos", "category_"+str(i))):
                os.makedirs(os.path.join(os.getcwd(), "videos", "category_"+str(i)))
            createVideo(category[i], filename=os.path.join(os.getcwd(), "videos", "category_"+str(i), "category_"+str(i)+".avi"))
            for img_path in category[i]:
                src = img_path
                img_name = img_path.split("/")[-1]
                des = os.path.join(os.getcwd(), "videos", "category_"+str(i), img_name)
                shutil.copy(src, des)
        print("Videos successfully created for the grouped categories")


        #This snippet enhances the categories but takes a quite amount of amount. Subject to optimisation
        # for testCategory in rawCategoriesList[5:]:
        #     predCategory = assignCategory(category, rawCategoriesList, testCategory)
        #     category[rawCategoriesList[predCategory]].extend(category[testCategory])
        # rawCategoriesList = sorted(category, key=lambda key: len(category[key]), reverse=True)
        # print([category[i] for i in rawCategoriesList])
        # pdb.set_trace()

        #     test.append([img_path, hash1-hash2])


        # createVideo(result, filename='videoWithoutDuplicate.avi')



