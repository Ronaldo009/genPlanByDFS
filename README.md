项目的目的与之前利用遗传算法拼接Part是一样的，都是寻找满足顾客要求的方案。
该项目利用了回溯算法，成功率达到81%，寻找成功的方案绝大部分时间均可在2秒以内。不成功的都是因为在规定时间内没有寻找到一条合适的方案。
改进方法：双向搜索。从前往后寻找的同时从后往前寻找。缩短了搜索时间，增加了在规定时间内寻找到最优方案的机率。
# genPlanByDFS By 24/7 2017.
