import re
import datetime
from string import Template


today = str(datetime.datetime.today().date())
report_file = './report-' + today + '.html'


regex = re.compile(
    r"""^(?P<timestamp>\d*-\d*-\d*\s\d*:\d*:\d*\.\d*)\| \w* \w*\W(?P<thread>\d*\s\w*)\W\| \w*\W(?P<IP>\d*\.\d*\.\d*\.\d*:\d*)\W\|\s+\w*\|(?P<master>\s*\d*\.\d*\.\d*\.\d*)\| (?P<user>\w*)\| \(\w* : \d+\)\s?\| \w*\|\s*(?P<connection>\w*\s?\w*\W*(?P<end>.*)$)""")


def read_file(given_file):
    with open(given_file) as file:
        for line in file.readlines():
            match = regex.search(line)
            if match:
                yield match.groups()


def how_many(groups, string):
    # 2018-11-06 16:54:36.533| on thread[140447603222272 c22s29]| IP[192.168.0.244:5000]| master| 192.168.0.244| sqream| (stmt : 29) | sqream|  Success
    res = []
    for i in groups:
        if string in i[-2]:
            res.append(i[-2])
    return res


def how_much(groups, string):
    res = 0
    for i in groups:
        if string in i:
            res += 1
    return res


def how_many_per_user(groups):
    res = []
    for i in groups:
        if "Success" in i[-2] or "Failed" in i[-2]:
            res.append({i[-3]: i[-2]})
    return res


def parse_slowest(groups):
    global end, start
    res = []
    for i in groups:
        if "Start Time" in i[-2]:
            start = datetime.datetime.strptime(i[-2].split()[4], "%H:%M:%S")
            continue
        elif "End Time" in i[-2]:
            end = datetime.datetime.strptime(i[-2].split()[4], "%H:%M:%S")
            if (end - start).total_seconds() > 0.0:
                res.append([i[-3], {"time": (end - start).total_seconds()}])
    return res


def who_slowest(*list_dict):
    return sorted(list_dict, key=lambda key: key[1]["time"])


def total_per_user(groups):
    dict_ = {"omer": 0, "sqream": 0, "Gilc": 0, "Guy": 0, "ben": 0}
    for i in groups:
        if i[-3] in dict_.keys():
            dict_[i[-3]] += 1
    return dict_



def calculate_users(users_all):
    omer = [sub['omer'] for sub in users_all if sub.get('omer')]
    sqream = [sub['sqream'] for sub in users_all if sub.get('sqream')]
    gilc = [sub['Gilc'] for sub in users_all if sub.get('Gilc')]
    guy = [sub['Guy'] for sub in users_all if sub.get('Guy')]
    ben = [sub['ben'] for sub in users_all if sub.get('ben')]
    omer_success = how_much(omer, "Success")
    omer_failed = how_much(omer, "Failed")
    sqream_success = how_much(sqream, "Success")
    sqream_failed = how_much(sqream, "Failed")
    gilc_success = how_much(gilc, "Success")
    gilc_failed = how_much(gilc, "Failed")
    guy_success = how_much(guy, "Success")
    guy_failed = how_much(guy, "Failed")
    ben_success = how_much(ben, "Success")
    ben_failed = how_much(ben, "Failed")

    return ["omer", omer_success, omer_failed], ["sqream", sqream_success, sqream_failed], \
           ["Gilc", gilc_success, gilc_failed], ["Guy", guy_success, guy_failed], ["ben", ben_success, ben_failed]


def render_template(*table_json):
    try:
        t = open('report.html', 'r+').read()
        template = Template(t)
        table_json = sorted(table_json, key=lambda item: item["success"], reverse=True)

        table_json = {"table_json": table_json}
        return template.safe_substitute(table_json)
    except Exception as e:
        print(f"Error occurred while rendering template: {e}")
        raise e


def save_report(result):
    try:
        open(report_file, 'w+').close()
        with open(report_file, "r+") as f:
            s = f.read()
            f.seek(0)
            f.write(result + s)
    except Exception as e:
        print(f"Error occurred while saving report: {e}")
        raise e


def prepare_report(total, users):
    list_dict_group, i = [], 0

    def append_to(dict_):
        list_dict_group.append(dict_)

    max_ = get_total([i for i in total.values()])
    users_dict = [{"user": i[0], "success": i[1], "failed": i[2]} for i in users]
    groups = read_file("./logfile.log")

    for group in groups:
        if group[-3] in users_dict[i].values():
            append_to({"success": users_dict[i]["success"], "failed": users_dict[i]["failed"], "timestamp": group[0],
                       "user": group[-3], "IP": group[2], "MASTER": group[3], "total": max_})
        elif group[-3] in users_dict[i + 1].values():
            append_to({"success": users_dict[i + 1]["success"], "failed": users_dict[i + 1]["failed"],
                       "timestamp": group[0], "user": group[-3], "IP": group[2], "MASTER": group[3], "total": max_})
        elif group[-3] in users_dict[i + 2].values():
            append_to({"success": users_dict[i + 2]["success"], "failed": users_dict[i + 2]["failed"],
                       "timestamp": group[0], "user": group[-3], "IP": group[2], "MASTER": group[3], "total": max_})
        elif group[-3] in users_dict[i + 3].values():
            append_to({"success": users_dict[i + 3]["success"], "failed": users_dict[i + 3]["failed"],
                       "timestamp": group[0], "user": group[-3], "IP": group[2], "MASTER": group[3], "total": max_})
        elif group[-3] in users_dict[i + 4].values():
            append_to({"success": users_dict[i + 4]["success"], "failed": users_dict[i + 4]["failed"],
                       "timestamp": group[0], "user": group[-3], "IP": group[2], "MASTER": group[3], "total": max_})

    return list_dict_group


def get_total(list_):
    try:
        total = 0
        for i in list_:
            total += i
        return total
    except Exception as e:
        print(f"Error occurred while calculating max value: {e}")


def main():
    print("1. How many successful statements were sent?")
    list_groups = [group for group in read_file("./logfile.log")]
    successes = len(how_many(list_groups, "Success"))
    print(f"Number of Successful statements: {successes}")
    print("====================================================================================")

    print("2. For each connection id - how many successful statements were sent?")
    connections = len(how_many(list_groups, "Connection"))
    print(f"Connection Number {connections}:  {successes} Successful statements")
    print("====================================================================================")

    print("3. How many failed/successful statements each user had sent to the server?")
    statements = how_many_per_user(list_groups)
    users = calculate_users(statements)
    for user in users:
        print(f"user {user[0]} sent {user[-2]} successful statements")
        print(f"user {user[0]} sent {user[-1]} Failed statements")
    print("====================================================================================")

    print("4. Which statement was the slowest successful statement?")
    slowest = parse_slowest(list_groups)
    slowest_ = who_slowest(*slowest)
    print(f"statement {slowest_} was the slowest")
    print("====================================================================================")

    print("5. How many statements in total were sent by each user?")
    total = total_per_user(list_groups)
    for k in total.keys():
        print(f"the user {k} had sent total of {total[k]} statements")
    print("====================================================================================")

    print("Additional work: Rendering Template HTML")
    list_dict_group = prepare_report(total, users)
    template = render_template(*list_dict_group)
    save_report(template)
    print("Report saved in current directory with current date in report name.")


if __name__ == "__main__":
    main()
