const Chainx = require('chainx.js').default;
const from = process.argv[2]
const to = process.argv[3]
const amount = process.argv[4]
const privkey = process.argv[5]
const memo = process.argv[6]
console.log(from);
console.log(to);
console.log(privkey);
console.log(memo);

(async () => {
  // 目前只支持 websocket 链接
  const chainx = new Chainx('wss://w1.chainx.org/ws');

  // 等待异步的初始化
  await chainx.isRpcReady();

  // 构造交易参数（同步）

  const extrinsic = chainx.asset.transfer(to, 'PCX', amount, memo);

  // 查看 method 哈希
  console.log('Function: ', extrinsic.method.toHex());
  
  // 签名并发送交易，0x0000000000000000000000000000000000000000000000000000000000000000 是用于签名的私钥
  await extrinsic.signAndSend(privkey, (error, response) => {
    if (error) {
      console.log(error);
      process.exit(-1);
    } else if (response.status === 'Finalized') {
      if (response.result === 'ExtrinsicSuccess') {
        console.log('交易成功');
        process.exit(0);
      }
    }
  });
})();

