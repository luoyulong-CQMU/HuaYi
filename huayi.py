# -*- coding:utf-8 -*-

"""
作者：luoyu
日期：2021年08月06日
"""
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import subprocess
import threading

"""
华医网继续教育强化学习

"""

def now():
    return time.strftime('%Y-%m-%d', time.localtime(time.time()))


def start_chrome():
    # print("启动浏览器")
    try:
        os.system("taskkill /f /im chromedriver.exe /t")
    except:
        print("clean_chromedriver_falied！")
    try:
        os.system("taskkill /f /im chrome.exe /t")
    except:
        print("failed!")
    subprocess.call('chrome.exe --remote-debugging-port=9222 --user-data-dir="D:\selenium\chrome_temp')


class HuaYi(object):

    def __init__(self, num):
        self.is_next_page = True if num == "2" else False
        self.current_video_elem = None
        self.passed_item = ''
        self.options = Options()
        self.options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.browser = webdriver.Chrome(options=self.options)
        # self.browser = webdriver.Chrome()
        self.main_url = 'https://www.91huayi.com/'
        self.global_url = 'http://cme24.91huayi.com/pages/knowledge_navigation.aspx?title_id=cd41ce9a-0dfc-49ef-819f-bed2b9cceace&title_name=%E5%9B%BDI%E7%B1%BB5%E5%88%86'
        self.local_url_tg = 'http://cme24.91huayi.com/pages/knowledge_navigation.aspx?title_id=be64363d-7d50-4b06-bda2-a88100eeeed3&title_name=%E5%B8%82%E7%BA%A7%E6%8E%A8%E5%B9%BF%E9%A1%B9%E7%9B%AE%EF%BC%885%E5%88%86%E6%8E%A8%E5%B9%BF%E5%8D%A1%E4%B8%93%E7%94%A8%EF%BC%89'
        self.select_url = self.global_url if num == '1' else self.local_url_tg

    def open_main_page(self):
        self.browser.get(url=self.main_url)
        input("请在当前页面完成登陆，任意键继续.. . ")
        self.select_class()

    def log_in(self):
        self.browser.find_element_by_xpath('/html/body/div[4]/div/div[2]/div[2]/a[2]').click()
        phone_id = input("输入手机号码：")
        passwd = input("输入密码：")
        code = input("请输入验证码：")
        self.browser.find_element_by_xpath('//*[@id="selectPopLoginType"]/option[2]').click()
        self.browser.find_element_by_xpath('//*[@id="userName"]').send_keys(phone_id)
        time.sleep(1)
        self.browser.find_element_by_xpath('//*[@id="userPwd"]').send_keys(passwd)
        self.browser.find_element_by_xpath('//*[@id="loginAccessPwd2"]').send_keys(code)
        time.sleep(1)
        self.browser.find_element_by_xpath('//*[@id="butLogin"]').click()
        self.select_class()

    def select_class(self):
        self.browser.get(self.select_url)
        time.sleep(1)
        if self.is_next_page:
            self.browser.switch_to.frame('course')
            self.browser.find_element_by_xpath('/html/body/form/div[3]/div[20]/div/div/div[2]/a[13]').click()  # 下一页
            time.sleep(1)
        else:
            self.browser.switch_to.frame('course')
        class_html_bs4 = BeautifulSoup(self.browser.page_source, 'lxml')
        class_lst = class_html_bs4.findAll('dt')[2:]
        class_url = []
        top_url = 'http://cme24.91huayi.com/pages/'
        for each in class_lst:
            i = each.findAll('a')[0]
            each_url = top_url + i.get('onclick').split('href=')[1].replace("'", "")
            each_text = i.text.strip()
            class_url.append((each_text, each_url))
        for item in class_url:
            print(f"准备学习课程-->【{item[0]}】")
            self.passed_item += item[0]
            self.get_lesson(item)

    def get_lesson(self, item):
        self.browser.get(item[1])
        page_source = BeautifulSoup(self.browser.page_source, 'lxml')
        a = page_source.findAll('a', target='new_courseWare')
        lesson_title = ""
        for i in range(0, len(a)):
            # url获取的时候，一个为题目，一个为图片，2个的url路径相同
            pic_url = ""
            url = ""
            try:  # 尝试获得lesson链接
                url = 'http://cme24.91huayi.com/' + a[i].get('href')[3:]
                try:
                    lesson_title = a[i].find('strong').text
                except:  # 尝试获得图片链接，通过链接判断是否学习完成;
                    # pic_studing 学习中;anniu_01a 未学习; anniu_03a 学习完成
                    pic_url = a[i].find('img').get('src')
                    if self.current_video_elem == url:
                        continue
                    elif 'anniu_03a' in pic_url:
                        print(f'已学习完小课-->{item[0]}--', lesson_title)
                    else:
                        print(f"准备学习小课-->{item[0]}--", lesson_title)
                        self.browser.get(url)
                        self.current_video_elem = url
                        self.video_play()
            except Exception as e:
                print(e)

    def video_play(self):
        # self.browser.get(self.current_video_elem)
        time.sleep(2)
        try:  # 支持html5
            self.browser.find_element_by_xpath('//*[@id="video"]/div/div[2]/div[2]/div[1]/button').click()
            total_time = self.browser.find_element_by_xpath(
                '//*[@id="video"]/div/div[2]/div[2]/div[1]/div/span[3]').text
            print("开始学习小课,当前课程预计剩余时间:", total_time)

            # 调节播放速度，调用js脚本
            self.browser.execute_script('''
            var div = document.createElement("div");
            div.innerHTML = '<div id="speeddiv" style="position:fixed;left:10px;top:10px;z-index:9999999;font-size:6em;display:none"></div>'
            document.getElementsByTagName('body')[0].appendChild(div);
            document.querySelector('video').playbackRate =16;
            ''')
            print("尝试开启16倍加速,如果网络或硬件受限,请尝试降低倍速")
            while True:
                current_time = ""
                try:
                    current_time = self.browser.find_element_by_xpath(
                        '//*[@id="video"]/div/div[2]/div[2]/div[1]/div/span[1]').text
                    time.sleep(1)
                except:
                    pass
                # 每秒获取播放时间以打印
                # print(current_time)
                if current_time == total_time:
                    print("播放完成！")
                    break
            self.browser.find_element_by_xpath('//*[@id="jrks"]').click()
            self.get_exam_question()
        except:
            try:
                self.browser.find_element_by_xpath("//span[@class='ccH5TogglePlay']").click()
            except:
                pass
            total_time = self.browser.find_element_by_xpath("//em[@class='ccH5TimeTotal']").text
            print("开始学习小课,当前课程预计剩余时间:", total_time)
            print("当前课程使用了ccH5播放器，可能无法倍速！-->还是尝试先")
            # 调节播放速度，调用js脚本
            self.browser.execute_script('''
                        var div = document.createElement("div");
                        div.innerHTML = '<div id="speeddiv" style="position:fixed;left:10px;top:10px;z-index:9999999;font-size:6em;display:none"></div>'
                        document.getElementsByTagName('body')[0].appendChild(div);
                        document.querySelector('video').playbackRate =16;
                        ''')
            while True:
                self.browser.execute_script("document.querySelector('video').playbackRate =16")
                self.browser.find_element_by_xpath('//*[@id="jrks"]').click()
                time.sleep(2)
                try:
                    self.browser.find_element_by_xpath('//*[@id="jrks"]')
                except:
                    break
            self.get_exam_question()

    def get_exam_question(self):
        print("进入考试")
        time.sleep(1)
        page = BeautifulSoup(self.browser.page_source, 'lxml')
        answers = page.findAll('tbody')[1:]
        titles = page.findAll('table', class_="tablestyle")
        self.question_dic = {}
        self.answer_elem_lst = []
        for index, i in enumerate(titles):
            title = i.find('span').text[2:].strip()
            j = answers[index].findAll('label')
            answer_ = []
            for each in j:
                self.answer_elem_lst.append(each)
                answer = each.text
                answer_.append(answer.strip().replace('\n', '').replace(" ", ""))
            self.question_dic[title] = answer_
        self.answer_question()

    def answer_question(self):
        while True:
            for k in self.question_dic:
                answer = self.question_dic[k][0]
                # 2个目的，获取题目，匹配合格后，要当前组；
                # 这里必须要xpath重新匹配，避免会有相同答案的问题，会卡循环
                question_xpath = f"//span[contains(text(),'{k}')]"
                answer_xpath = question_xpath + "/../../../../following-sibling::table[1]/tbody/tr/td/label"
                answer_elements = self.browser.find_elements_by_xpath(answer_xpath)
                for elem in answer_elements:
                    compare_answer = elem.text.strip().replace('\n', "").replace(" ", "")
                    # print(compare_answer, answer)
                    if answer in compare_answer:
                        elem.click()
                        break
            self.browser.find_element_by_xpath('//*[@id="btn_submit"]').click()
            try:
                a = self.browser.switch_to.alert
                print(a.text)
                time.sleep(1)
                a.accept()
                if "申请学分" in a:
                    break
            except:
                # print('break???')
                break
        time.sleep(1)
        self.check_next()

    def answer_question_backup(self):
        while True:
            for k in self.question_dic:
                answer = self.question_dic[k][0]
                for j in self.answer_elem_lst:

                    if answer == j.text:
                        xpath = f"//label[text()='{answer}']"
                        # self.browser.find_element_by_xpath(xpath).click()
                        # 调用all的原因很简单，因为可能有多个相同答案;
                        all_ = self.browser.find_elements_by_xpath(xpath)
                        for each in all_:
                            each.click()
                            print("each", each.text)
                        break

            self.browser.find_element_by_xpath('//*[@id="btn_submit"]').click()
            try:
                a = self.browser.switch_to.alert
                print(a.text)
                time.sleep(1)
                a.accept()
            except:
                break
        time.sleep(1)
        self.check_next()

    def check_next(self):
        statue = self.browser.find_element_by_xpath('/html/body/div[5]/b').text
        print(statue)
        if "考试没过" in statue:
            title = BeautifulSoup(self.browser.page_source, 'lxml').findAll('dd')
            for each in title:
                question_title = each.get('title')
                for k in self.question_dic:
                    if question_title in k:
                        # 移除第一个选项，因为默认选择的是第一个;
                        self.question_dic[k] = self.question_dic[k][1:]
            self.browser.find_element_by_xpath('/html/body/div[6]/div[1]/div/input[2]').click()
            self.answer_question()
        else:
            # page_source = self.browser.page_source
            if "立即学习" in self.browser.page_source:
                print("当前小课学习完成")
                # self.browser.get(self.video_play())
            else:
                print("当前课程学习完成！")
                try:
                    self.browser.find_element_by_xpath("/html/body/div[6]/div[1]/div[3]/div[3]/button").click()
                except:
                    pass

    def test(self):
        self.browser.find_element_by_xpath('//*[@id="btn_submit"]').click()
        a = self.browser.switch_to.alert
        print(a.text)
        time.sleep(1)
        a.accept()


if __name__ == '__main__':
    #
    thread_hi = threading.Thread(target=start_chrome, args=())
    thread_hi.start()
    print("启动浏览器")
    time.sleep(2)
    print("[1]. 全国I类5分项目")
    print("[2]. 市I类本地推广")
    select_num = input("请输入学习选择[1-2]):")
    current_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    # limit_date = '2021-08-11 12:00:00'
    # if current_date < limit_date:
    app = HuaYi(select_num)
    app.select_class()
    # else:
    #     input('任意键继续. . .')
    #     time.sleep(2)
