# crack-tongji-captcha

 识别同济新验证码

## 算法简介

1. 用opencv的findContours找到各个字母

2. 切出各个字母并放正

3. 与样本集逐个对比

## 自动填充脚本

在violentmonkey中添加[自动识别同济验证码](https://greasyfork.org/zh-CN/scripts/415244-%E8%87%AA%E5%8A%A8%E8%AF%86%E5%88%AB%E5%90%8C%E6%B5%8E%E9%AA%8C%E8%AF%81%E7%A0%81)为用户脚本。添加方法请参考[greasy-fork首页](https://greasyfork.org/zh-CN)。