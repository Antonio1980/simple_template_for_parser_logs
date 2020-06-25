import json


def read_json_config(json_file):
    with open(json_file) as f:
        json_dict = json.load(f)
    return json_dict


def calculate_items(json_dict):
    return [(key, len(json_dict[key].keys())) for key in json_dict.keys()]


def sort_true(json_dict):
    for j in json_dict.keys():
        for k in json_dict[j].keys():
            if json_dict[j][k] is True:
                print(k)


def main():
    print("1. How many items are under each key out of the 4 keys listed above.")
    json_dict = read_json_config("./config.json")
    t_list = calculate_items(json_dict)
    for i in t_list:
        print(i[0] + " : " + str(i[1]))

    print("========================================================")

    print("2. For each key, print the items whose values are “true”")
    sort_true(json_dict)

    print("========================================================")


if __name__ == "__main__":
    main()