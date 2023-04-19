


def SaveTxt(dict):

    with open('result.txt', "r+") as f:
        old = f.read()
        f.seek(0)
        f.write("START")
        f.write('\r')
        f.write(old)

    for item in dict.items():
        name = item[0]
        num = item[1]
        with open(r'result.txt', 'a') as f:
            f.write("Goal_ID="+str(name)+";"+"Num="+str(num))
            f.write('\r')

    with open('result.txt', "a+") as f:
        f.write("END")


if __name__ == '__main__':
    res = {'Unknown': 6, 'CD002': 3, 'CC002': 3, 'CC001': 3, 'CB002': 1}
    SaveTxt(res)