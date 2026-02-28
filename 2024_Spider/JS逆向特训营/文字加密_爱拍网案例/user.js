window = global;
const JSEncrypt = require('jsencrypt')

// 1.创建对象
var m = new JSEncrypt();

//2.设置公钥
var o = "-----BEGIN PUBLIC KEY-----MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDs/S8+O5yCcwypPNAQDmcVGY5UEa/iMNDFKcoovLFayhy3Jm/S1L8oYC85Rx8YwWOaQ9Zak0i6eb1AM2JDN7T9+pYb7mf4fzpE4BbXnAc3OqPwxEsNAsAsMKg6GhVxLu2/bfhrKOZ9Arvf6m/n0bGpfdJhIdom6iWh5iG4c+z5vwIDAQAB-----END PUBLIC KEY-----";
m.setPublicKey(o);
var l = m.encrypt('18217623705');
var b = l.replace(/\s|\n|\r\n/g, "+");

//3.加密
console.log(b);


// OdYVTS7/eWXvb23amrtuaNHoqIEDyYDleNCaod8vrpp0kykHIX2sTzdAOVdqBItHky+uR1gpbCn8bvuP/H3n21uGwrb5za7Y61gzvq1s+jdVUyEzV2HyIM8EM0aN6z5AOxrvbQFcttH/gTa6Oe4Hcm8GRl0aZkt3KKEg3YQBk+A=
// qvSbwveC+6ZH0QYuaoTBFGlIQgnIr2wx/YWQx5YbwBv8yFtp8sf4ssrxoAlnffMqs4ZNTAfJdhHaRigJyv5lCitsYld0FXHuNF2lYAwJsSRbjBp0DP7aDHHpuLZchmedlM5/ewse2fd0v2bKRp/xwzgirWCHes3iE+sufehlcf8=