// ==UserScript==
// @name        自动识别同济验证码
// @namespace   Violentmonkey Scripts
// @match       https://ids.tongji.edu.cn:8443/nidp/app/login
// @grant       GM.xmlHttpRequest
// @version     1.0
// @author      melonedo
// @description 11/1/2020, 7:14:05 PM
// ==/UserScript==
captcha_elem = document.forms["IDPLogin"]["Txtidcode"];
captcha_image = document.forms["IDPLogin"]["codeImg"];
captcha_image.onload = () => {
  GM.xmlHttpRequest({
    method: "POST",
    url: "http://172.81.215.215/pi/crack",
    data: JSON.stringify({ data_url: captcha_image.src }),
    onload: (resp) => {
      captcha_elem.value = JSON.parse(resp.responseText).ans;
    },
  });
};
