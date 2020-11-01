# crack-tongji-captcha

 识别同济新验证码

## 算法简介

1. 用opencv的findContours找到各个字母

2. 切出各个字母并放正

3. 与样本集逐个对比

## 自动填充

在violentmonkey中添加auto-captcha.js作为用户脚本。添加方法请参考[greasy-fork](https://greasyfork.org/zh-CN)。