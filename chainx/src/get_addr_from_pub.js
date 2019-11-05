const Chainx = require('chainx.js').default;
const { Account } = require('chainx.js');
const publickey= process.argv[2];

(async () => {
  // const account = chainx.account.from(seed);
  // console.log(account.address);
  // console.log(account.publicKey);
  // console.log(account.privateKey);
  const address_output = Account.encodeAddress(publickey); // 从公钥生成地址
  console.log('address_output: ', address_output);
  // 构造交易参数（同步）
  process.exit();
  // chainx.provider.websocket.close();
})();

