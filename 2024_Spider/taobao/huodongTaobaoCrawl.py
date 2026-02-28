# _*_ coding: utf-8 _*_
# @Time : 2025/8/8 星期五 20:02
# @Author : 韦丽
# @Version: V 1.0
# @File : huodongTaobaoCrawl.py
# @desc : 淘宝网商品活动数据采集
import requests
from fake_useragent import FakeUserAgent
from urllib.parse import unquote, quote


class activaeShopCrawl:
    def __init__(self, url):
        self.url = url

    def getRequest(self):
        header = {
            'User-Agent': FakeUserAgent().random
        }
        return requests.get(url=self.url, headers=header)

    def exec(self):
        response = self.getRequest()


    def unquote_str(self, str):
        return unquote(str)

    def taobalProductList(self):
        url = 'https://h5api.m.taobao.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/?jsv=2.7.4&appKey=12574478&t=1755001703671&sign=3a10571900a7101312f734d58f8132f0&api=mtop.relationrecommend.wirelessrecommend.recommend&v=2.0&timeout=10000&type=jsonp&dataType=jsonp&callback=mtopjsonp144&data=%7B%22appId%22%3A%2234385%22%2C%22params%22%3A%22%7B%5C%22device%5C%22%3A%5C%22HMA-AL00%5C%22%2C%5C%22isBeta%5C%22%3A%5C%22false%5C%22%2C%5C%22grayHair%5C%22%3A%5C%22false%5C%22%2C%5C%22from%5C%22%3A%5C%22nt_history%5C%22%2C%5C%22brand%5C%22%3A%5C%22HUAWEI%5C%22%2C%5C%22info%5C%22%3A%5C%22wifi%5C%22%2C%5C%22index%5C%22%3A%5C%224%5C%22%2C%5C%22rainbow%5C%22%3A%5C%22%5C%22%2C%5C%22schemaType%5C%22%3A%5C%22auction%5C%22%2C%5C%22elderHome%5C%22%3A%5C%22false%5C%22%2C%5C%22isEnterSrpSearch%5C%22%3A%5C%22true%5C%22%2C%5C%22newSearch%5C%22%3A%5C%22false%5C%22%2C%5C%22network%5C%22%3A%5C%22wifi%5C%22%2C%5C%22subtype%5C%22%3A%5C%22%5C%22%2C%5C%22hasPreposeFilter%5C%22%3A%5C%22false%5C%22%2C%5C%22prepositionVersion%5C%22%3A%5C%22v2%5C%22%2C%5C%22client_os%5C%22%3A%5C%22Android%5C%22%2C%5C%22gpsEnabled%5C%22%3A%5C%22false%5C%22%2C%5C%22searchDoorFrom%5C%22%3A%5C%22srp%5C%22%2C%5C%22debug_rerankNewOpenCard%5C%22%3A%5C%22false%5C%22%2C%5C%22homePageVersion%5C%22%3A%5C%22v7%5C%22%2C%5C%22searchElderHomeOpen%5C%22%3A%5C%22false%5C%22%2C%5C%22search_action%5C%22%3A%5C%22initiative%5C%22%2C%5C%22sugg%5C%22%3A%5C%22_4_1%5C%22%2C%5C%22sversion%5C%22%3A%5C%2213.6%5C%22%2C%5C%22style%5C%22%3A%5C%22list%5C%22%2C%5C%22ttid%5C%22%3A%5C%22600000%40taobao_pc_10.7.0%5C%22%2C%5C%22needTabs%5C%22%3A%5C%22true%5C%22%2C%5C%22areaCode%5C%22%3A%5C%22CN%5C%22%2C%5C%22vm%5C%22%3A%5C%22nw%5C%22%2C%5C%22countryNum%5C%22%3A%5C%22156%5C%22%2C%5C%22m%5C%22%3A%5C%22pc%5C%22%2C%5C%22page%5C%22%3A2%2C%5C%22n%5C%22%3A48%2C%5C%22q%5C%22%3A%5C%22%25E7%2594%25B5%25E8%2584%2591%25E6%2595%25B4%25E6%259C%25BA%5C%22%2C%5C%22qSource%5C%22%3A%5C%22url%5C%22%2C%5C%22pageSource%5C%22%3A%5C%22a21bo.jianhua%2Fa.201867-main.d2_2.3de02a89OHEQWl%5C%22%2C%5C%22channelSrp%5C%22%3A%5C%22%5C%22%2C%5C%22tab%5C%22%3A%5C%22all%5C%22%2C%5C%22pageSize%5C%22%3A%5C%2248%5C%22%2C%5C%22totalPage%5C%22%3A%5C%22100%5C%22%2C%5C%22totalResults%5C%22%3A%5C%228594%5C%22%2C%5C%22sourceS%5C%22%3A%5C%220%5C%22%2C%5C%22sort%5C%22%3A%5C%22_coefp%5C%22%2C%5C%22bcoffset%5C%22%3A%5C%22-9%5C%22%2C%5C%22ntoffset%5C%22%3A%5C%2213%5C%22%2C%5C%22filterTag%5C%22%3A%5C%22%5C%22%2C%5C%22service%5C%22%3A%5C%22%5C%22%2C%5C%22prop%5C%22%3A%5C%22%5C%22%2C%5C%22loc%5C%22%3A%5C%22%5C%22%2C%5C%22start_price%5C%22%3Anull%2C%5C%22end_price%5C%22%3Anull%2C%5C%22startPrice%5C%22%3Anull%2C%5C%22endPrice%5C%22%3Anull%2C%5C%22categoryp%5C%22%3A%5C%22%5C%22%2C%5C%22ha3Kvpairs%5C%22%3Anull%2C%5C%22myCNA%5C%22%3A%5C%22LtAcIV67%2BVEBASQJikTHkLT5%5C%22%2C%5C%22screenResolution%5C%22%3A%5C%221920x1080%5C%22%2C%5C%22userAgent%5C%22%3A%5C%22Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F139.0.0.0%20Safari%2F537.36%5C%22%2C%5C%22couponUnikey%5C%22%3A%5C%22%5C%22%2C%5C%22subTabId%5C%22%3A%5C%22%5C%22%2C%5C%22np%5C%22%3A%5C%22%5C%22%2C%5C%22clientType%5C%22%3A%5C%22h5%5C%22%2C%5C%22isNewDomainAb%5C%22%3A%5C%22false%5C%22%2C%5C%22forceOldDomain%5C%22%3A%5C%22false%5C%22%7D%22%7D&bx-ua=231!tDD7CkmUlJE%2BjT6vd473fSBjUGg0uSOn%2BfYFmLQQwGng0wmHntUSK%2B2ttWIwYfiRlXeQ%2BthKJXIvfegh2cGUuRIvbZ9fhRfZbrcyCwJp1Tn%2F1O6FZpESbo3QzHthMFlyGdU66t9uKYMx15yS8pe%2BytwIUGBsqq3t9V4iCQkjtEQbKDuzk6qVQDIOFb80WS6gTxiz4twEVZPYifp9zS9rqUtFQN41RRE3gDPUCv8XBPaCVKx40BMx3kop0Q3oyE%2BjauHhU0HIenHGHkE%2B%2B%2B3%2BqCS4%2BItuWAcuFmiNo%2BroPZkSLcdYjhOwCk4Sh8zMIdMap42U4vMMi8A1%2F1%2B2gy%2B0kvvdKZs6IZxJ8467eQOQXZK7xndNp6Eazv3GXJ2x%2BKkOBA%2BE13HPhkjHIyRvqUXaR3P%2FCM1xI3j%2Bto5aa7je7ZYga2VnoExp9nLAdYzV%2FgnisX8s%2FMtNBVpJinBRaT2yWr%2FVnK%2Fq%2FP43g2A9K9Kv5BwKUdEcvrd1BA1LPr6CK5287%2Bi6URjESjMPWqCjuulCLka%2B7BWx0pIQSvyR%2FD0dbzfEgHEalxiu136VfkfYofU6oaeGxQz4241to%2F749JKTmu%2BdkTs4OAQYuy6oxBcvMJPjEvfLmqt7B2rnwl%2BdhyAQh%2BZJEo1yRlhR7gafDKa%2BPhhnp50%2FUd1%2FBKUxnzY6lqhtzmwqglPAxWYYm5cWeAme1Frv5rWI1VRItkBZJ4zKx60NWSMTnX5VQphg5fBx4zKG3Yp8CubYoDYeSOBuZV57EEEnVAb8Gw6%2FEgNmZNT4A6NJPscCkuxeqt8oD8YnOZK%2B1l4FUFhoaCeUPNEH83PWK78zhnmk1exSIL%2B7D3X5K9bxJNDSgOB2bnqoT3oerSr0aJPmNXnFBvgbfYm7sg7G00SIRlcokFWyKjr4tyBHeT0CDU%2Fy8BrprpBkPQLSSmyJBG19M9d%2BkGtxYb5nzGS42%2Br%2B7avUw9FZhRSOtUUYK0HKBHSZ02RGSUaDDT0qLC1VDAPHtoztOsEyk91VHOaVrWXnPY%2FC5Zo3OsXaT4B%2B3FP3492rBved5SsusY1ee%2BwIMwDqYpilc2%2Bt76BwopD49WPL3whp%2BC3eQYNs1easRdDdTnAV8neBUHPYrDAMNLjb2QdZng6scM%2BuCP%2BCBZUUpw7RjSVKw9I9fuvT738kK21Bkg%2FNL0kihSSQ8WO5HNOl6kWCHFq6KqTAUpPQPv4n8AP%2Bp0RMQv5JbLiC%2FdqbOaKnKs4b7YjJRF4KIBHACBEUYLQLB9fw0%2Bh36uYNRgG56MdvieC0FBJL0NADmHdezjxFz6uKSUMWAmXdJytfrGSXWSLkQ%2FFarwbADfuYzjD81PIgGEVczhemtjcDXYnH%2B9GkUb868smQl3B1U%2FEsihSQ8QH53el%2Fn9TQDbHU36STbHTHezZ%2BPmxZ2%2BeC8JxoJqtmr6hCVk3Ooi0QJ%2BIYGzziqXfJu2CNbBQSDeEu2zLFwIwGp0vxxdgIfzg6yLhOmLoBVThOv0bhz%2BuWWDbk9hLEwmQmdtCoAl0sNJbVZFNZS2SyTXOtcjtkzB9MTbC1kdHJn8UyBX4S2TO%2F%2BOdZse%2B98x8ZGtmVmA1vyGqMuI9az3ckHmCiic5HRe09M%2FxO48pJ%2BenA6M14ZKDCHDj4cAGgVWWHm0rNGiNtxqRVJudgu4VxGZhkhTALYoiyy5SPQIbc0kMbcD5P6mpxmAum0zIQo9ZN0Io1cql%2Fsnh3zUv8SCJA2iJEBdCyMLtBPoSx7IoOqAXHulN55c1LeHwCAQEdAx%2FQnEXHEUfOeWWdefXRUz6eyq4BbAdN9UwhUEmaYpVK3vmz7dtrjpKlzQbKusoolR0XiLzUc2yvu5JgSO3Yeqv2bnmn%2FhRiO47aP2BPbd%2B3z0n1giwVsDSN87lTyV2d0uZ1jHAsYqK%2F%2FIO28Sw5jmtzLsZ0AAhTTkN7JQoEG03PPViWbVHptDMezWS0Pptyy0jww1mTefWFxy2hRIEGgDZEawDOOEaRDQ7aUKcNvnwUjB4OoQVkUwceYDwaCT580cBTjP7juddOhlI5lNIjFka7fYL%2F&bx-umidtoken=T2gAhpYHRqOwjgFUsTtAGw5bEGAizjgLwfycg6AzFu9ZjBI7R_BL5P451ku9rSf39KU%3D&bx_et=gRAqhUTHrjh4tUZSG3CaYWPMx7CYB1uSAoR1SNY9WPjcii9PSht-WqCXSG-wVgFXhxB1bP5vNKN1cmCwSH1ZADGIOELAT1mIAe5FrHCh7oVgilZur1_Zg0M7VELA612MeEDykPkcWnNcSG0PZN7Lo1jGIg0P7wSGsiXgq8bhqGfMjt4lqN7TsN2cSb0PWgjGs1xGZ471qGfGshYoIeYDS77Cn4qlL3j49r32-Ejzs5Am6tjUAN7RlQ7V3MXkV5bWaZWVxERedU3lrQOPdTas4_YpFnbPTbwctUJMYpxtd8C2SKxOUnn8Ug9kFFjGEPVBzs9WAdXrojYPgiWFkTz_HsJMDCWv3P3prsxJpMBme0QyGB6NvTromUTPm9Jwc0FGcp8k49O7VW192dxG73qV4WrOrjXB6KrgQtbRzMgrzg7prdCeDYGbBRBl9aSIlZwTBtbRzMgrzReOEwQPAq_f.'
        print(f'url: {self.unquote_str(url)}')
        # https://h5api.m.taobao.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/
        # ?jsv=2.7.4
        # &appKey=12574478
        # &t=1755001703671
        # &sign=3a10571900a7101312f734d58f8132f0
        # &api=mtop.relationrecommend.wirelessrecommend.recommend
        # &v=2.0
        # &timeout=10000
        # &type=jsonp
        # &dataType=jsonp
        # &callback=mtopjsonp144
        # &data={"appId":"34385","params":"{\"device\":\"HMA-AL00\",\"isBeta\":\"false\",\"grayHair\":\"false\",\"from\":\"nt_history\",\"brand\":\"HUAWEI\",\"info\":\"wifi\",\"index\":\"4\",\"rainbow\":\"\",\"schemaType\":\"auction\",\"elderHome\":\"false\",\"isEnterSrpSearch\":\"true\",\"newSearch\":\"false\",\"network\":\"wifi\",\"subtype\":\"\",\"hasPreposeFilter\":\"false\",\"prepositionVersion\":\"v2\",\"client_os\":\"Android\",\"gpsEnabled\":\"false\",\"searchDoorFrom\":\"srp\",\"debug_rerankNewOpenCard\":\"false\",\"homePageVersion\":\"v7\",\"searchElderHomeOpen\":\"false\",\"search_action\":\"initiative\",\"sugg\":\"_4_1\",\"sversion\":\"13.6\",\"style\":\"list\",\"ttid\":\"600000@taobao_pc_10.7.0\",\"needTabs\":\"true\",\"areaCode\":\"CN\",\"vm\":\"nw\",\"countryNum\":\"156\",\"m\":\"pc\",\"page\":2,\"n\":48,\"q\":\"%E7%94%B5%E8%84%91%E6%95%B4%E6%9C%BA\",\"qSource\":\"url\",\"pageSource\":\"a21bo.jianhua/a.201867-main.d2_2.3de02a89OHEQWl\",\"channelSrp\":\"\",\"tab\":\"all\",\"pageSize\":\"48\",\"totalPage\":\"100\",\"totalResults\":\"8594\",\"sourceS\":\"0\",\"sort\":\"_coefp\",\"bcoffset\":\"-9\",\"ntoffset\":\"13\",\"filterTag\":\"\",\"service\":\"\",\"prop\":\"\",\"loc\":\"\",\"start_price\":null,\"end_price\":null,\"startPrice\":null,\"endPrice\":null,\"categoryp\":\"\",\"ha3Kvpairs\":null,\"myCNA\":\"LtAcIV67+VEBASQJikTHkLT5\",\"screenResolution\":\"1920x1080\",\"userAgent\":\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36\",\"couponUnikey\":\"\",\"subTabId\":\"\",\"np\":\"\",\"clientType\":\"h5\",\"isNewDomainAb\":\"false\",\"forceOldDomain\":\"false\"}"}
        # &bx-ua=231!tDD7CkmUlJE+jT6vd473fSBjUGg0uSOn+fYFmLQQwGng0wmHntUSK+2ttWIwYfiRlXeQ+thKJXIvfegh2cGUuRIvbZ9fhRfZbrcyCwJp1Tn/1O6FZpESbo3QzHthMFlyGdU66t9uKYMx15yS8pe+ytwIUGBsqq3t9V4iCQkjtEQbKDuzk6qVQDIOFb80WS6gTxiz4twEVZPYifp9zS9rqUtFQN41RRE3gDPUCv8XBPaCVKx40BMx3kop0Q3oyE+jauHhU0HIenHGHkE+++3+qCS4+ItuWAcuFmiNo+roPZkSLcdYjhOwCk4Sh8zMIdMap42U4vMMi8A1/1+2gy+0kvvdKZs6IZxJ8467eQOQXZK7xndNp6Eazv3GXJ2x+KkOBA+E13HPhkjHIyRvqUXaR3P/CM1xI3j+to5aa7je7ZYga2VnoExp9nLAdYzV/gnisX8s/MtNBVpJinBRaT2yWr/VnK/q/P43g2A9K9Kv5BwKUdEcvrd1BA1LPr6CK5287+i6URjESjMPWqCjuulCLka+7BWx0pIQSvyR/D0dbzfEgHEalxiu136VfkfYofU6oaeGxQz4241to/749JKTmu+dkTs4OAQYuy6oxBcvMJPjEvfLmqt7B2rnwl+dhyAQh+ZJEo1yRlhR7gafDKa+Phhnp50/Ud1/BKUxnzY6lqhtzmwqglPAxWYYm5cWeAme1Frv5rWI1VRItkBZJ4zKx60NWSMTnX5VQphg5fBx4zKG3Yp8CubYoDYeSOBuZV57EEEnVAb8Gw6/EgNmZNT4A6NJPscCkuxeqt8oD8YnOZK+1l4FUFhoaCeUPNEH83PWK78zhnmk1exSIL+7D3X5K9bxJNDSgOB2bnqoT3oerSr0aJPmNXnFBvgbfYm7sg7G00SIRlcokFWyKjr4tyBHeT0CDU/y8BrprpBkPQLSSmyJBG19M9d+kGtxYb5nzGS42+r+7avUw9FZhRSOtUUYK0HKBHSZ02RGSUaDDT0qLC1VDAPHtoztOsEyk91VHOaVrWXnPY/C5Zo3OsXaT4B+3FP3492rBved5SsusY1ee+wIMwDqYpilc2+t76BwopD49WPL3whp+C3eQYNs1easRdDdTnAV8neBUHPYrDAMNLjb2QdZng6scM+uCP+CBZUUpw7RjSVKw9I9fuvT738kK21Bkg/NL0kihSSQ8WO5HNOl6kWCHFq6KqTAUpPQPv4n8AP+p0RMQv5JbLiC/dqbOaKnKs4b7YjJRF4KIBHACBEUYLQLB9fw0+h36uYNRgG56MdvieC0FBJL0NADmHdezjxFz6uKSUMWAmXdJytfrGSXWSLkQ/FarwbADfuYzjD81PIgGEVczhemtjcDXYnH+9GkUb868smQl3B1U/EsihSQ8QH53el/n9TQDbHU36STbHTHezZ+PmxZ2+eC8JxoJqtmr6hCVk3Ooi0QJ+IYGzziqXfJu2CNbBQSDeEu2zLFwIwGp0vxxdgIfzg6yLhOmLoBVThOv0bhz+uWWDbk9hLEwmQmdtCoAl0sNJbVZFNZS2SyTXOtcjtkzB9MTbC1kdHJn8UyBX4S2TO/+OdZse+98x8ZGtmVmA1vyGqMuI9az3ckHmCiic5HRe09M/xO48pJ+enA6M14ZKDCHDj4cAGgVWWHm0rNGiNtxqRVJudgu4VxGZhkhTALYoiyy5SPQIbc0kMbcD5P6mpxmAum0zIQo9ZN0Io1cql/snh3zUv8SCJA2iJEBdCyMLtBPoSx7IoOqAXHulN55c1LeHwCAQEdAx/QnEXHEUfOeWWdefXRUz6eyq4BbAdN9UwhUEmaYpVK3vmz7dtrjpKlzQbKusoolR0XiLzUc2yvu5JgSO3Yeqv2bnmn/hRiO47aP2BPbd+3z0n1giwVsDSN87lTyV2d0uZ1jHAsYqK//IO28Sw5jmtzLsZ0AAhTTkN7JQoEG03PPViWbVHptDMezWS0Pptyy0jww1mTefWFxy2hRIEGgDZEawDOOEaRDQ7aUKcNvnwUjB4OoQVkUwceYDwaCT580cBTjP7juddOhlI5lNIjFka7fYL/
        # &bx-umidtoken=T2gAhpYHRqOwjgFUsTtAGw5bEGAizjgLwfycg6AzFu9ZjBI7R_BL5P451ku9rSf39KU=
        # &bx_et=gRAqhUTHrjh4tUZSG3CaYWPMx7CYB1uSAoR1SNY9WPjcii9PSht-WqCXSG-wVgFXhxB1bP5vNKN1cmCwSH1ZADGIOELAT1mIAe5FrHCh7oVgilZur1_Zg0M7VELA612MeEDykPkcWnNcSG0PZN7Lo1jGIg0P7wSGsiXgq8bhqGfMjt4lqN7TsN2cSb0PWgjGs1xGZ471qGfGshYoIeYDS77Cn4qlL3j49r32-Ejzs5Am6tjUAN7RlQ7V3MXkV5bWaZWVxERedU3lrQOPdTas4_YpFnbPTbwctUJMYpxtd8C2SKxOUnn8Ug9kFFjGEPVBzs9WAdXrojYPgiWFkTz_HsJMDCWv3P3prsxJpMBme0QyGB6NvTromUTPm9Jwc0FGcp8k49O7VW192dxG73qV4WrOrjXB6KrgQtbRzMgrzg7prdCeDYGbBRBl9aSIlZwTBtbRzMgrzReOEwQPAq_f.

    def taobaoApi0812(self):
        src = 'https://h5api.m.tmall.com/h5/mtop.taobao.pcdetail.data.get/1.0/?jsv=2.7.4&appKey=12574478&t=1754997307956&sign=af68297ff281901bf04ab1d7766532f3&api=mtop.taobao.pcdetail.data.get&v=1.0&isSec=0&ecode=0&timeout=10000&jsonpIncPrefix=pcdetail&ttid=2022%40taobao_litepc_9.17.0&AntiFlood=true&AntiCreep=true&type=jsonp&dataType=jsonp&callback=mtopjsonppcdetail1&data=%7B%22id%22%3A%22714940505378%22%2C%22detail_v%22%3A%223.3.2%22%2C%22mi_id%22%3A%22aU9o3cijLRozKvp35O7SozXaXuH9II6s9I_yEUUbnx5Wfx0MgERSO9R9q3lPY6AeKPshztpLcOhDjlKYPWfsH-GGTi4XOGMJ2bl2pDPgf-Y%22%2C%22exParams%22%3A%22%7B%5C%22detail_redpacket_pop%5C%22%3A%5C%22true%5C%22%2C%5C%22id%5C%22%3A%5C%22714940505378%5C%22%2C%5C%22ns%5C%22%3A%5C%221%5C%22%2C%5C%22priceTId%5C%22%3A%5C%22213e073417548333993975257e0f8a%5C%22%2C%5C%22query%5C%22%3A%5C%22%E7%94%B5%E8%84%91%E6%95%B4%E6%9C%BA%5C%22%2C%5C%22skuId%5C%22%3A%5C%225003028529635%5C%22%2C%5C%22spm%5C%22%3A%5C%22a21n57.1.hoverItem.2%5C%22%2C%5C%22utparam%5C%22%3A%5C%22%7B%5C%5C%5C%22aplus_abtest%5C%5C%5C%22%3A%5C%5C%5C%224fbac48dfe78d412d592e6879c095ae2%5C%5C%5C%22%7D%5C%22%2C%5C%22xxc%5C%22%3A%5C%22ad_ztc%5C%22%2C%5C%22queryParams%5C%22%3A%5C%22detail_redpacket_pop%3Dtrue%26id%3D714940505378%26ns%3D1%26priceTId%3D213e073417548333993975257e0f8a%26query%3D%25E7%2594%25B5%25E8%2584%2591%25E6%2595%25B4%25E6%259C%25BA%26skuId%3D5003028529635%26spm%3Da21n57.1.hoverItem.2%26utparam%3D%257B%2522aplus_abtest%2522%253A%25224fbac48dfe78d412d592e6879c095ae2%2522%257D%26xxc%3Dad_ztc%5C%22%2C%5C%22domain%5C%22%3A%5C%22https%3A%2F%2Fdetail.tmall.com%5C%22%2C%5C%22path_name%5C%22%3A%5C%22%2Fitem.htm%5C%22%2C%5C%22pcSource%5C%22%3A%5C%22pcTaobaoMain%5C%22%2C%5C%22refId%5C%22%3A%5C%22Q9x6xklt2xVUx2bjTB4OSMAb1TcZW8Uy0XgAZw2OkQQ%3D%5C%22%2C%5C%22nonce%5C%22%3A%5C%22DY57m0hycCrsTuEaz%2FvBuYMAvIFc6sjoJ0Kl55p06vg%3D%5C%22%2C%5C%22feTraceId%5C%22%3A%5C%2269a63257-a79e-468c-ba36-422dd4129be9%5C%22%7D%22%7D&bx-ua=fast-load'
        print(f'src: {self.unquote_str(src)}')
        base_src = "https://h5api.m.tmall.com/h5/mtop.taobao.pcdetail.data.get/1.0/?jsv=2.7.4&appKey=12574478&t=1754986711132&sign=c48a838ffd3a4b8ad2f7be13372383d0&api=mtop.taobao.pcdetail.data.get&v=1.0&isSec=0&ecode=0&timeout=10000&jsonpIncPrefix=pcdetail&ttid=2022%40taobao_litepc_9.17.0&AntiFlood=true&AntiCreep=true&type=jsonp&dataType=jsonp&callback=mtopjsonppcdetail3&data=%7B%22id%22%3A%22714940505378%22%2C%22detail_v%22%3A%223.3.2%22%2C%22mi_id%22%3A%22aU9o3cijLRozKvp35O7SozXaXuH9II6s9I_yEUUbnx5Wfx0MgERSO9R9q3lPY6AeKPshztpLcOhDjlKYPWfsH-GGTi4XOGMJ2bl2pDPgf-Y%22%2C%22exParams%22%3A%22%7B%5C%22detail_redpacket_pop%5C%22%3A%5C%22true%5C%22%2C%5C%22id%5C%22%3A%5C%22714940505378%5C%22%2C%5C%22ns%5C%22%3A%5C%221%5C%22%2C%5C%22priceTId%5C%22%3A%5C%22213e073417548333993975257e0f8a%5C%22%2C%5C%22query%5C%22%3A%5C%22%E7%94%B5%E8%84%91%E6%95%B4%E6%9C%BA%5C%22%2C%5C%22skuId%5C%22%3A%5C%225003028529635%5C%22%2C%5C%22spm%5C%22%3A%5C%22a21n57.1.hoverItem.2%5C%22%2C%5C%22utparam%5C%22%3A%5C%22%7B%5C%5C%5C%22aplus_abtest%5C%5C%5C%22%3A%5C%5C%5C%224fbac48dfe78d412d592e6879c095ae2%5C%5C%5C%22%7D%5C%22%2C%5C%22xxc%5C%22%3A%5C%22ad_ztc%5C%22%2C%5C%22queryParams%5C%22%3A%5C%22detail_redpacket_pop%3Dtrue%26id%3D714940505378%26ns%3D1%26priceTId%3D213e073417548333993975257e0f8a%26query%3D%25E7%2594%25B5%25E8%2584%2591%25E6%2595%25B4%25E6%259C%25BA%26skuId%3D5003028529635%26spm%3Da21n57.1.hoverItem.2%26utparam%3D%257B%2522aplus_abtest%2522%253A%25224fbac48dfe78d412d592e6879c095ae2%2522%257D%26xxc%3Dad_ztc%5C%22%2C%5C%22domain%5C%22%3A%5C%22https%3A%2F%2Fdetail.tmall.com%5C%22%2C%5C%22path_name%5C%22%3A%5C%22%2Fitem.htm%5C%22%2C%5C%22pcSource%5C%22%3A%5C%22pcTaobaoMain%5C%22%2C%5C%22refId%5C%22%3A%5C%22Q9x6xklt2xVUx2bjTB4OSMLoaQ6E%2B6JkuLP5Dybr9W4%3D%5C%22%2C%5C%22nonce%5C%22%3A%5C%220qiFY%2BDs9%2FlEpKkNGuqv0%2FgjU1GcNc8VSRYSmDVeAXY%3D%5C%22%2C%5C%22feTraceId%5C%22%3A%5C%22e7a02d78-5542-4604-b83b-f612c720f43a%5C%22%7D%22%7D&bx-ua=fast-load"
        print(f'base_src: {self.unquote_str(base_src)}')
        # src: https://h5api.m.tmall.com/h5/mtop.taobao.pcdetail.data.get/1.0/?jsv=2.7.4&appKey=12574478&t=1754994980199&sign=507218a0b86e416792c5874fca3bb810&api=mtop.taobao.pcdetail.data.get&v=1.0&isSec=0&ecode=0&timeout=10000&jsonpIncPrefix=pcdetail&ttid=2022@taobao_litepc_9.17.0&AntiFlood=true&AntiCreep=true&type=jsonp&dataType=jsonp&callback=mtopjsonppcdetail1&data={"id":"714940505378","detail_v":"3.3.2","mi_id":"aU9o3cijLRozKvp35O7SozXaXuH9II6s9I_yEUUbnx5Wfx0MgERSO9R9q3lPY6AeKPshztpLcOhDjlKYPWfsH-GGTi4XOGMJ2bl2pDPgf-Y","exParams":"{\"detail_redpacket_pop\":\"true\",\"id\":\"714940505378\",\"ns\":\"1\",\"priceTId\":\"213e073417548333993975257e0f8a\",\"query\":\"电脑整机\",\"skuId\":\"5003028529635\",\"spm\":\"a21n57.1.hoverItem.2\",\"utparam\":\"{\\\"aplus_abtest\\\":\\\"4fbac48dfe78d412d592e6879c095ae2\\\"}\",\"xxc\":\"ad_ztc\",\"queryParams\":\"detail_redpacket_pop=true&id=714940505378&ns=1&priceTId=213e073417548333993975257e0f8a&query=%E7%94%B5%E8%84%91%E6%95%B4%E6%9C%BA&skuId=5003028529635&spm=a21n57.1.hoverItem.2&utparam=%7B%22aplus_abtest%22%3A%224fbac48dfe78d412d592e6879c095ae2%22%7D&xxc=ad_ztc\",\"domain\":\"https://detail.tmall.com\",\"path_name\":\"/item.htm\",\"pcSource\":\"pcTaobaoMain\",\"refId\":\"Q9x6xklt2xVUx2bjTB4OSMAb1TcZW8Uy0XgAZw2OkQQ=\",\"nonce\":\"DY57m0hycCrsTuEaz/vBuYMAvIFc6sjoJ0Kl55p06vg=\",\"feTraceId\":\"523b5637-87c2-47fc-bc21-a924e20ed1ae\"}"}&bx-ua=fast-load
        # base:https://h5api.m.tmall.com/h5/mtop.taobao.pcdetail.data.get/1.0/?jsv=2.7.4&appKey=12574478&t=1754986711132&sign=c48a838ffd3a4b8ad2f7be13372383d0&api=mtop.taobao.pcdetail.data.get&v=1.0&isSec=0&ecode=0&timeout=10000&jsonpIncPrefix=pcdetail&ttid=2022@taobao_litepc_9.17.0&AntiFlood=true&AntiCreep=true&type=jsonp&dataType=jsonp&callback=mtopjsonppcdetail3&data={"id":"714940505378","detail_v":"3.3.2","mi_id":"aU9o3cijLRozKvp35O7SozXaXuH9II6s9I_yEUUbnx5Wfx0MgERSO9R9q3lPY6AeKPshztpLcOhDjlKYPWfsH-GGTi4XOGMJ2bl2pDPgf-Y","exParams":"{\"detail_redpacket_pop\":\"true\",\"id\":\"714940505378\",\"ns\":\"1\",\"priceTId\":\"213e073417548333993975257e0f8a\",\"query\":\"电脑整机\",\"skuId\":\"5003028529635\",\"spm\":\"a21n57.1.hoverItem.2\",\"utparam\":\"{\\\"aplus_abtest\\\":\\\"4fbac48dfe78d412d592e6879c095ae2\\\"}\",\"xxc\":\"ad_ztc\",\"queryParams\":\"detail_redpacket_pop=true&id=714940505378&ns=1&priceTId=213e073417548333993975257e0f8a&query=%E7%94%B5%E8%84%91%E6%95%B4%E6%9C%BA&skuId=5003028529635&spm=a21n57.1.hoverItem.2&utparam=%7B%22aplus_abtest%22%3A%224fbac48dfe78d412d592e6879c095ae2%22%7D&xxc=ad_ztc\",\"domain\":\"https://detail.tmall.com\",\"path_name\":\"/item.htm\",\"pcSource\":\"pcTaobaoMain\",\"refId\":\"Q9x6xklt2xVUx2bjTB4OSMLoaQ6E+6JkuLP5Dybr9W4=\",\"nonce\":\"0qiFY+Ds9/lEpKkNGuqv0/gjU1GcNc8VSRYSmDVeAXY=\",\"feTraceId\":\"e7a02d78-5542-4604-b83b-f612c720f43a\"}"}&bx-ua=fast-load

        # brosewer
        # https://h5api.m.tmall.com/h5/mtop.taobao.pcdetail.data.get/1.0/?jsv=2.7.4&appKey=12574478&t=1754997307956&sign=af68297ff281901bf04ab1d7766532f3&api=mtop.taobao.pcdetail.data.get&v=1.0&isSec=0&ecode=0&timeout=10000&jsonpIncPrefix=pcdetail&ttid=2022%40taobao_litepc_9.17.0&AntiFlood=true&AntiCreep=true&type=jsonp&dataType=jsonp&callback=mtopjsonppcdetail1&data=%7B%22id%22%3A%22714940505378%22%2C%22detail_v%22%3A%223.3.2%22%2C%22mi_id%22%3A%22aU9o3cijLRozKvp35O7SozXaXuH9II6s9I_yEUUbnx5Wfx0MgERSO9R9q3lPY6AeKPshztpLcOhDjlKYPWfsH-GGTi4XOGMJ2bl2pDPgf-Y%22%2C%22exParams%22%3A%22%7B%5C%22detail_redpacket_pop%5C%22%3A%5C%22true%5C%22%2C%5C%22id%5C%22%3A%5C%22714940505378%5C%22%2C%5C%22ns%5C%22%3A%5C%221%5C%22%2C%5C%22priceTId%5C%22%3A%5C%22213e073417548333993975257e0f8a%5C%22%2C%5C%22query%5C%22%3A%5C%22%E7%94%B5%E8%84%91%E6%95%B4%E6%9C%BA%5C%22%2C%5C%22skuId%5C%22%3A%5C%225003028529635%5C%22%2C%5C%22spm%5C%22%3A%5C%22a21n57.1.hoverItem.2%5C%22%2C%5C%22utparam%5C%22%3A%5C%22%7B%5C%5C%5C%22aplus_abtest%5C%5C%5C%22%3A%5C%5C%5C%224fbac48dfe78d412d592e6879c095ae2%5C%5C%5C%22%7D%5C%22%2C%5C%22xxc%5C%22%3A%5C%22ad_ztc%5C%22%2C%5C%22queryParams%5C%22%3A%5C%22detail_redpacket_pop%3Dtrue%26id%3D714940505378%26ns%3D1%26priceTId%3D213e073417548333993975257e0f8a%26query%3D%25E7%2594%25B5%25E8%2584%2591%25E6%2595%25B4%25E6%259C%25BA%26skuId%3D5003028529635%26spm%3Da21n57.1.hoverItem.2%26utparam%3D%257B%2522aplus_abtest%2522%253A%25224fbac48dfe78d412d592e6879c095ae2%2522%257D%26xxc%3Dad_ztc%5C%22%2C%5C%22domain%5C%22%3A%5C%22https%3A%2F%2Fdetail.tmall.com%5C%22%2C%5C%22path_name%5C%22%3A%5C%22%2Fitem.htm%5C%22%2C%5C%22pcSource%5C%22%3A%5C%22pcTaobaoMain%5C%22%2C%5C%22refId%5C%22%3A%5C%22Q9x6xklt2xVUx2bjTB4OSMAb1TcZW8Uy0XgAZw2OkQQ%3D%5C%22%2C%5C%22nonce%5C%22%3A%5C%22DY57m0hycCrsTuEaz%2FvBuYMAvIFc6sjoJ0Kl55p06vg%3D%5C%22%2C%5C%22feTraceId%5C%22%3A%5C%2269a63257-a79e-468c-ba36-422dd4129be9%5C%22%7D%22%7D&bx-ua=fast-load
        # https://h5api.m.tmall.com/h5/mtop.taobao.pcdetail.data.get/1.0/?jsv=2.7.4&appKey=12574478&t=1754996021755&sign=83847f10f5df46b1758260bbdc45d62f&api=mtop.taobao.pcdetail.data.get&v=1.0&isSec=0&ecode=0&timeout=10000&jsonpIncPrefix=pcdetail&ttid=2022%40taobao_litepc_9.17.0&AntiFlood=true&AntiCreep=true&type=jsonp&dataType=jsonp&callback=mtopjsonppcdetail3&data=%7B%22id%22%3A%22714940505378%22%2C%22detail_v%22%3A%223.3.2%22%2C%22mi_id%22%3A%22aU9o3cijLRozKvp35O7SozXaXuH9II6s9I_yEUUbnx5Wfx0MgERSO9R9q3lPY6AeKPshztpLcOhDjlKYPWfsH-GGTi4XOGMJ2bl2pDPgf-Y%22%2C%22exParams%22%3A%22%7B%5C%22detail_redpacket_pop%5C%22%3A%5C%22true%5C%22%2C%5C%22id%5C%22%3A%5C%22714940505378%5C%22%2C%5C%22ns%5C%22%3A%5C%221%5C%22%2C%5C%22priceTId%5C%22%3A%5C%22213e073417548333993975257e0f8a%5C%22%2C%5C%22query%5C%22%3A%5C%22%E7%94%B5%E8%84%91%E6%95%B4%E6%9C%BA%5C%22%2C%5C%22skuId%5C%22%3A%5C%225003028529635%5C%22%2C%5C%22spm%5C%22%3A%5C%22a21n57.1.hoverItem.2%5C%22%2C%5C%22utparam%5C%22%3A%5C%22%7B%5C%5C%5C%22aplus_abtest%5C%5C%5C%22%3A%5C%5C%5C%224fbac48dfe78d412d592e6879c095ae2%5C%5C%5C%22%7D%5C%22%2C%5C%22xxc%5C%22%3A%5C%22ad_ztc%5C%22%2C%5C%22queryParams%5C%22%3A%5C%22detail_redpacket_pop%3Dtrue%26id%3D714940505378%26ns%3D1%26priceTId%3D213e073417548333993975257e0f8a%26query%3D%25E7%2594%25B5%25E8%2584%2591%25E6%2595%25B4%25E6%259C%25BA%26skuId%3D5003028529635%26spm%3Da21n57.1.hoverItem.2%26utparam%3D%257B%2522aplus_abtest%2522%253A%25224fbac48dfe78d412d592e6879c095ae2%2522%257D%26xxc%3Dad_ztc%5C%22%2C%5C%22domain%5C%22%3A%5C%22https%3A%2F%2Fdetail.tmall.com%5C%22%2C%5C%22path_name%5C%22%3A%5C%22%2Fitem.htm%5C%22%2C%5C%22pcSource%5C%22%3A%5C%22pcTaobaoMain%5C%22%2C%5C%22refId%5C%22%3A%5C%22Q9x6xklt2xVUx2bjTB4OSGUqjFSBoVaVLS55qwFxAmA%3D%5C%22%2C%5C%22nonce%5C%22%3A%5C%22EB7kPRgYty7okdSRq%2BS0nchVqppsS5YZo3mbO6Ndp9o%3D%5C%22%2C%5C%22feTraceId%5C%22%3A%5C%223c8f5e1c-c6da-499b-a838-61f47e41d58b%5C%22%7D%22%7D

    def taobaoApi0810(self):
        # 商品
        # https://h5api.m.taobao.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/?jsv=2.7.4&appKey=12574478&t=1754833399373&sign=59b949a15b61b6f8d72fbe368181ce18&api=mtop.relationrecommend.wirelessrecommend.recommend&v=2.0&timeout=10000&type=jsonp&dataType=jsonp&callback=mtopjsonp5&data=%7B%22appId%22%3A%2234385%22%2C%22params%22%3A%22%7B%5C%22device%5C%22%3A%5C%22HMA-AL00%5C%22%2C%5C%22isBeta%5C%22%3A%5C%22false%5C%22%2C%5C%22grayHair%5C%22%3A%5C%22false%5C%22%2C%5C%22from%5C%22%3A%5C%22nt_history%5C%22%2C%5C%22brand%5C%22%3A%5C%22HUAWEI%5C%22%2C%5C%22info%5C%22%3A%5C%22wifi%5C%22%2C%5C%22index%5C%22%3A%5C%224%5C%22%2C%5C%22rainbow%5C%22%3A%5C%22%5C%22%2C%5C%22schemaType%5C%22%3A%5C%22auction%5C%22%2C%5C%22elderHome%5C%22%3A%5C%22false%5C%22%2C%5C%22isEnterSrpSearch%5C%22%3A%5C%22true%5C%22%2C%5C%22newSearch%5C%22%3A%5C%22false%5C%22%2C%5C%22network%5C%22%3A%5C%22wifi%5C%22%2C%5C%22subtype%5C%22%3A%5C%22%5C%22%2C%5C%22hasPreposeFilter%5C%22%3A%5C%22false%5C%22%2C%5C%22prepositionVersion%5C%22%3A%5C%22v2%5C%22%2C%5C%22client_os%5C%22%3A%5C%22Android%5C%22%2C%5C%22gpsEnabled%5C%22%3A%5C%22false%5C%22%2C%5C%22searchDoorFrom%5C%22%3A%5C%22srp%5C%22%2C%5C%22debug_rerankNewOpenCard%5C%22%3A%5C%22false%5C%22%2C%5C%22homePageVersion%5C%22%3A%5C%22v7%5C%22%2C%5C%22searchElderHomeOpen%5C%22%3A%5C%22false%5C%22%2C%5C%22search_action%5C%22%3A%5C%22initiative%5C%22%2C%5C%22sugg%5C%22%3A%5C%22_4_1%5C%22%2C%5C%22sversion%5C%22%3A%5C%2213.6%5C%22%2C%5C%22style%5C%22%3A%5C%22list%5C%22%2C%5C%22ttid%5C%22%3A%5C%22600000%40taobao_pc_10.7.0%5C%22%2C%5C%22needTabs%5C%22%3A%5C%22true%5C%22%2C%5C%22areaCode%5C%22%3A%5C%22CN%5C%22%2C%5C%22vm%5C%22%3A%5C%22nw%5C%22%2C%5C%22countryNum%5C%22%3A%5C%22156%5C%22%2C%5C%22m%5C%22%3A%5C%22pc%5C%22%2C%5C%22page%5C%22%3A1%2C%5C%22n%5C%22%3A48%2C%5C%22q%5C%22%3A%5C%22%25E7%2594%25B5%25E8%2584%2591%25E6%2595%25B4%25E6%259C%25BA%5C%22%2C%5C%22qSource%5C%22%3A%5C%22url%5C%22%2C%5C%22pageSource%5C%22%3A%5C%22a21bo.jianhua%2Fa.201867-main.d2_2.3de02a89OHEQWl%5C%22%2C%5C%22channelSrp%5C%22%3A%5C%22%5C%22%2C%5C%22tab%5C%22%3A%5C%22all%5C%22%2C%5C%22pageSize%5C%22%3A48%2C%5C%22totalPage%5C%22%3A100%2C%5C%22totalResults%5C%22%3A4800%2C%5C%22sourceS%5C%22%3A%5C%220%5C%22%2C%5C%22sort%5C%22%3A%5C%22_coefp%5C%22%2C%5C%22bcoffset%5C%22%3A%5C%22%5C%22%2C%5C%22ntoffset%5C%22%3A%5C%22%5C%22%2C%5C%22filterTag%5C%22%3A%5C%22%5C%22%2C%5C%22service%5C%22%3A%5C%22%5C%22%2C%5C%22prop%5C%22%3A%5C%22%5C%22%2C%5C%22loc%5C%22%3A%5C%22%5C%22%2C%5C%22start_price%5C%22%3Anull%2C%5C%22end_price%5C%22%3Anull%2C%5C%22startPrice%5C%22%3Anull%2C%5C%22endPrice%5C%22%3Anull%2C%5C%22itemIds%5C%22%3Anull%2C%5C%22p4pIds%5C%22%3Anull%2C%5C%22p4pS%5C%22%3Anull%2C%5C%22categoryp%5C%22%3A%5C%22%5C%22%2C%5C%22ha3Kvpairs%5C%22%3Anull%2C%5C%22myCNA%5C%22%3A%5C%22LtAcIV67%2BVEBASQJikTHkLT5%5C%22%2C%5C%22screenResolution%5C%22%3A%5C%221920x1080%5C%22%2C%5C%22userAgent%5C%22%3A%5C%22Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F139.0.0.0%20Safari%2F537.36%5C%22%2C%5C%22couponUnikey%5C%22%3A%5C%22%5C%22%2C%5C%22subTabId%5C%22%3A%5C%22%5C%22%2C%5C%22np%5C%22%3A%5C%22%5C%22%2C%5C%22clientType%5C%22%3A%5C%22h5%5C%22%2C%5C%22isNewDomainAb%5C%22%3A%5C%22false%5C%22%2C%5C%22forceOldDomain%5C%22%3A%5C%22false%5C%22%7D%22%7D&bx-ua=fast-load
        product_list = 'https://h5api.m.taobao.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/?jsv=2.7.4&appKey=12574478&t=1754833399373&sign=59b949a15b61b6f8d72fbe368181ce18&api=mtop.relationrecommend.wirelessrecommend.recommend&v=2.0&timeout=10000&type=jsonp&dataType=jsonp&callback=mtopjsonp5&data=%7B%22appId%22%3A%2234385%22%2C%22params%22%3A%22%7B%5C%22device%5C%22%3A%5C%22HMA-AL00%5C%22%2C%5C%22isBeta%5C%22%3A%5C%22false%5C%22%2C%5C%22grayHair%5C%22%3A%5C%22false%5C%22%2C%5C%22from%5C%22%3A%5C%22nt_history%5C%22%2C%5C%22brand%5C%22%3A%5C%22HUAWEI%5C%22%2C%5C%22info%5C%22%3A%5C%22wifi%5C%22%2C%5C%22index%5C%22%3A%5C%224%5C%22%2C%5C%22rainbow%5C%22%3A%5C%22%5C%22%2C%5C%22schemaType%5C%22%3A%5C%22auction%5C%22%2C%5C%22elderHome%5C%22%3A%5C%22false%5C%22%2C%5C%22isEnterSrpSearch%5C%22%3A%5C%22true%5C%22%2C%5C%22newSearch%5C%22%3A%5C%22false%5C%22%2C%5C%22network%5C%22%3A%5C%22wifi%5C%22%2C%5C%22subtype%5C%22%3A%5C%22%5C%22%2C%5C%22hasPreposeFilter%5C%22%3A%5C%22false%5C%22%2C%5C%22prepositionVersion%5C%22%3A%5C%22v2%5C%22%2C%5C%22client_os%5C%22%3A%5C%22Android%5C%22%2C%5C%22gpsEnabled%5C%22%3A%5C%22false%5C%22%2C%5C%22searchDoorFrom%5C%22%3A%5C%22srp%5C%22%2C%5C%22debug_rerankNewOpenCard%5C%22%3A%5C%22false%5C%22%2C%5C%22homePageVersion%5C%22%3A%5C%22v7%5C%22%2C%5C%22searchElderHomeOpen%5C%22%3A%5C%22false%5C%22%2C%5C%22search_action%5C%22%3A%5C%22initiative%5C%22%2C%5C%22sugg%5C%22%3A%5C%22_4_1%5C%22%2C%5C%22sversion%5C%22%3A%5C%2213.6%5C%22%2C%5C%22style%5C%22%3A%5C%22list%5C%22%2C%5C%22ttid%5C%22%3A%5C%22600000%40taobao_pc_10.7.0%5C%22%2C%5C%22needTabs%5C%22%3A%5C%22true%5C%22%2C%5C%22areaCode%5C%22%3A%5C%22CN%5C%22%2C%5C%22vm%5C%22%3A%5C%22nw%5C%22%2C%5C%22countryNum%5C%22%3A%5C%22156%5C%22%2C%5C%22m%5C%22%3A%5C%22pc%5C%22%2C%5C%22page%5C%22%3A1%2C%5C%22n%5C%22%3A48%2C%5C%22q%5C%22%3A%5C%22%25E7%2594%25B5%25E8%2584%2591%25E6%2595%25B4%25E6%259C%25BA%5C%22%2C%5C%22qSource%5C%22%3A%5C%22url%5C%22%2C%5C%22pageSource%5C%22%3A%5C%22a21bo.jianhua%2Fa.201867-main.d2_2.3de02a89OHEQWl%5C%22%2C%5C%22channelSrp%5C%22%3A%5C%22%5C%22%2C%5C%22tab%5C%22%3A%5C%22all%5C%22%2C%5C%22pageSize%5C%22%3A48%2C%5C%22totalPage%5C%22%3A100%2C%5C%22totalResults%5C%22%3A4800%2C%5C%22sourceS%5C%22%3A%5C%220%5C%22%2C%5C%22sort%5C%22%3A%5C%22_coefp%5C%22%2C%5C%22bcoffset%5C%22%3A%5C%22%5C%22%2C%5C%22ntoffset%5C%22%3A%5C%22%5C%22%2C%5C%22filterTag%5C%22%3A%5C%22%5C%22%2C%5C%22service%5C%22%3A%5C%22%5C%22%2C%5C%22prop%5C%22%3A%5C%22%5C%22%2C%5C%22loc%5C%22%3A%5C%22%5C%22%2C%5C%22start_price%5C%22%3Anull%2C%5C%22end_price%5C%22%3Anull%2C%5C%22startPrice%5C%22%3Anull%2C%5C%22endPrice%5C%22%3Anull%2C%5C%22itemIds%5C%22%3Anull%2C%5C%22p4pIds%5C%22%3Anull%2C%5C%22p4pS%5C%22%3Anull%2C%5C%22categoryp%5C%22%3A%5C%22%5C%22%2C%5C%22ha3Kvpairs%5C%22%3Anull%2C%5C%22myCNA%5C%22%3A%5C%22LtAcIV67%2BVEBASQJikTHkLT5%5C%22%2C%5C%22screenResolution%5C%22%3A%5C%221920x1080%5C%22%2C%5C%22userAgent%5C%22%3A%5C%22Mozilla%2F5.0%20(Windows%20NT%2010.0%3B%20Win64%3B%20x64)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F139.0.0.0%20Safari%2F537.36%5C%22%2C%5C%22couponUnikey%5C%22%3A%5C%22%5C%22%2C%5C%22subTabId%5C%22%3A%5C%22%5C%22%2C%5C%22np%5C%22%3A%5C%22%5C%22%2C%5C%22clientType%5C%22%3A%5C%22h5%5C%22%2C%5C%22isNewDomainAb%5C%22%3A%5C%22false%5C%22%2C%5C%22forceOldDomain%5C%22%3A%5C%22false%5C%22%7D%22%7D&bx-ua=fast-load'
        # https://h5api.m.taobao.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/
        # ?jsv=2.7.4
        # &appKey=12574478
        # &t=1754833399373
        # &sign=59b949a15b61b6f8d72fbe368181ce18
        # &api=mtop.relationrecommend.wirelessrecommend.recommend
        # &v=2.0
        # &timeout=10000
        # &type=jsonp
        # &dataType=jsonp
        # &callback=mtopjsonp5
        # &data={
        #   "appId":"34385"
        #   ,"params":"{
        #       \"device\":\"HMA-AL00\"
        #       ,\"isBeta\":\"false\"
        #       ,\"grayHair\":\"false\"
        #       ,\"from\":\"nt_history\"
        #       ,\"brand\":\"HUAWEI\"
        #       ,\"info\":\"wifi\"
        #       ,\"index\":\"4\"
        #       ,\"rainbow\":\"\"
        #       ,\"schemaType\":\"auction\"
        #       ,\"elderHome\":\"false\"
        #       ,\"isEnterSrpSearch\":\"true\"
        #       ,\"newSearch\":\"false\"
        #       ,\"network\":\"wifi\"
        #       ,\"subtype\":\"\"
        #       ,\"hasPreposeFilter\":\"false\"
        #       ,\"prepositionVersion\":\"v2\"
        #       ,\"client_os\":\"Android\"
        #       ,\"gpsEnabled\":\"false\"
        #       ,\"searchDoorFrom\":\"srp\"
        #       ,\"debug_rerankNewOpenCard\":\"false\"
        #       ,\"homePageVersion\":\"v7\"
        #       ,\"searchElderHomeOpen\":\"false\"
        #       ,\"search_action\":\"initiative\"
        #       ,\"sugg\":\"_4_1\"
        #       ,\"sversion\":\"13.6\"
        #       ,\"style\":\"list\"
        #       ,\"ttid\":\"600000@taobao_pc_10.7.0\"
        #       ,\"needTabs\":\"true\"
        #       ,\"areaCode\":\"CN\"
        #       ,\"vm\":\"nw\"
        #       ,\"countryNum\":\"156\"
        #       ,\"m\":\"pc\"
        #       ,\"page\":1
        #       ,\"n\":48
        #       ,\"q\":\"%E7%94%B5%E8%84%91%E6%95%B4%E6%9C%BA\"
        #       ,\"qSource\":\"url\"
        #       ,\"pageSource\":\"a21bo.jianhua/a.201867-main.d2_2.3de02a89OHEQWl\"
        #       ,\"channelSrp\":\"\"
        #       ,\"tab\":\"all\"
        #       ,\"pageSize\":48
        #       ,\"totalPage\":100
        #       ,\"totalResults\":4800
        #       ,\"sourceS\":\"0\"
        #       ,\"sort\":\"_coefp\"
        #       ,\"bcoffset\":\"\"
        #       ,\"ntoffset\":\"\"
        #       ,\"filterTag\":\"\"
        #       ,\"service\":\"\"
        #       ,\"prop\":\"\"
        #       ,\"loc\":\"\"
        #       ,\"start_price\":null
        #       ,\"end_price\":null
        #       ,\"startPrice\":null
        #       ,\"endPrice\":null
        #       ,\"itemIds\":null
        #       ,\"p4pIds\":null
        #       ,\"p4pS\":null
        #       ,\"categoryp\":\"\"
        #       ,\"ha3Kvpairs\":null
        #       ,\"myCNA\":\"LtAcIV67+VEBASQJikTHkLT5\"
        #       ,\"screenResolution\":\"1920x1080\"
        #       ,\"userAgent\":\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36\"
        #       ,\"couponUnikey\":\"\"
        #       ,\"subTabId\":\"\"
        #       ,\"np\":\"\"
        #       ,\"clientType\":\"h5\"
        #       ,\"isNewDomainAb\":\"false\"
        #       ,\"forceOldDomain\":\"false\"
        #     }"
        #    }
        #    &bx-ua=fast-load
        print(f'product_list: {self.unquote_str(product_list)}')

        product_url = "https://detail.tmall.com/item.htm?id=891426830722&ltk2=1754669175987t72suv6xkhmb70y1kx30m&spm=a21bo.jianhua%2Fa.201876.d2.64d42a89JLlOqv&utparam=%7B%22item_ctr%22%3A0.012033%2C%22x_object_type%22%3A%22p4p_item%22%2C%22item_price%22%3A%2235.02%22%2C%22item_cvr%22%3A0.015806%2C%22pc_scene%22%3A%2220001%22%2C%22aplus_abtest%22%3A%22494b17b967b0e942e5a21d8d74ed97ba%22%2C%22tpp_buckets%22%3A%2230986%23449124%230_30986%23520373%2357062_30986%23521580%2357267%22%2C%22ab_info%22%3A%2230986%23449124%230_30986%23520373%2357062_30986%23521580%2357267%22%2C%22abid%22%3A%22520373_521580%22%2C%22pc_pvid%22%3A%2272e64092-b1cf-4cd3-a731-808c402e759e%22%2C%22mix_group%22%3A%22%22%2C%22item_ecpm%22%3A0.00373%2C%22x_object_id%22%3A891426830722%7D&xxc=ad_ct"
        print(f'product_url: {self.unquote_str(product_url)}')
        #              https://detail.tmall.com/item.htm
        #                ?id=891426830722
        #                &ltk2=1754669175987t72suv6xkhmb70y1kx30m
        #                &spm=a21bo.jianhua/a.201876.d2.64d42a89JLlOqv
        #                &utparam={
        #                   "item_ctr":0.012033
        #                   ,"x_object_type":"p4p_item"
        #                   ,"item_price":"35.02"
        #                   ,"item_cvr":0.015806
        #                   ,"pc_scene":"20001"
        #                   ,"aplus_abtest":"494b17b967b0e942e5a21d8d74ed97ba"
        #                   ,"tpp_buckets":"30986#449124#0_30986#520373#57062_30986#521580#57267"
        #                   ,"ab_info":"30986#449124#0_30986#520373#57062_30986#521580#57267"
        #                   ,"abid":"520373_521580"
        #                   ,"pc_pvid":"72e64092-b1cf-4cd3-a731-808c402e759e"
        #                   ,"mix_group":""
        #                   ,"item_ecpm":0.00373
        #                   ,"x_object_id":891426830722}
        #                &xxc=ad_ct

        activate_rul = "https://h5api.m.tmall.com/h5/mtop.taobao.pcdetail.data.get/1.0/?jsv=2.7.4&appKey=12574478&t=1754705354067&sign=9ccae504a69e8e7e5786bfc6da4b3197&api=mtop.taobao.pcdetail.data.get&v=1.0&isSec=0&ecode=0&timeout=10000&jsonpIncPrefix=pcdetail&ttid=2022%40taobao_litepc_9.17.0&AntiFlood=true&AntiCreep=true&type=jsonp&dataType=jsonp&callback=mtopjsonppcdetail4&data=%7B%22id%22%3A%22891426830722%22%2C%22detail_v%22%3A%223.3.2%22%2C%22exParams%22%3A%22%7B%5C%22id%5C%22%3A%5C%22891426830722%5C%22%2C%5C%22skuId%5C%22%3A%5C%225737637236744%5C%22%2C%5C%22spm%5C%22%3A%5C%22a21bo.jianhua%2Fa.201876.d2.64d42a89JLlOqv%5C%22%2C%5C%22utparam%5C%22%3A%5C%22%7B%5C%5C%5C%22item_ctr%5C%5C%5C%22%3A0.012033%2C%5C%5C%5C%22x_object_type%5C%5C%5C%22%3A%5C%5C%5C%22p4p_item%5C%5C%5C%22%2C%5C%5C%5C%22item_price%5C%5C%5C%22%3A%5C%5C%5C%2235.02%5C%5C%5C%22%2C%5C%5C%5C%22item_cvr%5C%5C%5C%22%3A0.015806%2C%5C%5C%5C%22pc_scene%5C%5C%5C%22%3A%5C%5C%5C%2220001%5C%5C%5C%22%2C%5C%5C%5C%22aplus_abtest%5C%5C%5C%22%3A%5C%5C%5C%22494b17b967b0e942e5a21d8d74ed97ba%5C%5C%5C%22%2C%5C%5C%5C%22tpp_buckets%5C%5C%5C%22%3A%5C%5C%5C%2230986%23449124%230_30986%23520373%2357062_30986%23521580%2357267%5C%5C%5C%22%2C%5C%5C%5C%22ab_info%5C%5C%5C%22%3A%5C%5C%5C%2230986%23449124%230_30986%23520373%2357062_30986%23521580%2357267%5C%5C%5C%22%2C%5C%5C%5C%22abid%5C%5C%5C%22%3A%5C%5C%5C%22520373_521580%5C%5C%5C%22%2C%5C%5C%5C%22pc_pvid%5C%5C%5C%22%3A%5C%5C%5C%2272e64092-b1cf-4cd3-a731-808c402e759e%5C%5C%5C%22%2C%5C%5C%5C%22mix_group%5C%5C%5C%22%3A%5C%5C%5C%22%5C%5C%5C%22%2C%5C%5C%5C%22item_ecpm%5C%5C%5C%22%3A0.00373%2C%5C%5C%5C%22x_object_id%5C%5C%5C%22%3A891426830722%7D%5C%22%2C%5C%22xxc%5C%22%3A%5C%22ad_ct%5C%22%2C%5C%22queryParams%5C%22%3A%5C%22id%3D891426830722%26ltk2%3D1754669175987t72suv6xkhmb70y1kx30m%26skuId%3D5737637236744%26spm%3Da21bo.jianhua%252Fa.201876.d2.64d42a89JLlOqv%26utparam%3D%257B%2522item_ctr%2522%253A0.012033%252C%2522x_object_type%2522%253A%2522p4p_item%2522%252C%2522item_price%2522%253A%252235.02%2522%252C%2522item_cvr%2522%253A0.015806%252C%2522pc_scene%2522%253A%252220001%2522%252C%2522aplus_abtest%2522%253A%2522494b17b967b0e942e5a21d8d74ed97ba%2522%252C%2522tpp_buckets%2522%253A%252230986%2523449124%25230_30986%2523520373%252357062_30986%2523521580%252357267%2522%252C%2522ab_info%2522%253A%252230986%2523449124%25230_30986%2523520373%252357062_30986%2523521580%252357267%2522%252C%2522abid%2522%253A%2522520373_521580%2522%252C%2522pc_pvid%2522%253A%252272e64092-b1cf-4cd3-a731-808c402e759e%2522%252C%2522mix_group%2522%253A%2522%2522%252C%2522item_ecpm%2522%253A0.00373%252C%2522x_object_id%2522%253A891426830722%257D%26xxc%3Dad_ct%5C%22%2C%5C%22domain%5C%22%3A%5C%22https%3A%2F%2Fdetail.tmall.com%5C%22%2C%5C%22path_name%5C%22%3A%5C%22%2Fitem.htm%5C%22%2C%5C%22pcSource%5C%22%3A%5C%22pcTaobaoMain%5C%22%2C%5C%22refId%5C%22%3A%5C%22Xkf%2BUSBleCxwfdeuVjSGRgoJulrHlXaQ4xJ4VMgr74c%3D%5C%22%2C%5C%22nonce%5C%22%3A%5C%22O65vCqFfLUSHaHpvCOHLqw%3D%3D%5C%22%2C%5C%22feTraceId%5C%22%3A%5C%2264783313-c5ae-4694-8021-001f4962dbd7%5C%22%7D%22%7D&bx-umidtoken=defaultFY2_load_failed%20with%20timeout%40%40https%3A%2F%2Fdetail.tmall.com%2Fitem.htm%40%401754705354068&x-pipu2=default_not_fun&bx-ua=fast-load"
        print(f'activate_rul: {self.unquote_str(activate_rul)}')
        # :             https://h5api.m.tmall.com/h5/mtop.taobao.pcdetail.data.get/1.0/
        #                    ?jsv=2.7.4                                  FF
        #                    &appKey=12574478                            FF
        #                    &t=1754705354067                            B
        #                    &sign=9ccae504a69e8e7e5786bfc6da4b3197      FF
        #                    &api=mtop.taobao.pcdetail.data.get          G
        #                    &v=1.0                                      F
        #                    &isSec=0                                    F
        #                    &ecode=0                                    F
        #                    &timeout=10000                              G F
        #                    &jsonpIncPrefix=pcdetail                    F
        #                    &ttid=2022@taobao_litepc_9.17.0             G F
        #                    &AntiFlood=true                             G F
        #                    &AntiCreep=true                             G F
        #                    &type=jsonp                                 X
        #                    &dataType=jsonp                             F
        #                    &callback=mtopjsonppcdetail4                G
        #                    &data={
        #                       "id":"891426830722"                      G F
        #                       ,"detail_v":"3.3.2"                      G F
        #                       ,"exParams":"{
        #                           \"id\":\"891426830722\"
        #                           ,\"skuId\":\"5737637236744\"
        #                           ,\"spm\":\"a21bo.jianhua/a.201876.d2.64d42a89JLlOqv\"
        #                           ,\"utparam\":\"{\\\"item_ctr\\\":0.012033                                           Product URL utparam
        #                           ,\\\"x_object_type\\\":\\\"p4p_item\\\"
        #                           ,\\\"item_price\\\":\\\"35.02\\\"
        #                           ,\\\"item_cvr\\\":0.015806
        #                           ,\\\"pc_scene\\\":\\\"20001\\\"
        #                           ,\\\"aplus_abtest\\\":\\\"494b17b967b0e942e5a21d8d74ed97ba\\\"
        #                           ,\\\"tpp_buckets\\\":\\\"30986#449124#0_30986#520373#57062_30986#521580#57267\\\"
        #                           ,\\\"ab_info\\\":\\\"30986#449124#0_30986#520373#57062_30986#521580#57267\\\"
        #                           ,\\\"abid\\\":\\\"520373_521580\\\"
        #                           ,\\\"pc_pvid\\\":\\\"72e64092-b1cf-4cd3-a731-808c402e759e\\\"
        #                           ,\\\"mix_group\\\":\\\"\\\"
        #                           ,\\\"item_ecpm\\\":0.00373
        #                           ,\\\"x_object_id\\\":891426830722}\"
        #                           ,\"xxc\":\"ad_ct\"
        #                           ,\"queryParams\":\                          ProductUrl param  F
        #                               "id=891426830722
        #                               &ltk2=1754669175987t72suv6xkhmb70y1kx30m
        #                               &skuId=5737637236744
        #                               &spm=a21bo.jianhua%2Fa.201876.d2.64d42a89JLlOqv
        #                               &utparam=%7B%22item_ctr%22%3A0.012033%2C%22x_object_type%22%3A%22p4p_item%22%2C%22item_price%22%3A%2235.02%22%2C%22item_cvr%22%3A0.015806%2C%22pc_scene%22%3A%2220001%22%2C%22aplus_abtest%22%3A%22494b17b967b0e942e5a21d8d74ed97ba%22%2C%22tpp_buckets%22%3A%2230986%23449124%230_30986%23520373%2357062_30986%23521580%2357267%22%2C%22ab_info%22%3A%2230986%23449124%230_30986%23520373%2357062_30986%23521580%2357267%22%2C%22abid%22%3A%22520373_521580%22%2C%22pc_pvid%22%3A%2272e64092-b1cf-4cd3-a731-808c402e759e%22%2C%22mix_group%22%3A%22%22%2C%22item_ecpm%22%3A0.00373%2C%22x_object_id%22%3A891426830722%7D
        #                               &xxc=ad_ct\"
        #                           ,\"domain\":\"https://detail.tmall.com\"                     F
        #                           ,\"path_name\":\"/item.htm\"                                 F
        #                           ,\"pcSource\":\"pcTaobaoMain\"                               F
        #                           ,\"refId\":\"Xkf+USBleCxwfdeuVjSGRgoJulrHlXaQ4xJ4VMgr74c=\"  F
        #                           ,\"nonce\":\"O65vCqFfLUSHaHpvCOHLqw==\"                      F
        #                           ,\"feTraceId\":\"64783313-c5ae-4694-8021-001f4962dbd7\"      F
        #                      }"
        #                    }
        #                    &bx-umidtoken=defaultFY2_load_failed with timeout@@https://detail.tmall.com/item.htm@@1754705354068   baxiaCommon.js 待确认
        #                    &x-pipu2=default_not_fun        baxiaCommon.js 待确认
        #                    &bx-ua=fast-load


        # https://h5api.m.taobao.com/h5/mtop.taobao.pcdetail.data.get/1.0/?jsv=2.7.4&appKey=12574478&t=1754752610541&sign=d003d3812d548b27307e793a742f682a&api=mtop.taobao.pcdetail.data.get&v=1.0&isSec=0&ecode=0&timeout=10000&jsonpIncPrefix=pcdetail&ttid=2022%40taobao_litepc_9.17.0&AntiFlood=true&AntiCreep=true&type=jsonp&dataType=jsonp&callback=mtopjsonppcdetail3&data=%7B%22id%22%3A%22929334932968%22%2C%22detail_v%22%3A%223.3.2%22%2C%22mi_id%22%3A%220000Rlgl7DoezFxQUoaT0sSU5EgFWfGkB571zkSW_0dWGvs%22%2C%22exParams%22%3A%22%7B%5C%22detail_redpacket_pop%5C%22%3A%5C%22true%5C%22%2C%5C%22id%5C%22%3A%5C%22929334932968%5C%22%2C%5C%22ns%5C%22%3A%5C%221%5C%22%2C%5C%22priceTId%5C%22%3A%5C%222147837617547522422333994e1277%5C%22%2C%5C%22query%5C%22%3A%5C%22%E7%94%B5%E8%A7%86%5C%22%2C%5C%22skuId%5C%22%3A%5C%225839863324630%5C%22%2C%5C%22spm%5C%22%3A%5C%22a21n57.1.hoverItem.2%5C%22%2C%5C%22utparam%5C%22%3A%5C%22%7B%5C%5C%5C%22aplus_abtest%5C%5C%5C%22%3A%5C%5C%5C%22340d08405d6fe23138fea0fcee806acf%5C%5C%5C%22%7D%5C%22%2C%5C%22xxc%5C%22%3A%5C%22ad_ztc%5C%22%2C%5C%22queryParams%5C%22%3A%5C%22detail_redpacket_pop%3Dtrue%26id%3D929334932968%26ns%3D1%26priceTId%3D2147837617547522422333994e1277%26query%3D%25E7%2594%25B5%25E8%25A7%2586%26skuId%3D5839863324630%26spm%3Da21n57.1.hoverItem.2%26utparam%3D%257B%2522aplus_abtest%2522%253A%2522340d08405d6fe23138fea0fcee806acf%2522%257D%26xxc%3Dad_ztc%5C%22%2C%5C%22domain%5C%22%3A%5C%22https%3A%2F%2Fitem.taobao.com%5C%22%2C%5C%22path_name%5C%22%3A%5C%22%2Fitem.htm%5C%22%2C%5C%22pcSource%5C%22%3A%5C%22pcTaobaoMain%5C%22%2C%5C%22refId%5C%22%3A%5C%22O3B0OT4bw7LJqVRi9oMabI89%2FWlOhv%2B0uKznoVMLVRk%3D%5C%22%2C%5C%22nonce%5C%22%3A%5C%22Y6k20iTv2RZQiEOnzfnZng%3D%3D%5C%22%2C%5C%22feTraceId%5C%22%3A%5C%22a1393729-4b1c-40a1-ae2d-d69336a7c124%5C%22%7D%22%7D
        #         # https://h5api.m.taobao.com/h5/mtop.taobao.pcdetail.data.get/1.0/
        #         ?jsv=2.7.4&appKey=12574478&t=1754752610541
        #         &sign=d003d3812d548b27307e793a742f682a&api=mtop.taobao.pcdetail.data.get&v=1.0&isSec=0&ecode=0&timeout=10000&jsonpIncPrefix=pcdetail&ttid=2022%40taobao_litepc_9.17.0&AntiFlood=true&AntiCreep=true&type=jsonp&dataType=jsonp&callback=mtopjsonppcdetail3&data=%7B%22id%22%3A%22929334932968%22%2C%22detail_v%22%3A%223.3.2%22%2C%22mi_id%22%3A%220000Rlgl7DoezFxQUoaT0sSU5EgFWfGkB571zkSW_0dWGvs%22%2C%22exParams%22%3A%22%7B%5C%22detail_redpacket_pop%5C%22%3A%5C%22true%5C%22%2C%5C%22id%5C%22%3A%5C%22929334932968%5C%22%2C%5C%22ns%5C%22%3A%5C%221%5C%22%2C%5C%22priceTId%5C%22%3A%5C%222147837617547522422333994e1277%5C%22%2C%5C%22query%5C%22%3A%5C%22%E7%94%B5%E8%A7%86%5C%22%2C%5C%22skuId%5C%22%3A%5C%225839863324630%5C%22%2C%5C%22spm%5C%22%3A%5C%22a21n57.1.hoverItem.2%5C%22%2C%5C%22utparam%5C%22%3A%5C%22%7B%5C%5C%5C%22aplus_abtest%5C%5C%5C%22%3A%5C%5C%5C%22340d08405d6fe23138fea0fcee806acf%5C%5C%5C%22%7D%5C%22%2C%5C%22xxc%5C%22%3A%5C%22ad_ztc%5C%22%2C%5C%22queryParams%5C%22%3A%5C%22detail_redpacket_pop%3Dtrue%26id%3D929334932968%26ns%3D1%26priceTId%3D2147837617547522422333994e1277%26query%3D%25E7%2594%25B5%25E8%25A7%2586%26skuId%3D5839863324630%26spm%3Da21n57.1.hoverItem.2%26utparam%3D%257B%2522aplus_abtest%2522%253A%2522340d08405d6fe23138fea0fcee806acf%2522%257D%26xxc%3Dad_ztc%5C%22%2C%5C%22domain%5C%22%3A%5C%22https%3A%2F%2Fitem.taobao.com%5C%22%2C%5C%22path_name%5C%22%3A%5C%22%2Fitem.htm%5C%22%2C%5C%22pcSource%5C%22%3A%5C%22pcTaobaoMain%5C%22%2C%5C%22refId%5C%22%3A%5C%22O3B0OT4bw7LJqVRi9oMabI89%2FWlOhv%2B0uKznoVMLVRk%3D%5C%22%2C%5C%22nonce%5C%22%3A%5C%22Y6k20iTv2RZQiEOnzfnZng%3D%3D%5C%22%2C%5C%22feTraceId%5C%22%3A%5C%22a1393729-4b1c-40a1-ae2d-d69336a7c124%5C%22%7D%22%7D

        # ad17675de2fdafa03978ec14f044b059
    def taobaoApi0809(self):
        # https://detail.tmall.com/item.htm?id=891426830722&ltk2=1754669175987t72suv6xkhmb70y1kx30m&spm=a21bo.jianhua%2Fa.201876.d2.64d42a89JLlOqv&utparam=%7B%22item_ctr%22%3A0.012033%2C%22x_object_type%22%3A%22p4p_item%22%2C%22item_price%22%3A%2235.02%22%2C%22item_cvr%22%3A0.015806%2C%22pc_scene%22%3A%2220001%22%2C%22aplus_abtest%22%3A%22494b17b967b0e942e5a21d8d74ed97ba%22%2C%22tpp_buckets%22%3A%2230986%23449124%230_30986%23520373%2357062_30986%23521580%2357267%22%2C%22ab_info%22%3A%2230986%23449124%230_30986%23520373%2357062_30986%23521580%2357267%22%2C%22abid%22%3A%22520373_521580%22%2C%22pc_pvid%22%3A%2272e64092-b1cf-4cd3-a731-808c402e759e%22%2C%22mix_group%22%3A%22%22%2C%22item_ecpm%22%3A0.00373%2C%22x_object_id%22%3A891426830722%7D&xxc=ad_ct
        # https://detail.tmall.com/item.htm
        # ?id=891426830722
        # &ltk2=1754669175987t72suv6xkhmb70y1kx30m
        # &spm=a21bo.jianhua%2Fa.201876.d2.64d42a89JLlOqv
        # &utparam=%7B%22item_ctr%22%3A0.012033%2C%22x_object_type%22%3A%22p4p_item%22%2C%22item_price%22%3A%2235.02%22%2C%22item_cvr%22%3A0.015806%2C%22pc_scene%22%3A%2220001%22%2C%22aplus_abtest%22%3A%22494b17b967b0e942e5a21d8d74ed97ba%22%2C%22tpp_buckets%22%3A%2230986%23449124%230_30986%23520373%2357062_30986%23521580%2357267%22%2C%22ab_info%22%3A%2230986%23449124%230_30986%23520373%2357062_30986%23521580%2357267%22%2C%22abid%22%3A%22520373_521580%22%2C%22pc_pvid%22%3A%2272e64092-b1cf-4cd3-a731-808c402e759e%22%2C%22mix_group%22%3A%22%22%2C%22item_ecpm%22%3A0.00373%2C%22x_object_id%22%3A891426830722%7D
        # &xxc=ad_ct
        utparam = '%7B%22item_ctr%22%3A0.012033%2C%22x_object_type%22%3A%22p4p_item%22%2C%22item_price%22%3A%2235.02%22%2C%22item_cvr%22%3A0.015806%2C%22pc_scene%22%3A%2220001%22%2C%22aplus_abtest%22%3A%22494b17b967b0e942e5a21d8d74ed97ba%22%2C%22tpp_buckets%22%3A%2230986%23449124%230_30986%23520373%2357062_30986%23521580%2357267%22%2C%22ab_info%22%3A%2230986%23449124%230_30986%23520373%2357062_30986%23521580%2357267%22%2C%22abid%22%3A%22520373_521580%22%2C%22pc_pvid%22%3A%2272e64092-b1cf-4cd3-a731-808c402e759e%22%2C%22mix_group%22%3A%22%22%2C%22item_ecpm%22%3A0.00373%2C%22x_object_id%22%3A891426830722%7D'
        print(f'utparam: {self.unquote_str(utparam)}')
        # utparam: {
        #   "item_ctr":0.012033,
        #   "x_object_type":"p4p_item",
        #   "item_price":"35.02",
        #   "item_cvr":0.015806,
        #   "pc_scene":"20001",
        #   "aplus_abtest":"494b17b967b0e942e5a21d8d74ed97ba",
        #   "tpp_buckets":"30986#449124#0_30986#520373#57062_30986#521580#57267",
        #   "ab_info":"30986#449124#0_30986#520373#57062_30986#521580#57267",
        #   "abid":"520373_521580",
        #   "pc_pvid":"72e64092-b1cf-4cd3-a731-808c402e759e",
        #   "mix_group":"",
        #   "item_ecpm":0.00373,
        #   "x_object_id":891426830722
        # }

        # https://h5api.m.tmall.com/h5/mtop.taobao.pcdetail.data.get/1.0/?jsv=2.7.4&appKey=12574478&t=1754705354067&sign=9ccae504a69e8e7e5786bfc6da4b3197&api=mtop.taobao.pcdetail.data.get&v=1.0&isSec=0&ecode=0&timeout=10000&jsonpIncPrefix=pcdetail&ttid=2022%40taobao_litepc_9.17.0&AntiFlood=true&AntiCreep=true&type=jsonp&dataType=jsonp&callback=mtopjsonppcdetail4&data=%7B%22id%22%3A%22891426830722%22%2C%22detail_v%22%3A%223.3.2%22%2C%22exParams%22%3A%22%7B%5C%22id%5C%22%3A%5C%22891426830722%5C%22%2C%5C%22skuId%5C%22%3A%5C%225737637236744%5C%22%2C%5C%22spm%5C%22%3A%5C%22a21bo.jianhua%2Fa.201876.d2.64d42a89JLlOqv%5C%22%2C%5C%22utparam%5C%22%3A%5C%22%7B%5C%5C%5C%22item_ctr%5C%5C%5C%22%3A0.012033%2C%5C%5C%5C%22x_object_type%5C%5C%5C%22%3A%5C%5C%5C%22p4p_item%5C%5C%5C%22%2C%5C%5C%5C%22item_price%5C%5C%5C%22%3A%5C%5C%5C%2235.02%5C%5C%5C%22%2C%5C%5C%5C%22item_cvr%5C%5C%5C%22%3A0.015806%2C%5C%5C%5C%22pc_scene%5C%5C%5C%22%3A%5C%5C%5C%2220001%5C%5C%5C%22%2C%5C%5C%5C%22aplus_abtest%5C%5C%5C%22%3A%5C%5C%5C%22494b17b967b0e942e5a21d8d74ed97ba%5C%5C%5C%22%2C%5C%5C%5C%22tpp_buckets%5C%5C%5C%22%3A%5C%5C%5C%2230986%23449124%230_30986%23520373%2357062_30986%23521580%2357267%5C%5C%5C%22%2C%5C%5C%5C%22ab_info%5C%5C%5C%22%3A%5C%5C%5C%2230986%23449124%230_30986%23520373%2357062_30986%23521580%2357267%5C%5C%5C%22%2C%5C%5C%5C%22abid%5C%5C%5C%22%3A%5C%5C%5C%22520373_521580%5C%5C%5C%22%2C%5C%5C%5C%22pc_pvid%5C%5C%5C%22%3A%5C%5C%5C%2272e64092-b1cf-4cd3-a731-808c402e759e%5C%5C%5C%22%2C%5C%5C%5C%22mix_group%5C%5C%5C%22%3A%5C%5C%5C%22%5C%5C%5C%22%2C%5C%5C%5C%22item_ecpm%5C%5C%5C%22%3A0.00373%2C%5C%5C%5C%22x_object_id%5C%5C%5C%22%3A891426830722%7D%5C%22%2C%5C%22xxc%5C%22%3A%5C%22ad_ct%5C%22%2C%5C%22queryParams%5C%22%3A%5C%22id%3D891426830722%26ltk2%3D1754669175987t72suv6xkhmb70y1kx30m%26skuId%3D5737637236744%26spm%3Da21bo.jianhua%252Fa.201876.d2.64d42a89JLlOqv%26utparam%3D%257B%2522item_ctr%2522%253A0.012033%252C%2522x_object_type%2522%253A%2522p4p_item%2522%252C%2522item_price%2522%253A%252235.02%2522%252C%2522item_cvr%2522%253A0.015806%252C%2522pc_scene%2522%253A%252220001%2522%252C%2522aplus_abtest%2522%253A%2522494b17b967b0e942e5a21d8d74ed97ba%2522%252C%2522tpp_buckets%2522%253A%252230986%2523449124%25230_30986%2523520373%252357062_30986%2523521580%252357267%2522%252C%2522ab_info%2522%253A%252230986%2523449124%25230_30986%2523520373%252357062_30986%2523521580%252357267%2522%252C%2522abid%2522%253A%2522520373_521580%2522%252C%2522pc_pvid%2522%253A%252272e64092-b1cf-4cd3-a731-808c402e759e%2522%252C%2522mix_group%2522%253A%2522%2522%252C%2522item_ecpm%2522%253A0.00373%252C%2522x_object_id%2522%253A891426830722%257D%26xxc%3Dad_ct%5C%22%2C%5C%22domain%5C%22%3A%5C%22https%3A%2F%2Fdetail.tmall.com%5C%22%2C%5C%22path_name%5C%22%3A%5C%22%2Fitem.htm%5C%22%2C%5C%22pcSource%5C%22%3A%5C%22pcTaobaoMain%5C%22%2C%5C%22refId%5C%22%3A%5C%22Xkf%2BUSBleCxwfdeuVjSGRgoJulrHlXaQ4xJ4VMgr74c%3D%5C%22%2C%5C%22nonce%5C%22%3A%5C%22O65vCqFfLUSHaHpvCOHLqw%3D%3D%5C%22%2C%5C%22feTraceId%5C%22%3A%5C%2264783313-c5ae-4694-8021-001f4962dbd7%5C%22%7D%22%7D&bx-umidtoken=defaultFY2_load_failed%20with%20timeout%40%40https%3A%2F%2Fdetail.tmall.com%2Fitem.htm%40%401754705354068&x-pipu2=default_not_fun&bx-ua=fast-load
        # https://h5api.m.tmall.com/h5/mtop.taobao.pcdetail.data.get/1.0/
        # ?jsv=2.7.4
        # &appKey=12574478
        # &t=1754705354067
        # &sign=9ccae504a69e8e7e5786bfc6da4b3197
        # &api=mtop.taobao.pcdetail.data.get
        # &v=1.0
        # &isSec=0
        # &ecode=0
        # &timeout=10000
        # &jsonpIncPrefix=pcdetail
        # &ttid=2022%40taobao_litepc_9.17.0
        print(f'ttid={self.unquote_str("2022%40taobao_litepc_9.17.0")}')
        # &AntiFlood=true
        # &AntiCreep=true
        # &type=jsonp
        # &dataType=jsonp
        # &callback=mtopjsonppcdetail4
        # &data=%7B%22id%22%3A%22891426830722%22%2C%22detail_v%22%3A%223.3.2%22%2C%22exParams%22%3A%22%7B%5C%22id%5C%22%3A%5C%22891426830722%5C%22%2C%5C%22skuId%5C%22%3A%5C%225737637236744%5C%22%2C%5C%22spm%5C%22%3A%5C%22a21bo.jianhua%2Fa.201876.d2.64d42a89JLlOqv%5C%22%2C%5C%22utparam%5C%22%3A%5C%22%7B%5C%5C%5C%22item_ctr%5C%5C%5C%22%3A0.012033%2C%5C%5C%5C%22x_object_type%5C%5C%5C%22%3A%5C%5C%5C%22p4p_item%5C%5C%5C%22%2C%5C%5C%5C%22item_price%5C%5C%5C%22%3A%5C%5C%5C%2235.02%5C%5C%5C%22%2C%5C%5C%5C%22item_cvr%5C%5C%5C%22%3A0.015806%2C%5C%5C%5C%22pc_scene%5C%5C%5C%22%3A%5C%5C%5C%2220001%5C%5C%5C%22%2C%5C%5C%5C%22aplus_abtest%5C%5C%5C%22%3A%5C%5C%5C%22494b17b967b0e942e5a21d8d74ed97ba%5C%5C%5C%22%2C%5C%5C%5C%22tpp_buckets%5C%5C%5C%22%3A%5C%5C%5C%2230986%23449124%230_30986%23520373%2357062_30986%23521580%2357267%5C%5C%5C%22%2C%5C%5C%5C%22ab_info%5C%5C%5C%22%3A%5C%5C%5C%2230986%23449124%230_30986%23520373%2357062_30986%23521580%2357267%5C%5C%5C%22%2C%5C%5C%5C%22abid%5C%5C%5C%22%3A%5C%5C%5C%22520373_521580%5C%5C%5C%22%2C%5C%5C%5C%22pc_pvid%5C%5C%5C%22%3A%5C%5C%5C%2272e64092-b1cf-4cd3-a731-808c402e759e%5C%5C%5C%22%2C%5C%5C%5C%22mix_group%5C%5C%5C%22%3A%5C%5C%5C%22%5C%5C%5C%22%2C%5C%5C%5C%22item_ecpm%5C%5C%5C%22%3A0.00373%2C%5C%5C%5C%22x_object_id%5C%5C%5C%22%3A891426830722%7D%5C%22%2C%5C%22xxc%5C%22%3A%5C%22ad_ct%5C%22%2C%5C%22queryParams%5C%22%3A%5C%22id%3D891426830722%26ltk2%3D1754669175987t72suv6xkhmb70y1kx30m%26skuId%3D5737637236744%26spm%3Da21bo.jianhua%252Fa.201876.d2.64d42a89JLlOqv%26utparam%3D%257B%2522item_ctr%2522%253A0.012033%252C%2522x_object_type%2522%253A%2522p4p_item%2522%252C%2522item_price%2522%253A%252235.02%2522%252C%2522item_cvr%2522%253A0.015806%252C%2522pc_scene%2522%253A%252220001%2522%252C%2522aplus_abtest%2522%253A%2522494b17b967b0e942e5a21d8d74ed97ba%2522%252C%2522tpp_buckets%2522%253A%252230986%2523449124%25230_30986%2523520373%252357062_30986%2523521580%252357267%2522%252C%2522ab_info%2522%253A%252230986%2523449124%25230_30986%2523520373%252357062_30986%2523521580%252357267%2522%252C%2522abid%2522%253A%2522520373_521580%2522%252C%2522pc_pvid%2522%253A%252272e64092-b1cf-4cd3-a731-808c402e759e%2522%252C%2522mix_group%2522%253A%2522%2522%252C%2522item_ecpm%2522%253A0.00373%252C%2522x_object_id%2522%253A891426830722%257D%26xxc%3Dad_ct%5C%22%2C%5C%22domain%5C%22%3A%5C%22https%3A%2F%2Fdetail.tmall.com%5C%22%2C%5C%22path_name%5C%22%3A%5C%22%2Fitem.htm%5C%22%2C%5C%22pcSource%5C%22%3A%5C%22pcTaobaoMain%5C%22%2C%5C%22refId%5C%22%3A%5C%22Xkf%2BUSBleCxwfdeuVjSGRgoJulrHlXaQ4xJ4VMgr74c%3D%5C%22%2C%5C%22nonce%5C%22%3A%5C%22O65vCqFfLUSHaHpvCOHLqw%3D%3D%5C%22%2C%5C%22feTraceId%5C%22%3A%5C%2264783313-c5ae-4694-8021-001f4962dbd7%5C%22%7D%22%7D
        # data={
        #       "id":"891426830722",
        #       "detail_v":"3.3.2",
        #       "exParams":"{
        #           \"id\":\"891426830722\",
        #           \"skuId\":\"5737637236744\",
        #           \"spm\":\"a21bo.jianhua/a.201876.d2.64d42a89JLlOqv\",
        #           \"utparam\":\"{
        #               \\\"item_ctr\\\":0.012033
        #               \\\"x_object_type\\\":\\\"p4p_item\\\",
        #               \\\"item_price\\\":\\\"35.02\\\",
        #               \\\"item_cvr\\\":0.015806,
        #               \\\"pc_scene\\\":\\\"20001\\\",
        #               \\\"aplus_abtest\\\":\\\"494b17b967b0e942e5a21d8d74ed97ba\\\",
        #               \\\"tpp_buckets\\\":\\\"30986#449124#0_30986#520373#57062_30986#521580#57267\\\",
        #               \\\"ab_info\\\":\\\"30986#449124#0_30986#520373#57062_30986#521580#57267\\\",
        #               \\\"abid\\\":\\\"520373_521580\\\",
        #               \\\"pc_pvid\\\":\\\"72e64092-b1cf-4cd3-a731-808c402e759e\\\",
        #               \\\"mix_group\\\":\\\"\\\",
        #               \\\"item_ecpm\\\":0.00373,
        #               \\\"x_object_id\\\":891426830722
        #           }\",
        #           \"xxc\":\"ad_ct\",
        #           \"queryParams\":\"
        #               id=891426830722
        #               &ltk2=1754669175987t72suv6xkhmb70y1kx30m
        #               &skuId=5737637236744
        #               &spm=a21bo.jianhua%2Fa.201876.d2.64d42a89JLlOqv
        #               &utparam=%7B%22item_ctr%22%3A0.012033%2C%22x_object_type%22%3A%22p4p_item%22%2C%22item_price%22%3A%2235.02%22%2C%22item_cvr%22%3A0.015806%2C%22pc_scene%22%3A%2220001%22%2C%22aplus_abtest%22%3A%22494b17b967b0e942e5a21d8d74ed97ba%22%2C%22tpp_buckets%22%3A%2230986%23449124%230_30986%23520373%2357062_30986%23521580%2357267%22%2C%22ab_info%22%3A%2230986%23449124%230_30986%23520373%2357062_30986%23521580%2357267%22%2C%22abid%22%3A%22520373_521580%22%2C%22pc_pvid%22%3A%2272e64092-b1cf-4cd3-a731-808c402e759e%22%2C%22mix_group%22%3A%22%22%2C%22item_ecpm%22%3A0.00373%2C%22x_object_id%22%3A891426830722%7D
        #               &xxc=ad_ct\",
        #           \"domain\":\"https://detail.tmall.com\",
        #           \"path_name\":\"/item.htm\",
        #           \"pcSource\":\"pcTaobaoMain\",
        #           \"refId\":\"Xkf+USBleCxwfdeuVjSGRgoJulrHlXaQ4xJ4VMgr74c=\",
        #           \"nonce\":\"O65vCqFfLUSHaHpvCOHLqw==\",
        #           \"feTraceId\":\"64783313-c5ae-4694-8021-001f4962dbd7\"
        #           }"
        #        }

        data = '%7B%22id%22%3A%22891426830722%22%2C%22detail_v%22%3A%223.3.2%22%2C%22exParams%22%3A%22%7B%5C%22id%5C%22%3A%5C%22891426830722%5C%22%2C%5C%22skuId%5C%22%3A%5C%225737637236744%5C%22%2C%5C%22spm%5C%22%3A%5C%22a21bo.jianhua%2Fa.201876.d2.64d42a89JLlOqv%5C%22%2C%5C%22utparam%5C%22%3A%5C%22%7B%5C%5C%5C%22item_ctr%5C%5C%5C%22%3A0.012033%2C%5C%5C%5C%22x_object_type%5C%5C%5C%22%3A%5C%5C%5C%22p4p_item%5C%5C%5C%22%2C%5C%5C%5C%22item_price%5C%5C%5C%22%3A%5C%5C%5C%2235.02%5C%5C%5C%22%2C%5C%5C%5C%22item_cvr%5C%5C%5C%22%3A0.015806%2C%5C%5C%5C%22pc_scene%5C%5C%5C%22%3A%5C%5C%5C%2220001%5C%5C%5C%22%2C%5C%5C%5C%22aplus_abtest%5C%5C%5C%22%3A%5C%5C%5C%22494b17b967b0e942e5a21d8d74ed97ba%5C%5C%5C%22%2C%5C%5C%5C%22tpp_buckets%5C%5C%5C%22%3A%5C%5C%5C%2230986%23449124%230_30986%23520373%2357062_30986%23521580%2357267%5C%5C%5C%22%2C%5C%5C%5C%22ab_info%5C%5C%5C%22%3A%5C%5C%5C%2230986%23449124%230_30986%23520373%2357062_30986%23521580%2357267%5C%5C%5C%22%2C%5C%5C%5C%22abid%5C%5C%5C%22%3A%5C%5C%5C%22520373_521580%5C%5C%5C%22%2C%5C%5C%5C%22pc_pvid%5C%5C%5C%22%3A%5C%5C%5C%2272e64092-b1cf-4cd3-a731-808c402e759e%5C%5C%5C%22%2C%5C%5C%5C%22mix_group%5C%5C%5C%22%3A%5C%5C%5C%22%5C%5C%5C%22%2C%5C%5C%5C%22item_ecpm%5C%5C%5C%22%3A0.00373%2C%5C%5C%5C%22x_object_id%5C%5C%5C%22%3A891426830722%7D%5C%22%2C%5C%22xxc%5C%22%3A%5C%22ad_ct%5C%22%2C%5C%22queryParams%5C%22%3A%5C%22id%3D891426830722%26ltk2%3D1754669175987t72suv6xkhmb70y1kx30m%26skuId%3D5737637236744%26spm%3Da21bo.jianhua%252Fa.201876.d2.64d42a89JLlOqv%26utparam%3D%257B%2522item_ctr%2522%253A0.012033%252C%2522x_object_type%2522%253A%2522p4p_item%2522%252C%2522item_price%2522%253A%252235.02%2522%252C%2522item_cvr%2522%253A0.015806%252C%2522pc_scene%2522%253A%252220001%2522%252C%2522aplus_abtest%2522%253A%2522494b17b967b0e942e5a21d8d74ed97ba%2522%252C%2522tpp_buckets%2522%253A%252230986%2523449124%25230_30986%2523520373%252357062_30986%2523521580%252357267%2522%252C%2522ab_info%2522%253A%252230986%2523449124%25230_30986%2523520373%252357062_30986%2523521580%252357267%2522%252C%2522abid%2522%253A%2522520373_521580%2522%252C%2522pc_pvid%2522%253A%252272e64092-b1cf-4cd3-a731-808c402e759e%2522%252C%2522mix_group%2522%253A%2522%2522%252C%2522item_ecpm%2522%253A0.00373%252C%2522x_object_id%2522%253A891426830722%257D%26xxc%3Dad_ct%5C%22%2C%5C%22domain%5C%22%3A%5C%22https%3A%2F%2Fdetail.tmall.com%5C%22%2C%5C%22path_name%5C%22%3A%5C%22%2Fitem.htm%5C%22%2C%5C%22pcSource%5C%22%3A%5C%22pcTaobaoMain%5C%22%2C%5C%22refId%5C%22%3A%5C%22Xkf%2BUSBleCxwfdeuVjSGRgoJulrHlXaQ4xJ4VMgr74c%3D%5C%22%2C%5C%22nonce%5C%22%3A%5C%22O65vCqFfLUSHaHpvCOHLqw%3D%3D%5C%22%2C%5C%22feTraceId%5C%22%3A%5C%2264783313-c5ae-4694-8021-001f4962dbd7%5C%22%7D%22%7D'
        print(f'data={self.unquote_str(data)}')
        # &bx-umidtoken=defaultFY2_load_failed%20with%20timeout%40%40https%3A%2F%2Fdetail.tmall.com%2Fitem.htm%40%401754705354068
        print(
            f'bx-umidtoken={self.unquote_str("defaultFY2_load_failed%20with%20timeout%40%40https%3A%2F%2Fdetail.tmall.com%2Fitem.htm%40%401754705354068")}')
        # &x-pipu2=default_not_fun
        # &bx-ua=fast-load


if __name__ == '__main__':
    asc = activaeShopCrawl('')
    asc.taobalProductList()
