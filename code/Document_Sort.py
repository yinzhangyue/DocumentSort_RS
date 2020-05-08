from scipy import stats
import time
import datetime
from datetime import datetime
# Author:印张悦 ECNU 10174503110
# 注意事项：
# history和schedule假定读入时就已经框定一个月的范围！！！
# 如果store不为空则默认已经计算得到了之前一个月的结果，且history仅包含当天文档的打开记录！！！
# 需要实现Relation匹配函数
# sigma的值可根据需求设定


# 设置基准时间（合理的基准时间可大大减少算力）
# Input:Null
# Output:基准时间戳 type:timeStamp
def Standard():
    # 以2020年5月1日00:00为基准
    timeArray = time.strptime('2020-5-1 00:00:00', "%Y-%m-%d %H:%M:%S")
    timeStamp = int(time.mktime(timeArray))
    # print(timeStamp)
    return timeStamp


# 计算方差
# Input:day7从今天起前7天的历史记录、day14从今天七前7到14天的历史记录 type:二维list
# Output:sigma type:float
def Sigma(day7, day14):
    length = len(day7) + len(day14)
    sigma = 9  # 该值可根据实际情况设定
    if length > 14 * 50:
        sigma -= length / 50
    if sigma < 0:
        sigma = 0
    return sigma


# 判断是否具有周期性
# Input:week1上周的历史记录、week2上上周的历史记录（注意与day7和day14的不同） type:二维list
# Output:0（无周期性） 7（以周为单位的周期性） 5（以工作日为单位的周期性） type:int
def Periodicity(week1, week2):
    w1 = [[], [], [], [], [], [], []]
    length1 = len(week1)
    for i in range(length1):
        ltime = time.localtime(week1[i][1])
        dateymd = time.strftime("%Y-%m-%d", ltime)
        w1[datetime.strptime(dateymd, "%Y-%m-%d").weekday()
           ].append(week1[i][0])

    w2 = [[], [], [], [], [], [], []]
    length2 = len(week2)
    for i in range(length2):
        ltime = time.localtime(week2[i][1])
        dateymd = time.strftime("%Y-%m-%d", ltime)
        w2[datetime.strptime(dateymd, "%Y-%m-%d").weekday()
           ].append(week2[i][0])

    # 以周为单位的周期性
    J1 = 0
    for i in range(7):
        if len(set(w1[i]) | set(w2[i])) != 0:
            # Jaccard相似度
            J1 += len(set(w1[i]) & set(w2[i])) / len(set(w1[i]) | set(w2[i]))
    J1 /= 7

    # 以工作日为单位的周期性
    J2 = 0
    for i in range(5):
        if len(set(w1[i]) | set(w2[i])) != 0:
            # Jaccard相似度
            J2 += len(set(w1[i]) & set(w2[i])) / len(set(w1[i]) | set(w2[i]))
    J2 /= 5

    if J1 > 0.5:
        return 7
    elif J2 > 0.5:
        return 5
    else:
        return 0


# 通过关键字匹配等方式将日程关联到文档，这个函数请根据实际情况实现，这只是根据案例情况写的
# Input:日程 type:str
# Output:日程匹配的文档 type:list
def Relation(schedule):
    if schedule == "高数考试":
        return ["高等数学"]
    elif schedule == "线代考试":
        return ["线性代数"]
    else:
        return []


# 排序算法的核心实现
# Input:history 一个月内文档的打开记录，假定读入时就已经框定一个月的范围！！！ type:[['文档','时间戳']]
#       schedule 未来一个月内的日程，假定读入时就已经框定一个月的范围！！！ type:[['日程','时间戳']]
#       sigma 计算得到的方差 type:float
#       periodicity 计算得到是否具有周期性 type:int
#       store 预存的计算结果，如果其不为空则默认已经计算得到了之前一个月的结果，且history仅包含当天文档的打开记录！！！ type:[['文档','概率']]
#       now 指定排序的时刻，默认为当前时刻 type:int
# Output:文档的先后顺序 type:[('文档',概率值)]
def Document_Sort(history, schedule, sigma=9, periodicity=0, store=[], now=int(time.time())):
    standard = Standard()
    # print(sigma)
    # 使用字典存储结果
    arr = {}

    # 判断之前是否有预存计算结果
    if store != []:
        length_store = len(store)
        for i in range(length_store):
            # 文章中我们提到如果存入数据库时就*0.9可以进一步减少算力，这里我们假定之前没有这么做，直接存入的计算结果
            arr[store[i][0]] = store[i][1] * 0.9

    # 历史打开记录
    length_history = len(history)
    for i in range(length_history):
        # prob = stats.norm.pdf(x, mu, sigma)
        prob = stats.norm.pdf((now - standard)/(24*60*60),
                              (history[i][1] - standard)/(24*60*60), sigma)
        if history[i][0] in arr.keys():
            arr[history[i][0]] += prob
        else:
            arr[history[i][0]] = prob

    # 未来日程
    length_schedule = len(schedule)
    for i in range(length_schedule):
            # prob = stats.norm.pdf(x, mu, sigma)
        prob = stats.norm.pdf((now - standard)/(24*60*60),
                              (schedule[i][1] - standard)/(24*60*60), sigma)
        for j in Relation(schedule[i][0]):
            if j in arr.keys():
                arr[j] += prob
            else:
                arr[j] = prob
    # print(sorted(arr.items(), key=lambda x: x[1], reverse=True))
    return sorted(arr.items(), key=lambda x: x[1], reverse=True)


# 就是调用一下Document_Sort()定期计算一下结果，可按需要进行转换后存入数据库
def Store(history, schedule, sigma=9, periodicity=0, now=int(time.time())):
    return Document_Sort(history, schedule, sigma, periodicity, now=now)


if __name__ == "__main__":
    '''
    示例数据如下：
    当前时间2020年5月19日8:00 1589846400
    日程：
    1. 2020年5月19日10:00 1589853600 高数考试
    2. 2020年5月20日13:00 1589950800 线代考试
    打开历史记录：
    1. 2020年5月6日8:22 1588724520 高等数学
    2. 2020年5月6日9:23 1588728180 高等数学
    3. 2020年5月7日14:01 1588831260 线性代数
    4. 2020年5月8日10:03 1588903380 概率论
    5. 2020年5月13日8:02 1589328120 高等数学
    6. 2020年5月13日10:47 1589338020 高等数学
    7. 2020年5月14日12:59 1589432340 线性代数
    4. 2020年5月15日10:04 1589508240 概率论
    '''
    # 上周的记录
    week1 = [['高等数学', 1589328120], ['高等数学', 1589338020],
             ['线性代数', 1589432340], ['概率论', 1589508240]]
    # 上上周的记录
    week2 = [['高等数学', 1588724520], ['高等数学', 1588728180],
             ['线性代数', 1588831260], ['概率论', 1588903380]]
    # 从今天起前7天的历史记录
    day7 = [['高等数学', 1589328120], ['高等数学', 1589338020],
            ['线性代数', 1589432340], ['概率论', 1589508240]]
    # 从今天七前7到14天的历史记录
    day14 = [['高等数学', 1588724520], ['高等数学', 1588728180],
             ['线性代数', 1588831260], ['概率论', 1588903380]]
    # 这边情况特殊恰好是一样的，实际如需避免多次访问数据库可用week1替代day7，week2替代day14，效果差别应该不大
    sigma = Sigma(day7, day14)
    periodicity = Periodicity(week1, week2)
    history = [['高等数学', 1589328120], ['高等数学', 1589338020],
               ['线性代数', 1589432340], ['概率论', 1589508240],
               ['高等数学', 1588724520], ['高等数学', 1588728180],
               ['线性代数', 1588831260], ['概率论', 1588903380]]
    schedule = [['高数考试', 1589853600], ['线代考试', 1589950800]]
    # history和schedule假定读入时就已经框定一个月的范围！！！
    k = Document_Sort(history, schedule, sigma, periodicity, now=1589846400)
    print(k)
    result = []
    for i in k:
        result.append(i[0])
    print(result)
