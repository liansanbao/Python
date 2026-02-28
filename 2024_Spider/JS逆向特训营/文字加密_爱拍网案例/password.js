// 定义常量
const CryptoJS = require('crypto-js') // 相当python中的import语法

var l = CryptoJS.encrypt(h);
var b = l.replace(/\s|\n|\r\n/g, "+");

var passwrod = CryptoJS.MD5('mm').toString()

console.log(passwrod)


