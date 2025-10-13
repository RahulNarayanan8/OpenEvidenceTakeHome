from classify import identify_keywords, get_highest_paying_ad


key1 = {
    "What are some common symptoms of breast cancer?": ["Breast Cancer"],
    "What are some demographics that are at higher risk for hypertension and lung cancer?": ["Lung Cancer", "Hypertension"],
    "What day is it?": []
}

key2 = {
    "What are some common symptoms of melanoma and breast cancer?": {
                "category": "Breast Cancer",
                "ad_path": "ad_images/genentech_breast_cancer.png",
                "company": "genentech",
                "cost": 70,
                "link": "https://www.gene.com/patients/medicines/herceptin"
            },
    "What are demographics with high incidences of obesity and pancreatic cancer?":{
        "category": "Obesity",
        "ad_path": "ad_images/lilly_obesity.png",
        "company": "eli lilly",
        "cost": 60,
        "link": "https://www.lilly.com/lillydirect/medicines/zepbound"
    }
}



def identify_keywords_test_1():
    return identify_keywords(list(key1.keys())[0]) == sorted(key1[list(key1.keys())[0]])
def identify_keywords_test_2():
    return identify_keywords(list(key1.keys())[1]) == sorted(key1[list(key1.keys())[1]])
def identify_keywords_test_3():
    return identify_keywords(list(key1.keys())[2]) == sorted(key1[list(key1.keys())[2]])

def get_highest_paying_ad_test_1():
    return get_highest_paying_ad(list(key2.keys())[0]) == key2[list(key2.keys())[0]]
def get_highest_paying_ad_test_2():
    return get_highest_paying_ad(list(key2.keys())[1]) == key2[list(key2.keys())[1]]


def main():
    if identify_keywords_test_1():
        print("Test 1 Passed")
    if identify_keywords_test_2():
        print("Test 2 Passed")
    if identify_keywords_test_3():
        print("Test 3 Passed")

    if get_highest_paying_ad_test_1():
        print("Test 4 Passed")
    if get_highest_paying_ad_test_2():
        print("Test 5 Passed")
    


if __name__ == "__main__":
    main()