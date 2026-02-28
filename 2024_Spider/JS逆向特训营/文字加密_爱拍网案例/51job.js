const crypto = require('crypto-js');

function generateSecureSign(params, secretKey) {
  // 1. 参数按键名排序
  const sortedParams = Object.keys(params)
    .sort()
    .reduce((acc, key) => {
      acc[key] = params[key];
      return acc;
    }, {});

  // 2. 序列化为稳定JSON字符串
  const paramString = JSON.stringify(sortedParams);

  // 3. 生成随机数与同步时间戳
  const nonce = crypto.lib.WordArray.random(16).toString(); // 128位随机数
  const timestamp = Date.now(); // 从服务端同步

  // 4. 构建签名基础字符串
  const rawString = `${paramString}|${nonce}|${timestamp}|${secretKey}`;

  // 5. 使用 HMAC-SHA256 计算签名
  return crypto.HmacSHA256(rawString, secretKey).toString();
}

var poa = "{'api_key': '51job','timestamp': 1745844618, 'intentionId': 40560723, 'pageSize': 50, 'pageNum': 2, 'type': 'recommend', 'source': 1, 'requestId': '4606b087c9025626054220e7e898b362', 'needApply': 'true', 'scene': 'main_rec'}"
var par = '/wuhan-dhxjs/coB2RSM144UmUEZQ1nVDc.html'

console.log(generateSecureSign(par, 'abfc8f9dcf8c3f3d8aa294ac5f2cf2cc7767e5592590f39c3f503271dd68562b'))
