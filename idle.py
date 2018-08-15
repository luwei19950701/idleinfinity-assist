# -*- coding: utf-8 -*-

import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains


class Idle():
    """定义参数"""

    def __init__(self, username="", password=""):
        self.bossId = None
        self.username = username  # 账号
        self.password = password  # 密码
        self.charList = []  # 当前账号角色列表
        self.charId = None  # 当前角色id
        self.nth = None  # 第几个角色
        self.checkedPublic = []  # 不可点击的区域
        self.sum = 0  # 总花费时间
        self.count = 0  # 总战斗次数
        self.remaining = 0  # 剩余怪物数量
        self.nowTime = 0  # 进入秘境的时间
        self.timeRemaining = 0  # 预计剩余时间
        self.stone = 0  # 剩余石头数量
        self.boss = False  # 是否刷完Boss重置
        self.type = 1  # 刷副本类型 1:全部刷完  2:刷掉至少一半和Boss  3:刷掉Boss

        # self.homeUrl = "http://118.25.41.160:8888"
        self.homeUrl = "https://www.idleinfinity.cn"
        self.detailUrl = self.homeUrl + "/Character/Detail?id="
        self.mysteryUrl = self.homeUrl + "/Map/Detail?id="
        # self.codeUrl = "http://118.25.41.160:8888/Home/Code"
        self.codeUrl = "https://www.idleinfinity.cn/Home/Code"

        print("启动浏览器中...")
        self.driver = webdriver.Chrome()
        # self.driver.set_window_size(1000, 800)
        # self.driver.implicitly_wait(10)

    def start(self):
        self.driver.get(self.homeUrl)

        self.inputAccount()

        while True:
            code = self.driver.find_element_by_id("code")
            login = self.driver.find_element_by_class_name("btn-login")
            temp = input("手动输入验证码:")
            code.send_keys(temp)
            self.click(login, False)

            if not self.isElementExists(".img-thumbnail"):
                self.inputAccount()
                print("验证码输入错误，重新输入")
                continue

            break

        # self.driver.minimize_window()
        print("获取角色信息...")
        self.getUserList()

    # 启动浏览器 登录账号
    def inputAccount(self):
        username = self.driver.find_element_by_id("username")
        password = self.driver.find_element_by_id("password")
        username.send_keys(self.username)
        password.send_keys(self.password)

    # 获取所有角色信息
    def getUserList(self):
        jobs = self.driver.find_elements_by_class_name("col-sm-6")
        j = 1
        for i in jobs:
            temp = {}
            temp['name'] = i.find_element_by_class_name("panel-heading").text.split(' ')[0]
            temp['job'] = i.find_element_by_class_name("media-body").text.split("\n")[0]
            temp['id'] = i.find_element_by_class_name("btn-default").get_attribute("href").split('=')[1]
            print("角色 %d：\n    id：%s\n    昵称：%s\n    职业：%s" % (j, temp['id'], temp['name'], temp['job']))
            self.charList.append(temp)
            j += 1

    # 选择角色
    def character(self):
        while True:
            self.nth = int(input("输入角色编号："))
            if self.nth == '' or int(self.nth) > len(self.charList):
                print("错误的角色编号，重新输入")
                continue

            self.charId = self.charList[int(self.nth) - 1]['id']

            self.driver.get(self.detailUrl + str(self.charId))
            print("选择了第 %s 个角色" % (self.nth))
            break

    # 进入秘境
    def toMystery(self):
        self.driver.get(self.mysteryUrl + str(self.charId))
        time.sleep(1)

    def isMystery(self):
        text = self.driver.find_element_by_xpath("/html/body/div[1]/div/div[1]/div[1]/div[1]").text.split("\n")[0]
        text = list(filter(str.isdigit, text))
        strs = ''
        for i in text:
            strs += str(i)

        if (int(strs) % 10 != 0):
            raise Exception("当前非秘境副本！！！\n")

    # 开始秘境  1:全部刷完  2:刷掉至少一半和Boss  3:刷掉Boss
    def mystery(self, type):
        print("秘境开始...")
        self.nowTime = time.time()
        # 进入秘境
        self.toMystery()
        self.isMystery()

        self.click("/html/body/div[1]/div/div[1]/div[1]/div[1]/div/a[1]")

        self.boss = (type == 3)

        while True:
            # 剩余怪物数量
            monster_number = int(
                self.driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div[2]/p[11]/span[2]").text)
            # 剩余Boss数量
            boss_number = int(
                self.driver.find_element_by_xpath("/html/body/div[1]/div/div[2]/div/div[2]/p[12]/span[2]").text)

            self.remaining = monster_number

            # 剩余石头数量
            self.stone = int(self.driver.find_element_by_xpath("/html/body/div[1]/div/div[1]/div/div[1]/span").text)

            if type == 1:
                if monster_number == 0:
                    if self.stone == 0:
                        quit()
                    self.resetMystery()
            elif type == 2:
                if monster_number <= 25 and boss_number == 0:
                    if self.stone == 0:
                        quit()
                    self.resetMystery()
            else:
                if boss_number == 0:
                    if self.stone == 0:
                        quit()
                    self.resetMystery()

            div = self.driver.find_element_by_xpath("/html/body/div[1]/div/div[1]/div/div[2]")
            remove = self.driver.find_element_by_xpath('/html/body/footer/div/p/span[2]/a')

            # 判断空格
            public = div.find_elements_by_class_name("public")
            print("迷雾区域判断，稍后自动开始模拟点击...")
            for i in public:
                currentId = int(i.get_attribute("id"))
                #print(currentId)
                currentClass = i.get_attribute("class")
                #print(currentClass)

                if (currentId in self.checkedPublic) or ("monster" in currentClass):
                    continue

                if self.isCanDiv(currentId, currentClass):
                    self.checkedPublic.append(currentId)
                    continue
                else:
                    # action = ActionChains(self.driver)
                    # self.driver.execute_script("arguments[0].style.display='none';",remove)
                    # location = i.location
                    # #action.move_to_element(i).click(i).perform()
                    #
                    # action.move_by_offset(location['x'],location['y']).click(i).perform()
                    # time.sleep(1)
                    self.click(i, False,True)

            # 判断是否有怪
            monster = div.find_elements_by_class_name("monster")
            # 优先清除地图Boss
            if type != 1:
                for i in monster:
                    if "boss" in i.get_attribute("class"):
                        self.remaining = 0
                        self.startPlay(i)
                        break
                if self.remaining == 0:
                    continue

            # 清地图小怪
            monsterLen = len(monster)
            if monsterLen:
                self.startPlay(monster.pop())
                continue

    # 开始战斗
    def startPlay(self, monster):
        monsterId = monster.get_attribute("id")
        self.checkedPublic.append(monsterId)
        self.click(monster, False,True)
        if self.isElementExists("#time"):
            count = int(self.driver.find_element_by_id("time").text)
            print("等待上次战斗结束 %s 秒" % (count))
            self.setTimeOut(count)

        count = (len(self.driver.find_elements_by_class_name("turn")) / 2) + 1
        self.driver.execute_script("document.getElementsByClassName('turn')[0].style.display='block'")
        result = self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[3]/div/div[1]/div[1]").text
        self.sum += count
        self.count += 1

        if self.boss:
            when_minutes = int((time.time() - self.nowTime) / 60)
            if self.remaining:
                minutes = str(int(self.sum / self.count * 51 / 60) - when_minutes) + " 分"
            else:
                minutes = str(count) + " 秒"
            print("%s 怪物ID: %s, 战斗时间: %s 秒, 本次秘境用时: %s 分钟, 预计剩余时间: %s \n" % (
                result, monsterId, count, when_minutes, minutes))
        else:
            when_minutes = self.sum / self.count
            minutes = int(when_minutes * 51 / 60)
            when_minutes = int((self.remaining - 1) * when_minutes / 60)
            print("%s 怪物ID: %s, 战斗时间: %s 秒，预计本次剩余时间: %s 分钟, 预计单次耗时: %s 分\n" % (
                result, monsterId, count, when_minutes, minutes))
        self.setTimeOut(count)

        self.click("/html/body/div[1]/div/div/div[1]/div[1]/div/a")
        self.setTimeOut(1)

    # 判断是否是不需要被点击的div,True表示不能被点击,
    def isCanDiv(self, divId, currentClass):
        left = self.isLeftCanDiv(divId, currentClass)
        top = self.isTopCanDiv(divId, currentClass)
        right = self.isRightCanDiv(divId, currentClass)
        bottom = self.isBottomCanDiv(divId, currentClass)
        #print('########%d'%divId)
        #print(left)
        #print(top)
        #print(right)
        #print(bottom)
        #print('########end')

        return left and top and right and bottom

    # 判断左侧是否是可见区域,或者点击不能点亮
    def isLeftCanDiv(self, divId, currentClass):
        if (divId % 20) != 0:
            left = self.driver.find_element_by_id(str(divId - 1)).get_attribute("class")
            if ("mask" in left) and ("left" not in currentClass):
                return False
        return True

    def isTopCanDiv(self, divId, currentClass):
        if divId > 19:
            top = self.driver.find_element_by_id(str(divId - 20)).get_attribute("class")
            if ("mask" in top) and ("top" not in currentClass):
                return False
        return True

    def isRightCanDiv(self, divId, currentClass):
        if (divId % 20) != 19:
            right = self.driver.find_element_by_id(str(divId + 1)).get_attribute("class")
            if ("mask" in right) and ("left" not in right):
                return False
        return True

    def isBottomCanDiv(self, divId, currentClass):
        if divId < 380:
            bottom = self.driver.find_element_by_id(str(divId + 20)).get_attribute("class")
            if ("mask" in bottom) and ("top" not in bottom):
                return False
        return True

    # 重置秘境
    def resetMystery(self):
        self.nowTime = time.time()
        print("本次秘境结束，即将重置...")
        self.checkedPublic.clear()
        self.click("/html/body/div[1]/div/div[1]/div/div[1]/div/a[1]")
        self.click("//*[@id=\"modalConfirm\"]/div/div/div[3]/button[1]")

    # type == True 传入的是一个字符串
    # type == False 传入的是一个对象
    def click(self, element, type=True,monster=False):
        if monster:
            js = "const width = $(arguments[0]).width() - 1;" \
             "const height = $(arguments[0]).height() - 1;" \
             "const rect = $(arguments[0]).offset();" \
             "const x = Math.round(rect.left + 1 + (width * Math.random())) + $(window).scrollLeft(); " \
             "const y = Math.round(rect.top + 1 + (height * Math.random())) + $(window).scrollTop(); " \
             "$(arguments[0]).trigger({ type: 'mousedown', pageX: x, pageY: y });"
        else:
            if isinstance(element, str):
                element = self.driver.find_element_by_xpath(element)
                js = "arguments[0].click()"
            else:
                js = "const width = $(arguments[0]).width() - 1;" \
                     "const height = $(arguments[0]).height() - 1;" \
                     "const rect = $(arguments[0]).offset();" \
                     "const x = Math.round(rect.left + 1 + (width * Math.random())) + $(window).scrollLeft(); " \
                     "const y = Math.round(rect.top + 1 + (height * Math.random())) + $(window).scrollTop(); " \
                     "$(arguments[0]).trigger({ type: 'click', pageX: x, pageY: y });"

        self.driver.execute_script(js, element)
        # ActionChains(self.driver).click(element).perform()
        # self.driver.execute_script("arguments[0].click();", element)
        time.sleep(1)

    # 出售物品
    def sell(self):
        self.driver.get("%s/Equipment/Query?id=%s" % (self.homeUrl, self.charId))

        while True:
            goodsType = int(input("选择要出售的类型：\n   0 全部 1 普通 2 魔法 3 稀有 4 套装 5 传奇 6 神奇\n输入对应数字:"))
            if goodsType > 6 or goodsType < 0:
                print("输入错误，重新输入")
                continue

            types = [
                "physical", "base", "magical", "rare", "set", "unique", "artifact"
            ]

            temp = self.driver.find_element_by_xpath(
                "/html/body/div[1]/div/div/div[2]/div[1]/div/div[1]/ul").find_element_by_class_name(types[goodsType])
            self.click(temp, False)
            temp = self.driver.find_element_by_class_name("equip-sellbagallpage")
            self.click(temp, False)
            self.click("//*[@id=\"modalConfirm\"]/div/div/div[3]/button[1]")
            print("选中物品已经出售完成...\n")
            print("返回菜单...\n")
            time.sleep(1)
            break

    # 倒计时
    def setTimeOut(self, count):
        while count > 0:
            print("\r倒计时 %s 秒" % count, end="")
            count -= 1
            time.sleep(1)

        print('\r', end="")

    # 判断元素是否存在
    def isElementExists(self, element):
        try:
            self.driver.find_element_by_css_selector(element)
            return True

        except:
            return False


    # 回到主页，角色选择页面
    def home(self):
        self.click("/html/body/nav/div/div[1]/a")

    # 回到主页，角色选择页面
    def quit(self):
        self.driver.quit()


if __name__ == '__main__':
    idle = Idle()
    idle.start()
    idle.main()
