def customConf(path, dic):
    dic_copy = dic.copy()
    with open(path, "r+") as fr:
        lines = fr.readlines()
        for line in lines:
            for key in dic:
                if line.startswith(key):
                    del dic_copy[key]

    with open(path, "a+") as fw:
        fw.write("\n#==================================== doris custom config ====================================\n")
        for key in dic_copy:
            line = (key + "=" + dic_copy[key] + "\n")
            fw.write(line)
