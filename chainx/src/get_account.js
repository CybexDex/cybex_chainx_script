const Chainx = require('chainx.js').default;
const { Account } = require('chainx.js');
const publickey= process.argv[2];
const address = process.argv[3];

(async () => {
  // const account = chainx.account.from(seed);
  // console.log(account.address);
  // console.log(account.publicKey);
  // console.log(account.privateKey);
  const address_output = Account.encodeAddress(publickey); // 从公钥生成地址
  console.log('address_output: ', address_output);
  const publickey_output = Account.decodeAddress(address); // 从地址获取生成公钥
  console.log('publickey_output: ', publickey_output);
  // 构造交易参数（同步）
  process.exit();
  // chainx.provider.websocket.close();
})();

